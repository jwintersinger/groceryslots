import requests
import dateutil.parser
import datetime
import time
import argparse
import sys
import re

DOMAINS = {
  'superstore': 'www.realcanadiansuperstore.ca',
  'loblaws': 'www.loblaws.ca',
}
SITE_BANNERS = {
  'superstore': 'superstore',
  'loblaws': 'loblaw',
}

# From https://stackoverflow.com/a/15586020
class Reprinter:
  def __init__(self):
    self.text = ''

  def moveup(self, lines):
    for _ in range(lines):
      sys.stdout.write("\x1b[A")

  def reprint(self, text):
    # Clear previous text by overwritig non-spaces with spaces
    self.moveup(self.text.count("\n"))
    sys.stdout.write(re.sub(r"[^\s]", " ", self.text))

    # Print new text
    lines = min(self.text.count("\n"), text.count("\n"))
    self.moveup(lines)
    sys.stdout.write(text)
    self.text = text

def make_header(site):
  headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en' ,
    'Site-Banner': SITE_BANNERS[site],
    'Content-Type': 'application/json;charset=utf-8',
    'Connection': 'keep-alive',
   }
  return headers

def fetch(site, location, cookies):
  r = requests.get('https://%s/api/pickup-locations/%s/time-slots' % (DOMAINS[site], location), cookies=cookies, headers=make_header(site))
  return r.json()

def get_cookies(site):
  r = requests.get('https://%s' % DOMAINS[site], headers=make_header(site))
  return r.cookies

def parse_time(T, offset):
  T = dateutil.parser.parse(T, fuzzy=True)
  # Account for timezone difference
  T -= datetime.timedelta(hours=offset)
  return T

def check_slots(site, location, cookies, tzoffset=4):
  response = fetch(site, location, cookies)
  avail = [(
    parse_time(S['startTime'], tzoffset),
    parse_time(S['endTime'], tzoffset),
  ) for S in response['timeSlots'] if S['available']]
  
  return [S[0] for S in avail]

def main():
  parser = argparse.ArgumentParser(
    description='Query PC-umbrella grocery store (Loblaws, Superstore, etc.) for open pick-up slots',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  # To find the location:
  # 1. Go to https://www.loblaws.ca/store-locator
  # 2. Choose a location and click the "Location Details" link
  # 3. Find the integer ID at the end of the URL (e.g., https://www.loblaws.ca/store-locator/details/1007)
  parser.add_argument('--location', type=int, default=1007,
    help='Integer ID of PC-umbrella (Loblaws, Superstore, etc.) grocery store')
  parser.add_argument('--delay', type=float, default=60,
    help='Delay ins econds between checks')
  parser.add_argument('--tzoffset', type=int, default=4,
    help='Timezone offset in hours. Default seems to work for both Toronto and Calgary')
  parser.add_argument('--announce', action='store_true',
    help='Announce new open slots via Chromecast device (including Google home')
  parser.add_argument('--site', choices=('loblaws', 'superstore'), default='loblaws',
    help='Type of PC-umbrella grocery store')
  args = parser.parse_args()

  init_cookies = get_cookies(args.site)
  rep = Reprinter()
  prev_first_slot = None

  while True:
    slots = check_slots(args.site, args.location, init_cookies, args.tzoffset)
    if args.announce and len(slots) > 0 and slots[0] != prev_first_slot:
      import saytext
      saytime = slots[0].strftime('The next available grocery pickup slot is on %A, %B %d at %I %p.')
      saytext.say(saytime)
      prev_first_slot = slots[0]

    now = datetime.datetime.now()
    out = ['last_checked = %s' % now.strftime('%H:%M:%S')]
    out.append('next_check = %s' % (now + datetime.timedelta(seconds=args.delay)).strftime('%H:%M:%S'))
    for S in slots:
      out.append('avail = %s' % S.strftime('%Y-%m-%d %H:%M'))
    rep.reprint('\n'.join(out) + '\n')
    time.sleep(args.delay)

if __name__ == '__main__':
  main()
