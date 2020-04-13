Grocery Slots
=============
This program will periodically check Loblaws for open grocery pick-up slots (by default, every 60 seconds), printing open slots to the terminal. The program can also announce via any Chromecast-compatible device (including Google Home) when a new spot opens.

Requirements
------------
* Python 3

Usage
-----
1. Install necessary Python libraries.

    pip3 install --user requests dateutil

2. Find your Loblaws location ID.
    a. Go to https://www.loblaws.ca/store-locator
    b. Choose a location and click the "Location Details" link
    c. Find the integer ID at the end of the URL (e.g., `1007` from https://www.loblaws.ca/store-locator/details/1007)

3. Run the main script.

    python3 loblaws.py --location 1007

Getting audible announcements
-----------------------------
You can configure the script to announce new slots via any Chromecast device (including Google Home).

1. Install additional libraries.

    pip3 install --user pychromecast gtts

2. In a separate terminal, start a web server to serve the text-to-speech audio
   file to your Chromecast device. By default, this audio file will be stored
   as `/tmp/out.mp3`, but you can control this via the `AUDIO_PATH` variable in
   `saytext.py`.

    cd /tmp
    python3 -m http.server

3. Change the `HTTP_IP` variable in `saytext.py` to correspond to the IP of
   your local machine that will serve the audio file to your Chromecast.

4. Run the main script with `--announce`.

    python3 loblaws.py --location 1007 --announce