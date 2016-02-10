#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import glob
import json
import discogs_client
from mutagen.mp3 import MP3
import time

disco_check = False
if os.path.exists('conf.json') :
	with open('conf.json') as file :
		conf = json.load(file)
		disco_check = True
		user = conf["user"]
		token = conf['user_token']
else :
	token = raw_input("T'as pas de conf.json avec ton token discogs dedans, donne-le moi : ")
	if len(token) > 10:
		disco_check = True
		print "Ok cool, cimer. Patience."
	else:
		print "C'est pas un token de discogs ce que tu m'as filé..."

d = discogs_client.Client(user, user_token=token)

folder = sys.argv[1]
file_names = glob.glob(folder+'*.mp3')
tracklist = open('Playlist.txt', 'w')
playtracks = open('Trackids.txt', 'w')
total_time = 0.0

for name in file_names:
	artist = name.split('/')[1].split('.')[0].split('-')[0].strip()
	song = name.split('/')[1].split('.')[0].split('-')[1].strip()

	new_name = song + ' - ' + artist + '.mp3'
	song_length = MP3(name).info.length
	total_time += song_length
	song_length = time.strftime('%M:%S', time.gmtime(song_length))
	os.rename(name, new_name)
	tracklist.write(song_length + ' - ' + new_name[:-4] + '\n')

	if disco_check == True:
		results = d.search(song, type='release')
		# results = d.search("Codine", type='release')
		trackline = ''
		track_ids = []
		for i in range(25):
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
			trackline = track[0] + ' / ' + track[1] + ' / ' + track[2] + ' / ' + track[3] + ' / ' + track[4]
			if track[5] != '':
				trackline += ' // ' + track[5].replace('\n', ' ').replace('  ', ' ')
			trackline += '\n'
		else:
			trackline = "rien / trouvé / pour / ce / track\n"

		playtracks.write(trackline)

tracklist.write(time.strftime('%H:%M:%S', time.gmtime(total_time)))



