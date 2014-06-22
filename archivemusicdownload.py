import os
import re
import sys
import json
from urllib import urlretrieve
from urllib2 import urlopen

sanitize    = lambda filename: filename.replace('/', '_')
nt_sanitize = lambda filename: re.sub('[<>:\"/\|\?*]', ' ', filename)

def get_metadata(url):
	# Parse and reformat metadata
	metadata = json.loads(urlopen('https://archive.org/metadata/'+url).read())
	new_metadata = {
		'download_base' : 'https://'+metadata['server']+metadata['dir']+'/', # py2 % formatting is werid with slashes
		'local_download_dir' : "%s - %s - %s" % (metadata['metadata']['creator'], metadata['metadata']['date'], metadata['metadata']['venue']),
		'files' : [],
	}
	for file_data in metadata['files']:
		if file_data['format'] == 'VBR MP3':
			new_file = {
				'title' : file_data['title'],
				'download_filename' : file_data['name'],
			}
			try:
				new_file['local_filename'] = "%s. %s" % (file_data['track'], file_data['title'])
			except KeyError:
				new_file['local_filename'] = file_data['title']
			new_file['local_filename'] = sanitize(new_file['local_filename'])
			new_metadata['files'].append(new_file)
	return new_metadata

def download(url):
	is_windows = os.name == 'nt'
	print "[..] Downloading "+url
	print "[..] Retrieving metadata..."
	metadata = get_metadata(url)
	local_download_dir = metadata['local_download_dir']
	if is_windows: local_download_dir = nt_sanitize(local_download_dir)
	print "[..] Checking for existing download..."
	resume = False
	if (os.path.isdir(local_download_dir)):
		# Ghetto file resume, might break with certain shows but yolo
		# TODO:
		# If the dl gets interupted, it's rare for the last file to be 100% dl'ed,
		# so I'm having the script re-download the last downloaded file
		print "[..] Found existing directory..."
		resume = True
		downloaded_files = os.listdir(os.path.dirname(os.path.realpath(__file__))+'/'+local_download_dir)
		downloaded_files.sort()
		downloaded_files = downloaded_files
		print downloaded_files
	else:
		print "[..] Creating directory..."
		os.mkdir(local_download_dir)
	print "[..] Downloading files..."
	file_count = len(metadata['files'])
	for i, file_data in enumerate(metadata['files']):
		local_filename = "%s/%s" % (local_download_dir, file_data['local_filename'])
		if resume and file_data['local_filename'] in downloaded_files: continue
		if is_windows: local_filename = nt_sanitize(local_filename)
		print "[..] Downloading %s (%i/%i)..." % (file_data['local_filename'], i+1, file_count)
		urlretrieve(metadata['download_base']+file_data['download_filename'], local_filename)

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
