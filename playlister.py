import sys
import os
import glob
from mutagen.mp3 import MP3
import time

folder = sys.argv[1]
file_names = glob.glob(folder+'*.mp3')
tracklist = open('Playlist.txt', 'w')
total_time = 0.0

for name in file_names:
	artist_song = name.split('/')[1].split('.')[0].split('-')
	new_name = artist_song[1].strip() + ' - ' + artist_song[0].strip() + '.mp3'
	song = MP3(name).info.length
	total_time += song
	song = time.strftime('%M:%S', time.gmtime(song))
	os.rename(name, new_name)
	tracklist.write(song + ' - ' + new_name[:-4] + '\n')

tracklist.write(time.strftime('%H:%M:%S', time.gmtime(total_time)))