#!/usr/bin/env python
# supernets namecheap api tool - developed by acidvegas in python (https://git.acid.vegas/supertools)

import re
import requests
import xml.etree.ElementTree as et

# Config
username = 'changeme'
api_key  = 'changeme'
ip_addr  = 'changeme'

def api(cmd, extra=False):
	payload = {
		'ApiKey'   : api_key,
		'ApiUser'  : username,
		'UserName' : username,
		'ClientIP' : ip_addr,
		'Command'  : cmd
	}
	if extra:
		payload.update(extra)
	r = requests.post('https://api.namecheap.com/xml.response', params=payload)
	return r.content

class domains:
	class dns:
		def getHosts():
			data = api('namecheap.domains.dns.getHosts', extra={'TLD': 'supernets','SLD':'org'})
			for child in et.fromstring(data).findall('.//{http://api.namecheap.com/xml.response}host'):
				print(child.attrib)

	def setHosts(type, address):
		payload = {
			'SLD'        : 'supernets',
			'TLD'        : 'org',
			'HostName'   : 'irc',
			'RecordType' : type,
			'Address'    : address,
			'TTL'        : '60'
		}
		data = api('namecheap.domains.dns.setHosts', payload)

class ssl:
	def getInfo(id):
		'''https://www.namecheap.com/support/api/methods/ssl/get-info/'''
		data = api('namecheap.ssl.getInfo', extra={'CertificateID':id})

	def getList():
		'''https://www.namecheap.com/support/api/methods/ssl/get-list/'''
		data = api('namecheap.ssl.getList')

	def activate(id, csr, mail):
		'''https://www.namecheap.com/support/api/methods/ssl/activate/'''
		payload = {
			'CertificateID': id,
			'CSR':csr,
			'AdminEmailAddress':mail
		}
		data = api('namecheap.ssl.activate', payload)

	def parseCSR(csr):
		payload = {
			'csr': csr,
			'CertificateType': 'PositiveSSL'
		}
		data = api('namecheap.ssl.parseCSR', payload)

	def renew(id):
		'''https://www.namecheap.com/support/api/methods/ssl/renew/'''
		payload = {
			'CertificateID':id,
			'SSLType': 'PositiveSSL',
			'years': '1' # or 5
		}
		data = api('namecheap.ssl.renew')
