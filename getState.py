#!/usr/bin/python3
import json

# --- Variables -----------------------------------------------------------------------

null = None
false = False

# --- Class / Def ---------------------------------------------------------------------

# --- Main ----------------------------------------------------------------------------

result = subprocess.getoutput('/usr/bin/curl -s 0 http://127.0.0.1:3000/api/v1/getstate')
#result = '{"status":"stop","position":0,"albumart":"/albumart","uri":"http://streamer.radio.co/s6a349b3a2/listen","trackType":"webradio","seek":668,"samplerate":"","bitdepth":"","channels":0,"random":null,"repeat":null,"repeatSingle":false,"consume":false,"volume":29,"disableVolumeControl":false,"mute":false,"stream":"webradio","updatedb":false,"volatile":false,"service":"webradio"}'
jsonResult = json.loads(result)


print()
print('    ', 'Status:                ', jsonResult['status'])
print('    ', 'Volume:                ', jsonResult['volume'])
print('    ', 'Mute:                  ', jsonResult['mute'])
print('    ', 'DisableVolumeControl:  ', jsonResult['disableVolumeControl'])
print()
for key, value in jsonResult.items():
    print('  ', key, ":", value)
print()



