#!/usr/bin/env python
# hateserv irc bot - developed by acidvegas in python (https://git.acid.vegas/hateserv)

import http.client
import json
import re

def between(source, start, stop):
	data = re.compile(start + '(.*?)' + stop, re.IGNORECASE|re.MULTILINE).search(source)
	return data.group(1) if data else False

def geoip(ip: str):
	api = geturl('api.ipapi.is', '?q='+ip)
	data = json.loads(api)
	LOCATION = '{0}, {1}, {2}'.format(data['location']['city'], data['location']['state'], data['location']['country_code'])
	ASN = 'AS{0} {1}'.format(data['asn']['asn'], data['asn']['descr'])
	RIR = data['rir']
	return {'location': LOCATION, 'asn': ASN, 'rir': RIR}

def geturl(url, endpoint, headers={}):
	conn = http.client.HTTPSConnection(url, timeout=15)
	conn.request('GET', endpoint, headers=headers)
	response = conn.getresponse().read()
	conn.close()
	return response

def google(query):
	service = build('customsearch', 'v1', developerKey=google_api_key, cache_discovery=False).cse()
	results = service.list(q=query, cx=google_cse_id, num=10).execute()
	return results['items'] if results else False

def github(option, query):
	if option == 'search':
		data = json.loads(geturl('api.github.com', '/search/repositories?q='+query, headers={'Accept':'application/vnd.github.v3+json','User-Agent':'HateServ/1.0'}))
		return data['items'] if data['items'] else False
	elif option == 'repo':
		return json.loads(geturl('api.github.com', '/repos/'+query, headers={'Accept':'application/vnd.github.v3+json','User-Agent':'HateServ/1.0'}))
	elif option == 'user':
		return json.loads(geturl('api.github.com', '/users/'+query, headers={'Accept':'application/vnd.github.v3+json','User-Agent':'HateServ/1.0'}))

def imdb(query):
	''' https://www.omdbapi.com '''
	year = query.split()[-1]
	query = query.replace(' ','%20')
	search = 'i' if query.startswith('tt') else 't'
	if search == 't' and len(year) == 4 and year.isdigit():
		endpoint = f'/?{search}={query[:-5]}&y={year}&apikey={api_key}'
	else:
		endpoint = f'/?{search}={query}&apikey={api_key}'
	conn = http.client.HTTPSConnection('omdbapi.com', timeout=15)
	conn.request('GET', endpoint, headers={'Accept':'application/json'})
	response = json.loads(conn.getresponse().read())
	conn.close()
	return response if response['Response'] == 'True' else False

def reddit(option, subreddit, id=None):
	if option == 'post':
		data = json.loads(geturl('reddit.com', f'/r/{subreddit}/comments/{id}.json', headers={'Accept':'application/json','User-Agent':'HateServ/1.0'}))
		return data[0]['data']['children'][0]['data'] if 'error' not in data else False
	elif option == 'subreddit':
		data = json.loads(geturl('reddit.com', f'/r/{subreddit}.json?limit=20', headers={'Accept':'application/json','User-Agent':'HateServ/1.0'}))
		posts = [item['data'] for item in data['data']['children'] if not item['data']['stickied']]
		return posts if posts else None

def youtube(option, query, api_key):
	if option == 'video':
		api = httplib.get_json(f'https://www.googleapis.com/youtube/v3/videos?key={config.api.google_api_key}&part=snippet,statistics&id={id}')
		if api['items']:
			api                 = api['items'][0]
			data                = {}
			data['channel']     = api['snippet']['channelTitle']
			data['description'] = ' '.join(api['snippet']['description'].split())
			data['dislikes']    = api['statistics']['dislikeCount']
			data['likes']       = api['statistics']['likeCount']
			data['title']       = api['snippet']['title']
			data['views']       = api['statistics']['viewCount']
			return data
		else:
			return False
	elif option == 'search':
		service = build('youtube', 'v3', developerKey=api_key).search()
		results = service.list(part='id', type='video', q=query, maxResults=10).execute()
		return results['items'] if results else False

def twitter(data):
#	auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
#	auth.set_access_token(twitter_access_token, twitter_access_secret)
#	api = tweepy.API(auth)
#	api.update_status(data)
	pass

def unreal():
	pass

def anope():
	pass


'''
elif args[0] == '.imdb' and len(args) >= 2:
                        query = ' '.join(args[1:])
                        api   = imdb.search(query, config.api.omdbapi_key)
                        if api:
                            Commands.sendmsg(chan, '{0} {1} {2} {3}'.format(color('Title  :', white), api['Title'], api['Year'], color(api['Rated'], grey)))
                            Commands.sendmsg(chan, '{0} {1}{2}'.format(color('Link   :', white), underline, color('https://imdb.com/title/' +  api['imdbID'], light_blue)))
                            Commands.sendmsg(chan, '{0} {1}'.format(color('Genre  :', white), api['Genre']))
                            if api['imdbRating'] == 'N/A':
                                Commands.sendmsg(chan, '{0} {1} N/A'.format(color('Rating :', white), color('★★★★★★★★★★', grey)))
                            else:
                                Commands.sendmsg(chan, '{0} {1}{2} {3}'.format(color('Rating :', white), color('★'*round(float(api['imdbRating'])), yellow), color('★'*(10-round(float(api['imdbRating']))), grey), a
pi['imdbRating']))
                            Commands.sendmsg(chan, '{0} {1}'.format(color('Plot   :', white), api['Plot']))
                        else:
                            Commands.error(chan, 'no results found')
'''