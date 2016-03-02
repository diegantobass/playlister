#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import glob
import json
import discogs_client
import musicbrainzngs
from mutagen.mp3 import MP3
import time
import argparse

# Function needed to check the validity/existence of the list of link specified as arg
def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist" % arg)
    else:
        return open(arg, 'r')

# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--disco", "--check-discogs", help='checks for tracks information on discogs.com', action="store_true", dest="disco_check", default=False)
parser.add_argument("-mb", "--mbrainz", "--check-musicbrainz", help='checks for tracks information on musicbrainz.com', action="store_true", dest="mb_check", default=False)
parser.add_argument("-l", "-liste", dest="liste", help="optional list of youtube links to be downloaded and added to the mp3_folder", type=lambda x: is_valid_file(parser, x))
parser.add_argument("-f", "-folder", dest="folder", help='the mp3 folder where the tracks are stored')
args = parser.parse_args()

# Folder from which the script is launched
if '/' in sys.argv[0]:
	script_folder = '/'.join(sys.argv[0].split('/')[:-1])
else:
	script_folder = './'

# If no folder for mp3 storage is specified set it to mp3_folder and walk it to find already dled mp3
if not args.folder:
	args.folder = "./mp3_folder"
if not args.folder[-1] == '/':
	args.folder += '/'
if os.path.exists(args.folder):
	file_names = [os.path.basename(x) for x in glob.glob(args.folder + '*.mp3')]
else:
    os.makedirs(args.folder)
    file_names = []

# If a list of links to download is specified, download it and add them to the mp3 folder if not already there
if args.liste:
	for link in args.liste:
		splitted_line = link.split(' : ')
		if (args.folder + splitted_line[0] + ".mp3") not in file_names:
			dl_command = 'youtube-dl -x --audio-format mp3 -o "' + args.folder + splitted_line[0] + '.%(ext)s" ' + splitted_line[1]
			os.system(dl_command)
	file_names = [os.path.basename(x) for x in glob.glob(args.folder + '*.mp3')]

# Connects to the discogs API if specified in args
if args.disco_check:
	id_disco = open(args.folder + 'idiscogs.txt', 'w')
	if os.path.exists(os.path.join(script_folder, 'conf.json')):
		with open(os.path.join(script_folder, 'conf.json')) as file :
			conf = json.load(file)
			user = conf["user"]
			token = conf['user_token']
	else :
		user = raw_input("No conf file provided. Please enter your Discogs app username : ")
		token = raw_input("Enter your Discogs user token : ")

	d = discogs_client.Client(user, user_token=token)
	test_discogs_client = d.search("Moonage Daydream", type='release', limit=2)
	try:
		test_moonage = test_discogs_client[0]
	except discogs_client.exceptions.HTTPError:
		disco_check = False
		print "Information provided for the Discogs API weren't correct. Continuing without it."

# Connects to the music brainz API if specified in args	
if args.mb_check:
	id_mb = open(args.folder + 'idmb.txt', 'w')
	mb = musicbrainzngs.set_useragent("Voix de Garage", "0.1")
	try:
		test_litter = musicbrainzngs.search_artists(query="The Litter", limit=2)
	except:
		mb_check = False
		print "Music Brainz API unavailable at the moment."

# If there are no files in the mp3 folder at this point, the script has nothing to do so it exits with an explicit message
if len(file_names) < 1:
	print "There are no mp3 files in your folder and you didn't give me any to download."
	sys.exit(0)

# Do the stuff
else:
	tracklist = open(args.folder + 'Playlist.txt', 'w')	
	total_time = 0.0

	for name in file_names:
		fullname = os.path.join(args.folder + name)
		song = name.split('.')[0].split('-')[0].strip()
		artist = name.split('.')[0].split('-')[1].strip()

		song_length = MP3(fullname).info.length
		total_time += song_length
		song_length = time.strftime('%M:%S', time.gmtime(song_length))
		tracklist.write(song_length + ' - ' + name + '\n')

		if args.disco_check:
			results = d.search(song, type='release')
			trackline_disco = ''
			track_ids = []
			results_nb = len(results)
			if results_nb > 0:
				if results_nb > 50:
					results_nb = 50
				for i in range(results_nb):
					page = results[i]
					if artist in page.artists[0].name:
						artist = page.artists[0].name
						album = page.title
						year = str(page.year)
						country = page.country
						label = page.labels[0].name
						note = ''
						data = page.data
						for key in data:
							if key == "notes":
								note += data[key].replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')
						trackline_disco = (artist, album, year, country, label, note)
						track_ids.append(trackline_disco)
				if len(track_ids) > 0:
					sortedtrackids = sorted(track_ids, key=lambda tup: int(tup[2]), reverse=True)
					track = sortedtrackids.pop()
					while(int(track[2]) < 1900):
						track = sortedtrackids.pop()
					trackline_disco = song + ' / ' + track[0].replace('/', '&') + ' / ' + track[1].replace('/', '+') + ' / ' + track[2] + ' / ' + track[3].replace('/', '&') + ' / ' + track[4].replace('/', '&')
					if track[5] != '':
						trackline_disco += ' // ' + track[5].replace('/', ' ').replace('  ', ' ')
					trackline_disco += '\n'

				id_disco.write(trackline_disco.encode('utf-8'))

		if args.mb_check:
			trackline_mb = ''
			recordings = musicbrainzngs.search_recordings(recording=song)
			release_list = []
			for recording in recordings["recording-list"]:
				if recording["artist-credit-phrase"] == artist and "release-list" in recording:
					for release in recording["release-list"]:
						if "date" in release.keys():
							release_tuple = (release, release["date"][:4])
							release_list.append(release_tuple)

			sortedreleases = sorted(release_list, key=lambda release_tuple: release_tuple[1])
			if len(sortedreleases) > 0:
				album = sortedreleases[0][0]["title"]
				date = sortedreleases[0][0]["date"][:4]
				country = sortedreleases[0][0]["country"]

				trackline_mb = song + ' / ' + artist + ' / ' + album + ' / ' + date + ' / ' + country + ' / label\n'
				id_mb.write(trackline_mb.encode('utf-8'))

	tracklist.write(time.strftime('%H:%M:%S', time.gmtime(total_time)))


