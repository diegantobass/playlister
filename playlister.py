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

mp3_folder = "mp3_files/"

if '/' in sys.argv[0]:
	script_folder = '/'.join(sys.argv[0].split('/')[:-1])
else:
	script_folder = './'
	
if os.path.exists(mp3_folder):
	file_names = glob.glob(mp3_folder+'*.mp3')
else:
    os.makedirs(mp3_folder)
    file_names = []

lista = open(sys.argv[1], 'r')
for link in lista:
	splitted_line = link.split(' : ')
	if (mp3_folder + splitted_line[0] + ".mp3") not in file_names:
		dl_command = 'youtube-dl -x --audio-format mp3 -o "' + mp3_folder + splitted_line[0] + '.%(ext)s" ' + splitted_line[1]
		os.system(dl_command)

disco_check = False
mb_check = False
if sys.argv[-1] == "--check":
	mb_check = True
	disco_check = True
	if os.path.exists(os.path.join(script_folder, 'conf.json')):
		with open(os.path.join(script_folder, 'conf.json')) as file :
			conf = json.load(file)
			user = conf["user"]
			token = conf['user_token']
	else :
		user = raw_input("No conf file provided. Please enter your Discogs app username : ")
		token = raw_input("Enter your Discogs user token : ")

	d = discogs_client.Client(user, user_token=token)
	test_discogs_client = d.search("Moonage Daydream", type='release')
	try:
		test_moonage = test_discogs_client[0]
	except discogs_client.exceptions.HTTPError:
		disco_check = False
		print "Information provided for the Discogs API weren't correct. Continuing without it."
	mb = musicbrainzngs.set_useragent("Voix de Garage", "0.1")
	try:
		test_litter = musicbrainzngs.search_artists(query="The Litter", limit=2)
	except:
		mb_check = False
		print "Music Brainz API unavailable at the moment."


file_names = glob.glob(mp3_folder+'*.mp3')
if len(file_names) < 1:
	print "There are no mp3 files in your folder."
	sys.exit(0)
playtracks_disco = open(mp3_folder + 'Trackids_discogs.txt', 'w')
playtracks_mb = open(mp3_folder + 'Trackids_mb.txt', 'w')
tracklist = open(mp3_folder + 'Playlist.txt', 'w')	
total_time = 0.0

for name in file_names:
	song = name.split('/')[-1].split('.')[0].split('-')[0].strip()
	artist = name.split('/')[-1].split('.')[0].split('-')[1].strip()

	song_length = MP3(name).info.length
	total_time += song_length
	song_length = time.strftime('%M:%S', time.gmtime(song_length))
	tracklist.write(song_length + ' - ' + name[10:-4] + '\n')

	if disco_check == True:
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

			playtracks_disco.write(trackline_disco.encode('utf-8'))

	if mb_check == True:
		trackline_mb = ''
		recordings = musicbrainzngs.search_recordings(recording=song)
		release_list = []
		for recording in recordings["recording-list"]:
			if recording["artist-credit-phrase"] == artist:
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
			playtracks_mb.write(trackline_mb.encode('utf-8'))

tracklist.write(time.strftime('%H:%M:%S', time.gmtime(total_time)))


