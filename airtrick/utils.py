from __future__ import absolute_import, unicode_literals
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from django.apps import apps
from datetime import datetime, timedelta
from random import randint
import logging
from time import sleep
import psutil
import random
import unidecode
import os
import time
import subprocess
import django

django.setup()
Proxy_Connection = apps.get_model('proxy_catcher', 'Proxy_Connection')
logger = logging.getLogger(__name__)
mobile_emulation = {"deviceName": "iPhone 6 Plus"}


def between(value, a, b):
    # Find and validate before-part.
    pos_a = value.find(a)
    if pos_a == -1: return ""
    # Find and validate after part.
    pos_b = value.rfind(b)
    if pos_b == -1: return ""
    # Return middle part.
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= pos_b: return ""
    return value[adjusted_pos_a:pos_b]



def checkMem():
	per = float(psutil.virtual_memory()[2])
	if per >= 90.0:
		#proc = subprocess.call("find /tmp -name '*rust_mozprofile*' -exec rm -r {} \;", shell=True)
		#proc = subprocess.call("find /tmp -name '*tmpaddon*' -exec rm -r {} \;", shell=True)
 		logger.info("Memory usage is too high... killing processes and starting over")
 		resetXvfb()

def resetXvfb():
	proc = subprocess.call('pgrep chrome | xargs kill -9', shell=True)
	logger.info('Xvfb reset!')


def innactivateProxy(proxy_ip, proxy_port):
	p = Proxy_Connection.objects.filter(ip=proxy_ip, port=proxy_port)
	for i in p:
		i.active = False
		i.salvar()

def getRandomProxy():
	resp=[]
	date_hj = datetime.today()
	date_atras = date_hj - timedelta(days=1)

	res = Proxy_Connection.objects.filter(date__range=(date_atras, date_hj), active=1)
	t_row = res.count()
	random_index = randint(0, t_row - 1)
	ele_p = res[random_index]
	resp.append(ele_p.ip)
	resp.append(ele_p.port)
	return resp

def getLatestProxy(dias):
	resp=[]
	date_hj = datetime.today()
	date_atras = date_hj - timedelta(days=int(dias))

	res = Proxy_Connection.objects.filter(date__range=(date_atras, date_hj), active=1)
	for item in res:
		resp.append(item.ip + ":" + str(item.port))
	return resp


def normal_connection():
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument("--incognito")
	chrome_options.add_argument('--disable-extensions')
	chrome_options.add_argument("--disable-setuid-sandbox")
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--disable-gpu')
	chrome_options.add_argument('--no-sandbox')
	return webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=chrome_options)

def private_connection(PROXY_HOST,PROXY_PORT, mobile):
	chrome_options = webdriver.ChromeOptions()
	PROXY = PROXY_HOST + ':' + str(PROXY_PORT)
	chrome_options.add_argument('--proxy-server=%s' % PROXY)
	chrome_options.add_argument("--incognito")
	#chrome_options.add_argument("user-agent=iPhone")
	chrome_options.add_argument('--disable-extensions')
	chrome_options.add_argument("--disable-setuid-sandbox")
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--disable-gpu')
	chrome_options.add_argument('--no-sandbox')
	if mobile:
		chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
	return webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=chrome_options)		

