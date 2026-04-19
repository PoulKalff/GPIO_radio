#!/usr/bin/python3

import urllib.request

url = "http://streamer.radio.co/s6a349b3a2/listen"

def getTitle(stream_url):
    request = urllib.request.Request(stream_url, headers={'Icy-MetaData' : 1})
    response = urllib.request.urlopen(request)
    icy_metaint_header = response.headers.get('icy-metaint')
    if icy_metaint_header is not None:
        metaint = int(icy_metaint_header)
        read_buffer = metaint+255
        content = response.read(read_buffer)
        content_str = ""
        for _byte in content:
            content_str += chr(int(_byte))
        stream_title_pos = content_str.find("StreamTitle=")
        post_title_content = content_str[stream_title_pos+13:]
        semicolon_pos = post_title_content.find(';')
        title = post_title_content[:semicolon_pos-1]
    return title





title = getTitle(url)
print(title)
