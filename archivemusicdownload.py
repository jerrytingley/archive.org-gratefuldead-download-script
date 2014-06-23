import os
import sys
import json
from urllib import urlretrieve
from urllib2 import urlopen

# Hopefully this is the final version, with only minor tweaks from now on
# I originally wrote this with compact-ness in mind but I rewrote it to
# hopefully make it more readable.

def sanitize(filename):
	return filename.replace('->', '-]').replace('/', ' - ')

def get_m3u(url):
	url = 'https://archive.org/download/{0}/{0}_vbr.m3u'.format(url)
	data = urlopen(url).read()
	return data.split('\n')[0:-1]

def get_metadata(url):
	metadata = json.loads(urlopen('https://archive.org/metadata/'+url).read())
	server = metadata['server']
	dir_ = metadata['dir']
	creator = metadata['metadata']['creator']
	date = metadata['metadata']['date']
	venue = metadata['metadata']['venue']
	new_metadata = {
		'download_base' : 'https://{0}{1}/'.format(server, dir_),
		'local_download_dir' : '{0} - {1} - {2}'.format(creator, date, venue),
	}
	for file_data in metadata['files']:
		if file_data['format'] == 'VBR MP3':
			filename = file_data['name']
			title = file_data['title']
			track = file_data['track']
			new_metadata[filename] = {
				'title'             : title,
				'download_filename' : filename
			}
			try:
				new_metadata[filename]['local_filename'] = "{0}. {1}".format(track, title)
			except KeyError:
				new_metadata[filename]['local_filename'] = title
			new_metadata[filename]['local_filename'] = sanitize(new_metadata[filename]['local_filename'])
	return new_metadata

def download(url):
	print "[..] Downloading "+url
	print "[..] Retrieving metadata..."
	metadata = get_metadata(url)
	local_download_dir = metadata['local_download_dir']
	links = get_m3u(url)
	print "[..] Checking for existing download..."
	resume = False
	downloaded_files = []
	if (os.path.isdir(local_download_dir)):
		print "[..] Found existing directory..."
		resume = True
		downloaded_files = os.listdir(os.path.dirname(os.path.realpath(__file__))+'/'+local_download_dir)
		downloaded_files.sort()
		downloaded_files = downloaded_files[0:-1]
	else:
		print "[..] Creating directory..."
		os.mkdir(local_download_dir)
	print "[..] Downloading files..."
	file_count = len(links)
	for i, link in enumerate(links, 1):
		link = link.split('/')[-1]
		link_metadata = metadata[link]
		archive_download_url = metadata['download_base']+link
		local_filename = link_metadata['local_filename']
		if resume and local_filename in downloaded_files: continue
		local_download_name = '{0}/{0}'.format(local_download_dir, local_filename)
		print "[..] Downloading {0} ({1}/{2})...".format(local_filename, i, file_count)
		urlretrieve(archive_download_url, local_download_name)

def main():
	if len(sys.argv) < 2:
		print "usage: python archivemusicdownload.py <archive.org ID>"
	else:
		try:
			url = sys.argv[1]
			download(url)
		except KeyboardInterrupt:
			print "[!!] CTRL-C, Quitting..."
main()
