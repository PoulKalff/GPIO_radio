#!/usr/bin/env python3

# Copyright (c) 2025 Luc Van Braekel
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import requests
import sys
import argparse
from time import sleep, time
from datetime import datetime
import urllib.parse

def get_icy_metadata(url, timeout=10):
    """Retrieve ICY metadata from a stream URL."""
    headers = {'Icy-MetaData': '1'}  # Request metadata
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=timeout)
        response.raise_for_status()  # Check for HTTP errors

        # Validate icy-metaint header
        metaint = response.headers.get('icy-metaint')
        if not metaint:
            print("Error: No icy-metaint header found in response")
            return None
        try:
            metaint = int(metaint)
            if metaint <= 0:
                raise ValueError
        except ValueError:
            print("Error: Invalid icy-metaint value")
            return None

        bytes_until_metadata = metaint
        metadata = None
        buffer = b''

        for chunk in response.iter_content(chunk_size=1024):
            if not chunk:  # Handle empty chunk (stream termination)
                print("Warning: Empty chunk received, stream may have ended")
                break

            buffer += chunk
            while len(buffer) >= bytes_until_metadata:
                # Extract audio data
                audio_data = buffer[:bytes_until_metadata]
                buffer = buffer[bytes_until_metadata:]

                # Read metadata length byte
                if len(buffer) < 1:
                    print("Error: Buffer too short to read metadata length")
                    break
                meta_length = buffer[0] * 16  # ICY metadata length is byte * 16
                buffer = buffer[1:]  # Remove the length byte

                # Read metadata
                if len(buffer) < meta_length:
                    print("Error: Buffer too short for metadata (need {meta_length}, got {len(buffer)})")
                    break
                metadata = buffer[:meta_length].decode('utf-8', errors='ignore')
                buffer = buffer[meta_length:]

                # Reset bytes until next metadata
                bytes_until_metadata = metaint

                # Parse metadata
                if metadata and "StreamTitle" in metadata:
                    try:
                        title = metadata.split("StreamTitle='")[1].split("';")[0]
                        return urllib.parse.unquote(title)
                    except IndexError:
                        print("Warning: Malformed metadata: {metadata}")
                        continue
                else:
                    print("Warning: No StreamTitle in metadata: {metadata}")

                # Reset metadata for next iteration
                metadata = None

        # If we exit the loop without metadata, return None
        print("Warning: No valid metadata found in stream")
        return None

    except requests.RequestException as e:
        print("Error: Failed to connect or read stream: {e}")
        return None






stream_url = "http://streamer.radio.co/s6a349b3a2/listen"
metadata = get_icy_metadata(stream_url)
print(len(metadata))
print(metadata)
