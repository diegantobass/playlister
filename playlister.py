#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import glob
import json
import discogs_client
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

lista = open(sys.argv[1], 'r')
for link in lista:
	splitted_line = link.split(' : ')
	if (mp3_folder + splitted_line[0] + ".mp3") not in file_names:
		dl_command = "youtube-dl -x --audio-format mp3 -o '" + mp3_folder + splitted_line[0] + ".%(ext)s' " + splitted_line[1]
		os.system(dl_command)

disco_check = False
if sys.argv[-1] == "--check":
	if os.path.exists(os.path.join(script_folder, 'conf.json')):
		with open(os.path.join(script_folder, 'conf.json')) as file :
			conf = json.load(file)
			disco_check = True
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

file_names = glob.glob(mp3_folder+'*.mp3')
if len(file_names) < 1:
	print "There are no mp3 files in your folder."
	sys.exit(0)
tracklist = open(mp3_folder + 'Playlist.txt', 'w')
if disco_check == True:
	playtracks = open(mp3_folder + 'Trackids.txt', 'w')
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
		trackline = ''
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
					trackline = (artist, album, year, country, label, note)
					track_ids.append(trackline)
			if len(track_ids) > 0:
				sortedtrackids = sorted(track_ids, key=lambda tup: int(tup[2]), reverse=True)
				track = sortedtrackids.pop()
				while(int(track[2]) < 1900):
					track = sortedtrackids.pop()
				trackline = song + ' / ' + track[0].replace('/', '&') + ' / ' + track[1].replace('/', '+') + ' / ' + track[2] + ' / ' + track[3].replace('/', '&') + ' / ' + track[4].replace('/', '&')
				if track[5] != '':
					trackline += ' // ' + track[5].replace('/', ' ').replace('  ', ' ')
				trackline += '\n'

			playtracks.write(trackline.encode('utf-8'))

tracklist.write(time.strftime('%H:%M:%S', time.gmtime(total_time)))