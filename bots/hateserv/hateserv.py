#!/usr/bin/env python
# hateserv irc bot - developed by acidvegas in python (https://git.acid.vegas/hateserv)

import re
import socket
import ssl
import time
import urllib.request

import commands

# Config
admin             = 'acidvegas!~stillfree@most.dangerous.motherfuck'
server            = 'irc.supernets.org'
channel           = '#dev'
nickname          = '[dev]HateServ'
username          = 'H'
realname          = 'SuperNETs HATE Services'
nickserv_password = 'simps0nsfan22'
operator_password = 'EatMYsh0rts39'

# Colors & Control Characters
bold        = '\x02'
underline   = '\x1F'
reset       = '\x0f'
white       = '00'
black       = '01'
blue        = '02'
green       = '03'
red         = '04'
brown       = '05'
purple      = '06'
orange      = '07'
yellow      = '08'
light_green = '09'
cyan        = '10'
light_cyan  = '11'
light_blue  = '12'
pink        = '13'
grey        = '14'
light_grey  = '15'

def color(msg, foreground, background=None):
    return f'\x03{foreground},{background}{msg}{reset}' if background else f'\x03{foreground}{msg}{reset}'

def debug(data):
	print('{0} | [~] - {1}'.format(time.strftime('%I:%M:%S'), data))

def error(data, reason=None):
	print('{0} | [!] - {1} ({2})'.format(time.strftime('%I:%M:%S'), data, str(reason))) if reason else print('{0} | [!] - {1}'.format(time.strftime('%I:%M:%S'), data))

def irc_error(chan, data, reason=None):
	sendmsg(chan, '[{0}] {1}'.format(color('error', red), data, color(f'({reason})', grey))) if reason else sendmsg(chan, '[{0}] {1}'.format(color('error', red), data))

def raw(msg):
	msg = msg.replace('\r\n',' ')
	sock.send(bytes(msg[:510] + '\r\n', 'utf-8'))

def sendmsg(target, msg):
	raw(f'PRIVMSG {target} :{msg}')

def trim(data, max_length):
	return data[:max_length] + '...' if len(data) > max_length else data

def urlcheck(msg):
	url = re.compile('(?:http[s]?:\/\/|http[s]?:\/\/www.)(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', re.IGNORECASE).findall(msg)
	if url:
		url = url[0]
		try:
			if (check := re.match('^.*?github.com\/([0-9A-Za-z]+\/[0-9A-Za-z]+).*?', url, re.IGNORECASE)):
				data = commands.github('repo', check.group(1))
				if data:
					if not data['description']:
						data['description'] = 'no description available'
					sendmsg(channel, '{0} {1} {2} [{3}:{4}|{5}:{6}|{7}:{8}]'.format(color(' GitHub ', black, grey), data['full_name'], color('('+data['description']+')', grey), color('Stars', purple), data['stargazers_count'], color('Watch', purple), data['watchers'], color('Forks', purple), data['forks']))
			elif (check := re.match('^.*?github.com\/([0-9A-Za-z]+)', url, re.IGNORECASE)):
				data = commands.github('user', check.group(1))
				if data:
					data['bio'] = data['bio'].replace('\r\n','') if data['bio'] else ''
					sendmsg(channel, '{0} {1} {2} {3} [{4}:{5}|{6}:{7}]'.format(color(' GitHub ', black, grey), data['login'], color('('+data['name']+')', grey), data['bio'], color('Repos', purple), data['public_repos'], color('Followers', purple), data['followers']))
			elif (check := re.match('^.*?reddit.com\/r\/(.*?)\/comments\/([0-9A-Za-z]+).*$', url, re.IGNORECASE)):
				data = commands.reddit('post', check.group(1), check.group(2))
				sendmsg(channel, '[{0}] - {1} [{2}/{3}|{4}]'.format(color('reddit', cyan), color(trim(data['title'], 300), white), color('+' + str(data['ups']), green), color('-' + str(data['downs']), red), color(str(data['num_comments']), white)))
			elif (check := re.match('^.*?youtu(be)?\.([a-z])+\/(watch(.*?)(\?|\&)v=)?(.*?)(&(.)*)*$', url, re.IGNORECASE)):
				pass
			else:
				source = urllib.request.urlopen(url, timeout=10)
				title = re.compile(r'<title.*?>(.+?)</title>', re.I | re.M | re.S | re.U).search(source.read().decode('utf-8'))
				if title:
					title = title.group(1).replace('\n',' ')
					if len(title) > 100:
						title = title[:100] + '...'
					type = source.info().get_content_type()
					sendmsg(channel, f'[{type}] {title}')
		except Exception as ex:
			error('failed to get parse url title', ex)

