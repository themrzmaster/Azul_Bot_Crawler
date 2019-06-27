from __future__ import absolute_import, unicode_literals
import requests
import time
from datetime import datetime, timedelta
import urllib2, socket
from socket import error as SocketError
import errno
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup as bs
from selenium.common.exceptions import TimeoutException
from .models import Proxy_Connection
from airtrick.utils import *
from celery import task
import os
import logging
import subprocess


logger = logging.getLogger(__name__)


def getlist(p_list):
	try:
		browser = normal_connection()
		base_url = "http://proxydb.net/?protocol=http&anonlvl=1&min_uptime=75&max_response_time=5&country=BR"
		t = time.time()
		browser.set_page_load_timeout(10)
		browser.get(base_url)
	except TimeoutException:
		browser.execute_script("window.stop();")

	except WebDriverException as e:
		resetXvfb()
		try:
			browser = normal_connection()
			base_url = "http://proxydb.net/?protocol=http&anonlvl=1&min_uptime=75&max_response_time=5&country=BR"
			t = time.time()
			browser.set_page_load_timeout(10)
			browser.get(base_url)
		except TimeoutException:
			browser.execute_script("window.stop();")	


	base_html = browser.page_source
	soup = bs(base_html, "html.parser")
	soup.prettify()
	table = soup.find('table')
	table_body = table.find('tbody')
	rows = table_body.find_all('tr')

	for row in rows: #each row means a proxy
		item = row.find('td')
		proxy_item = (item.find('a')).text
		#print proxy_item
		p_list.append(proxy_item)

	browser.quit()

def check_proxy(proxy):
	try:
		proxy_handler = urllib2.ProxyHandler({'https': proxy})
		opener = urllib2.build_opener(proxy_handler)
		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		urllib2.install_opener(opener)
		req=urllib2.Request('https://www.voeazul.com.br/')
		sock=urllib2.urlopen(req, timeout=7)
	except urllib2.HTTPError, e:
		logger.info('Error code: ' + str(e.code))
		return e.code
	except urllib2.URLError, e:
		logger.info("more than 7 sec")
		return 0
	except socket.timeout, e:
   		logger.info("more than 7 sec")
   		return 0
   	except SocketError as e:
   		logger.error(e)
   		return 0
   	return 1
   		

@task()
def proxy_catch():
	logger.info('Starting Proxy Catcher! :)')

	logger.info('First check old proxies and mark the bad ones...')
	lista_old_p = getLatestProxy(2)
	for i in lista_old_p:
		if check_proxy(i) != 1:
			ip_p, port_p = i.split(":")
			logger.info(str(ip_p) + " is bad")
			logger.info('Connection timeout, marking proxy as unactive!')
			innactivateProxy(ip_p, port_p)

	p_list = []
	logger.info('Getting fresh ones :)')
	#socket.setdefaulttimeout(180)
	getlist(p_list)
	logger.info(p_list)

	for item in p_list:
		if check_proxy(item) == 1:
			#ok, can add to db
			ip_p, port_p = item.split(":")
			now_date = datetime.now()
			logger.info('adding proxy! ' + ip_p + ':' + str(port_p))
			p_obj = Proxy_Connection.objects.create(date=now_date,ip=ip_p,port=port_p)
			p_obj.salvar()


