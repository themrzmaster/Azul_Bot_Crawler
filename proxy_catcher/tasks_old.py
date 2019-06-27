from __future__ import absolute_import, unicode_literals
import requests
import time
import datetime
import urllib2, socket
from selenium.webdriver import FirefoxProfile
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup as bs
from selenium.common.exceptions import TimeoutException
from .models import Proxy_Connection
from celery import task
import os
import logging
import subprocess


logger = logging.getLogger(__name__)

def _connection():
	o = Options()
	fp = FirefoxProfile()
	o.add_argument('-private')
	fp.set_preference("network.proxy.type", 0)
	#fp.set_preference("general.useragent.override","iPhone")
	fp.update_preferences()
	return Firefox(firefox_profile=fp, firefox_options=o)
	


def resetXvfb():
	proc = subprocess.call('killall firefox', shell=True)
	proc = subprocess.call('killall Xvfb', shell=True)
	sp = subprocess.call('nohup Xvfb :99 -screen 0 375x667x8 &', shell=True)
	#xvfb = subprocess.Popen(['Xvfb', ':99'])
	time.sleep(2)
	os.environ["DISPLAY"]=":99"
	logger.info('Xvfb reset!')


def getlist(p_list):

	try:
		browser = _connection()
		base_url = "http://proxydb.net/?protocol=http&anonlvl=1&min_uptime=75&max_response_time=5&country=BR"
		t = time.time()
		browser.set_page_load_timeout(10)
		browser.get(base_url)
	except TimeoutException:
		browser.execute_script("window.stop();")

	except WebDriverException as e:
		resetXvfb()
		try:
			browser = _connection()
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
		proxy_handler = urllib2.ProxyHandler({'http': proxy})
		opener = urllib2.build_opener(proxy_handler)
		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		urllib2.install_opener(opener)
		req=urllib2.Request('http://voeazul.com.br')
		sock=urllib2.urlopen(req, timeout=7)
	except urllib2.HTTPError, e:
		logger.info('Error code: ', e.code)
		return e.code
	except urllib2.URLError, e:
		print "more than 7 sec"
		return 0
	except socket.timeout, e:
   		print "more than 7 sec"
   		return 0
   	return 1	

@task()
def proxy_catch():
	logger.info('Starting Proxy Catcher! :)')
	p_list = []
	#socket.setdefaulttimeout(180)
	getlist(p_list)
	print p_list

	for item in p_list:
		if check_proxy(item) == 1:
			#ok, can add to db
			ip_p, port_p = item.split(":")
			now_date = datetime.datetime.now()
			logger.info('adding proxy! ' + ip_p + ':' + str(port_p))
			p_obj = Proxy_Connection.objects.create(date=now_date,ip=ip_p,port=port_p)
			p_obj.salvar()
			print p_obj


