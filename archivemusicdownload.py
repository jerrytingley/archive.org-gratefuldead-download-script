import os
import sys
import json
from urllib import urlretrieve
from urllib2 import urlopen

from pprint import pprint as p

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
			new_metadata['files'].append(new_file)
	return new_metadata

def download(url):
	print "[..] Retrieving metadata..."
	metadata = get_metadata(url)
	print "[..] Creating directory..."
	os.mkdir(metadata['local_download_dir'])
	print "[..] Downloading files..."
	file_count = len(metadata['files'])
	for i, file_data in enumerate(metadata['files']):
		local_filename = "%s/%s" % (metadata['local_download_dir'], file_data['local_filename'])
		print "[..] Downloading %s (%i/%i)..." % (file_data['local_filename'], i+1, file_count)
		urlretrieve(metadata['download_base']+file_data['download_filename'], local_filename)

def main():
	if len(sys.argv) < 2:
		print "usage: python archivemusicdownload.py <archive.org ID>"
	else:
		url = sys.argv[1]
		print "[..] Downloading "+url
		download(url)
main()
