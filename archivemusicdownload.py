import os
import sys
import string
import random
import eyed3
from urllib import urlretrieve
from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup

tmp_dir_string = lambda: 'tmp_'+''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(6))

def get_m3u_from_url(url):
	soup = BeautifulSoup(urlopen(url).read())
	m3u_link = soup.find('p', {'class':'content'}).find('a')['href']
	return m3u_link

def rename(tmp_dir_name):
	files = os.listdir(tmp_dir_name)
	info = eyed3.load(tmp_dir_name+'/'+files[0])
	artist = info.tag.artist
	album = info.tag.album
	del info
	for f in files:
		old_filename = '%s/%s' % (tmp_dir_name, f)
		metadata = eyed3.load(old_filename)
		new_title = metadata.tag.title
		new_num = metadata.tag.track_num[0]
		ext = f.split('.')[-1]
		new_filename = '%s/%i. %s.%s' % (tmp_dir_name, new_num, new_title, ext)
		print "[..] Renaming %s to %s" % (old_filename, new_filename)
		os.rename(old_filename, new_filename)
	new_albumname = '%s - %s' % (artist, album)
	print "[..] Renaming %s to %s" % (tmp_dir_name, new_albumname)
	os.rename(tmp_dir_name, new_albumname)
	
def download(m3u_link):
	print "[..] Downloading M3U... "
	html = urlopen(m3u_link).read()
	links = html.split('\n')[0:-1]
	print "[..] Creating temporary directory..."
	tmp_dir_name = tmp_dir_string()
	os.mkdir(tmp_dir_name)
	print "[..] Downloading files..."
	file_count = len(links)
	for i, link in enumerate(links):
		filename = tmp_dir_name+"/"+link.split('/')[-1]
		print "[..] Downloading %s (%i/%i)..." % (filename, i+1, file_count)
		urlretrieve(link, filename)
	print "[..] Renaming files..."
	rename(tmp_dir_name)

def main():
	url = sys.argv[1]
	m3u_link = get_m3u_from_url('https://archive.org/details/'+url)
	print "[..] Downloading "+url
	download(m3u_link)
main()
