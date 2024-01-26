import csv
import io
import json
import urllib.request
import sys
import time

def download_file(url: str, dest_filename: str, chunk_size: int = 1024*1024):
    '''
    Download a file from a given URL in chunks and save to a destination filename.

    :param url: The URL of the file to download
    :param dest_filename: The destination filename to save the downloaded file
    :param chunk_size: Size of chunks to download. Default is set to 1MB.
    '''
    with urllib.request.urlopen(url) as response:
        total_size = int(response.getheader('Content-Length').strip())
        downloaded_size = 0
        with open(dest_filename, 'wb') as out_file:
            while True:
                start_time = time.time()
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                downloaded_size += len(chunk)
                out_file.write(chunk)
                end_time = time.time()
                speed = len(chunk) / (end_time - start_time)
                progress = (downloaded_size / total_size) * 100
                sys.stdout.write(f'\rDownloaded {downloaded_size} of {total_size} bytes ({progress:.2f}%) at {speed/1024:.2f} KB/s\r')
                sys.stdout.flush()
            print()

def get_url(url: str, sent_headers: dict = {}, reader: bool = True):
	'''
	Retrieve a URL with custom headers.
	
	:param url: The URL to retrieve
	:param data: The headers to send
	:param reader: Return the reader object instead of the decoded data
	'''
	req = urllib.request.Request(url, headers=sent_headers)
	if reader:
		return urllib.request.urlopen(req, timeout=10).read().decode()
	else:
		return urllib.request.urlopen(req, timeout=10)
      
def setup_user_agent(user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'):
	'''
	Set up urllib.request user agent.
	
	:param user_agent: The user agent to use
	'''
	handler = urllib.request.HTTPHandler()
	opener = urllib.request.build_opener(handler)
	opener.addheaders = [('User-agent', user_agent)]
	urllib.request.install_opener(opener)


# -------------------------------------------------------------------------------- #

def asn_seach(query: str):
    '''
    Search for an ASN by string.
      
    :param query: The string to search
    '''
    return json.loads(get_url('https://api.bgpview.io/search?query_term='+query))

def cve_search(query: str, limit: str = '25'):
	'''
    Search for a CVE by string.
    
    :param query: The string to search
    :param limit: The number of results to return
    '''
	return json.loads(get_url(f'https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={query}&resultsPerPage={limit}'))

def geoip(ip: str):
	'''
	Get the geolocation of an IP address.
	
	:param ip: The IP address to geolocate
	'''
	return json.loads(get_url('https://api.ipapi.is/?q='+ip))

def github(option: str, query: str):
    '''
    Search for a GitHub repository or user.
    
    :param option: The option to search for (search, repo, user)
    :param query: The query to search
    '''
    header = {'Accept': 'application/vnd.github.v3+json'}
    if option == 'search':
        url = 'https://api.github.com/search/repositories?q=' + query
        data = json.loads(get_url(url, header))  # Changed this line
        return data['items'] if data['items'] else False
    elif option == 'repo':
        url = 'https://api.github.com/repos/' + query
        return json.loads(get_url(url, header))  # And this one
    elif option == 'user':
        url = 'https://api.github.com/users/' + query
        return json.loads(get_url(url, header))  # And this one

def librex(query: str):
	'''
	Search on the SuperNETs running LibreX.
	
	:param query: The query to search
	'''
	return json.loads(get_url(f'https://librex.supernets.org/api.php?q={query}&t=0'))

def reddit(option, subreddit, id=None):
	'''
	Search for a Reddit post or subreddit.
	
	:param option: The option to search for (post, subreddit)
	:param subreddit: The subreddit to search
	:param id: The post ID to search
    '''
	header = {'Accept':'application/json'}
	if option == 'post':
		data = json.loads(get_url('https://reddit.com', f'/r/{subreddit}/comments/{id}.json', header))
		return data[0]['data']['children'][0]['data'] if 'error' not in data else False
	elif option == 'subreddit':
		data = json.loads(get_url('https://reddit.com', f'/r/{subreddit}.json?limit=20', header))
		posts = [item['data'] for item in data['data']['children'] if not item['data']['stickied']]
		return posts if posts else None
	
def exploitdb(query: str):
	'''
	Search for an exploit or shellcode on ExploitDB.
	
	:param query: The query to search
	'''
	exploits = get_url('https://git.supernets.org/mirrors/exploitdb/raw/branch/main/files_exploits.csv')
	shellcodes = get_url('https://git.supernets.org/mirrors/exploitdb/raw/branch/main/files_shellcodes.csv')
	results = []
	for database in (exploits, shellcodes):
		reader = csv.DictReader(io.StringIO(database))
		results += [row for row in reader if query.lower() in row['description'].lower()]
	return results