def event_message(chan, nick, ident, msg):
	args = msg.split()
	if not msg.startswith('.'):
		urlcheck(msg)
		if msg == '@hateserv':
			sendmsg(channel, 'hateserv irc bot for supernets - developed by acidvegas in python (https://git.acid.vegas/hateserv)')
		elif msg in ('melp','.melp','melp?','.melp?'):
			sendmsg(chan, '\x01ACTION explodes\x01')
	else:
		if ident == admin:
			if msg == '.massjoin':
				raw('WHO * n%nc')
		if args[0] in ('.g','.s'):
			query   = ' '.join(args[1:])
			results = commands.librex(query)
			if results:
				for item in results:
					sendmsg(chan, '[{0}] {1}'.format(color(str(results.index(item)+1).zfill(2), pink), trim(item['title'], 300)))
					sendmsg(chan, ' '*5 + underline + color(item['link'], light_blue))
			else:
				irc_error(chan, 'no results found')
		elif args[0] == '.cve':
			data = commands.cve_search(' '.join(args[1:]))
			for item in data['vulnerabilities']:
				id = item['cve']['id']
				desc = item['cve']['descriptions'][0]['value']
				sendmsg(chan, '[{0}] {1} - {2}'.format(color(str(data['vulnerabilities'].index(item)+1).zfill(2), pink), color(id, cyan), trim(desc, 300)))
		elif args[0] == '.ip':
			data = commands.geoip(args[1])
			location = '{0}, {1}, {2}'.format(data['location']['city'], data['location']['state'], data['location']['country_code'])
			asn = 'AS{0} ({1})'.format(data['asn']['asn'], data['asn']['descr'])
			sendmsg(chan, '[{0}] {1} under {2} controlled by {3}'.format(color('geoip', light_blue), color(location, yellow), color(asn, cyan), color(data['rir'], pink)))
		elif args[0] == '.gh':
			query = ' '.join(args[1:]).replace(' ','%20')
			results = commands.github('search',query)
			if results:
				for item in results:
					if not item['description']:
						item['description'] = 'no description'
					sendmsg(chan, '[{0}] {1}/{2}{3}{4} {5}'.format(color(str(results.index(item)+1).zfill(2), pink), item['owner']['login'], bold, item['name'], reset, color('('+item['description']+')', grey)))
					sendmsg(chan, ' '*5 + underline + color(item['html_url'], light_blue))
		elif args[0] == '.r' and len(args) == 2:
			query   = args[1]
			results = commands.reddit('subreddit', query)
			if results:
				for item in results:
					sendmsg(chan, '[{0}] {1} [{2}/{3}|{4}]'.format(color(str(results.index(item)+1).zfill(2), pink), trim(item['title'], 300), color('+' + str(item['ups']), green), color('-' + str(item['downs']), red), color(item['num_comments'], white)))
					sendmsg(chan, ' '*5 + underline + color(item['url'], light_blue))
			else:
				irc_error(chan, 'no results found')

while True:
	#try:
		#sock = ssl.wrap_socket(socket.socket())
		sock = socket.socket()
		sock.connect((server, 6667))
		raw(f'USER {username} 0 * :{realname}')
		raw('NICK ' + nickname)
		while True:
			try:
				data = sock.recv(1024).decode('utf-8')
				for line in (line for line in data.split('\r\n') if len(line.split()) >= 2):
					debug(line)
					args = line.split()
					if line.startswith('ERROR :Closing Link:'):
						raise Exception('Connection has closed.')
					elif args[0] == 'PING':
						raw('PONG ' + args[1][1:])
					elif args[1] == '001': #RPL_WELCOME
						raw(f'MODE {nickname} +B')
						raw(f'PRIVMSG NickServ IDENTIFY {nickname} {nickserv_password}')
						raw(f'OPER hates {operator_password}')
						raw('JOIN ' + channel)
						last = 5
					elif args[1] == '354' and len(args) == 5: #RPL_WHOSPCRPL
						nick = args[4]
						if nick not in (nickname,'AI','BLACKHOLE','BotServ','ChanServ','EliManning','fraud','Global','HostServ','IRCCEX','NickServ','OperServ','THEGAME'):
							raw(f'SAJOIN {nick} {channel}')
					elif args[1] == 'JOIN' and len(args) == 3:
						nick = args[0].split('!')[0][1:]
						chan = args[2][1:]
					elif args[1] == 'PRIVMSG' and len(args) >= 4:
						ident  = args[0][1:]
						chan   = args[2]
						nick   = args[0].split('!')[0][1:].lower()
						msg    = ' '.join(args[3:])[1:]
						if chan == channel:
							#try:
								event_message(chan, nick, ident, msg)
							#except Exception as ex:
							#	irc_error(chan, 'unknown error occured', ex)
						elif chan == nickname and ident == admin and msg.startswith('.raw '):
							raw(msg[5:])
			except (UnicodeDecodeError, UnicodeEncodeError):
				pass
	#except Exception as ex:
	#	error('fatal error occured', ex)
	#	sock.close()
	#finally:
	#	time.sleep(15)