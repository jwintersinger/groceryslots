import pychromecast
import gtts
import os
import sys
import argparse

def say(text, volume=1.0):
  audio_path = '/tmp/out.mp3'

  speech = gtts.gTTS(text = text, lang = 'en', slow = False)
  speech.save(audio_path)

  cc = pychromecast.get_chromecasts()
  cast = next(C for C in cc if C.device.friendly_name == 'Living Room speaker')
  cast.wait()
  cast.set_volume(volume)

  mc = cast.media_controller
  mc.play_media('http://192.168.0.15:8000/out.mp3', 'audio/mp3')
  mc.block_until_active()

def main():
  parser = argparse.ArgumentParser(
  description='LOL HI THERE',
  formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument('--volume', type=float, default=0.5)
  parser.add_argument('text')
  args = parser.parse_args()

  say(args.text, args.volume)

if __name__ == '__main__':
  main()
