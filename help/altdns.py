#!/usr/bin/env python
import socket

dns = (
	'irc.hardchats.net',
	'irc.ngr.bz',
	'irc.wepump.in',
	'irc.autist.life'
)

servers = set([i[4][0] for i in socket.getaddrinfo('irc.supernets.org', 6667)])
for hostname in dns:
	try:
		if socket.gethostbyname(hostname) in servers:
			print('GOOD\t' + hostname)
		else:
			print('BAD \t' + hostname)
	except:
		print('BAD \t' + hostname)