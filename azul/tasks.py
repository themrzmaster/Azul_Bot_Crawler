from __future__ import absolute_import, unicode_literals
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from django.apps import apps
from datetime import datetime, timedelta
from random import randint
from airtrick.extract_settings import Azul_Settings
from .models import Azul_Trecho
import logging
from airtrick.utils import *
from time import sleep
import psutil
import random
import unidecode
import os
import time
import subprocess
from celery import task

meses = {'janeiro' : 1, 'fevereiro' : 2, 'marco' : 3, 'abril' : 4, 'maio' : 5, 'junho' : 6, 'julho' : 7, 'agosto' : 8, 'setembro' : 9, 'outubro' : 10, 'novembro' : 11, 'dezembro' : 12}
logger = logging.getLogger(__name__)
Proxy_Connection = apps.get_model('proxy_catcher', 'Proxy_Connection')


def browserGet(browser, proxy_ip, proxy_port):
	try:
		browser.get('https://m.voeazul.com.br/MobileSite/Booking/Search')
	except TimeoutException as e:
		#remove proxy if webdriver too long (TODO)
		innactivateProxy(proxy_ip, proxy_port)
		new_proxy = getRandomProxy()
		browser = private_connection(new_proxy[0], new_proxy[1], True)
		browser.get('https://m.voeazul.com.br/MobileSite/Booking/Search')
	except WebDriverException as e:
		logger.error(e)
		try:
			resetXvfb()
			browser = private_connection(proxy_ip, proxy_port, True)
			browser.get('https://m.voeazul.com.br/MobileSite/Booking/Search')
		except:
			logger.info("cant quit driver.. maybe not running..")	
	except:
		logger.error("error opening url...")	
		browser.quit()

def getFlight(proxy_ip, proxy_port, mes_ida, ida_dia, mes_volta, volta_dia, origem_air, destino_air):
	#create browser (proxy)
	logger.info('Initializing Azul Flight extraction - Params :' + str(ida_dia) + "/" + str(mes_ida) + " " + str(volta_dia) + "/"+ str(mes_volta))
	logger.info(proxy_ip + ":" + str(proxy_port))

	browser = private_connection(proxy_ip, proxy_port, True)
	browserGet(browser, proxy_ip, proxy_port)

	try:
		WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='btnVooOrigem']"))).click()
	except TimeoutException as e:
		logger.info("timeout ")
		logger.info(browser.page_source)
		browser.quit()
		#innactivateProxy(proxy_ip, proxy_port)
		proxy_l = getRandomProxy()
		proxy_ip = proxy_l[0]
		proxy_port = proxy_l[1]
		browser = private_connection(proxy_ip, proxy_port, True)
		browserGet(browser, proxy_ip, proxy_port)
		WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='btnVooOrigem']"))).click()
	#btnOrigem.click()
	#lista de cidades, this case select Confins 
	cidade = browser.find_element_by_partial_link_text(origem_air)
	#print cidade
	cidade.click()
	#voltar iconSearchVoltar
	btnVolta = browser.find_element_by_id("iconSearchVoltar")
	btnVolta.click()
	#destino
	btnDestino = browser.find_element_by_id("btnVooDestino")
	btnDestino.click()
	#lista de cidades, destino
	logger.info(destino_air)
	WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, destino_air)))
	cidade2 = browser.find_element_by_partial_link_text(destino_air).click()
	logger.info("parcial link text destino passed")
	#IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA

	#data ida btnVooDataIda
	btnIda = browser.find_element_by_id("btnVooDataIda")
	btnIda.click()

	#month changer

	#WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-month")))
	sleep(1)
	mes_atual = browser.find_element_by_class_name("ui-datepicker-month").text
	mes_atual_n = int(meses[unidecode.unidecode(mes_atual.lower())]) 
	#logger.info(mes_ida)
	#logger.info(mes_atual_n)
	while mes_atual_n != int(mes_ida):
		#click next month .ui-datepicker-next
		#logger.info(str(mes_atual_n))
		browser.find_element_by_class_name("ui-datepicker-next").click()
		#sleep(3)
		#WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-month")))
		mes_atual = browser.find_element_by_class_name("ui-datepicker-month").text
		mes_atual_n = int(meses[unidecode.unidecode(mes_atual.lower())])
		#print mes_atual

	#day ida
	logger.info('passed')
	dataida = browser.find_element_by_link_text(str(ida_dia))
	dataida.click()

	#VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA

	#data volta btnVooDataVolta
	btnVolta = browser.find_element_by_id("btnVooDataVolta")
	btnVolta.click()
	sleep(1)
	mes_atual = browser.find_element_by_class_name("ui-datepicker-month").text #setembro
	mes_atual_n = int(meses[unidecode.unidecode(mes_atual.lower())]) #9
	#logger.info('mes atual:' + unidecode.unidecode(mes_atual) + " volta: " + str(mes_volta))
	while mes_atual_n != int(mes_volta):
		#click next month .ui-datepicker-next
		browser.find_element_by_class_name("ui-datepicker-next").click()
		mes_atual = browser.find_element_by_class_name("ui-datepicker-month").text
		mes_atual_n = int(meses[unidecode.unidecode(mes_atual.lower())])


	#logger.info("volta_dia")
	datavolta = browser.find_element_by_link_text(str(volta_dia))
	datavolta.click()
	sleep(0.5)

	#logger.info("pesquisa")
	#divPesquisar
	btnPesquisa= browser.find_element_by_id("divPesquisar")
	btnPesquisa.click()

	#wait page to load after click submission
	try:
		myElem = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'divVooEspacoAzul')))
	except TimeoutException as ex:
		#timeout exception
		logger.error("timeout waiting for divVooEspacoAzul")
		browser.quit()
	#logger.info("source")
	#got the source code, work with it BEUTIFULSOUP IT :)
	src = browser.page_source
	soup = BeautifulSoup(src, "html.parser")

	first_ele = soup.find_all("div", class_="listaSelectReais")

	#elemento ida (contem divs da ida)
	ida_elemento = first_ele[0]
	#elemento volta (contem divs da volta)
	volta_elemento = first_ele[1]

	#IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDAIDA IDA IDA IDA IDA IDA IDA IDA
	best_val_ida = 99999
	for trecho in ida_elemento.find_all("div", class_="divSelectFlightTypeFaresMaisAzul"):
		#GET CHEAPEAST FLIGHT
		cur_val = float(trecho['amountadt'].replace(',', '.'))
		if (cur_val < best_val_ida):
			#check if escala exists in this trecho
			if "^AD" not in trecho['journeysellkey']:
				best_val_ida = cur_val
				best_trecho = trecho
	if (best_val_ida == 99999):
		logger.info("Data nao disponivel!")
		browser.quit()
		return
				
	logger.info(best_val_ida)		

	try:
		cod_ida = str(best_trecho['farebasiscode'])
		#price ida
		best_val_ida_str = str(best_val_ida)
		#print best_trecho['journeysellkey']

		dat = between(best_trecho['journeysellkey'], origem_air+"~", "~"+destino_air)
		datetime_object_ida = datetime.strptime(dat, '%m/%d/%Y %H:%M')
		#date ida
		data_ida_obj = str(datetime_object_ida)
	except ValueError as w:
		logger.error(w)
		logger.error('data error... should not be here')
		browser.quit()
		return

			

	#VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA
	best_val_volta = 99999
	for trecho in volta_elemento.find_all("div", class_="divSelectFlightTypeFaresMaisAzul"):
		#GET CHEAPEAST FLIGHT
		cur_val = float(trecho['amountadt'].replace(',', '.'))
		if (cur_val < best_val_volta):
			#check escala
			if "^AD" not in trecho['journeysellkey']:
				best_val_volta = cur_val
				best_trecho = trecho
	try:
		cod_volta = str(best_trecho['farebasiscode'])
		best_val_volta_str = str(best_val_volta)

		dat = between(best_trecho['journeysellkey'], destino_air+"~", "~"+origem_air)
		datetime_object_volta = datetime.strptime(dat, '%m/%d/%Y %H:%M')
		data_volta_obj = str(datetime_object_volta)
		now_date = datetime.now()
	except ValueError:
		logger.error('Data nao disponivel... should not be here')
		browser.quit()
		return

	browser.quit()
	logger.info('Data extracted: ' + str(now_date) + origem_air + destino_air + data_ida_obj + data_volta_obj + best_val_ida_str + best_val_volta_str + str(cod_ida) + str(cod_volta))
	#exit and clean
	
	a_obj = Azul_Trecho.objects.create(extracted_date=now_date,origem=origem_air,destino=destino_air,data_ida=data_ida_obj,data_volta=data_volta_obj,preco_ida=best_val_ida_str,preco_volta=best_val_volta_str,azul_code_ida=cod_ida,azul_code_volta=cod_volta)
	a_obj.salvar()
	#browser.close()
	#cleanFirefox()



@task()
def get_azul():
	logger.info("Starting to pick up values..!")
	"""
	mes_ida = random.choice(Azul_Settings['mes_ida'])
	dia_ida = random.choice(Azul_Settings['dias_ida'])
	
	mes_volta = random.choice(Azul_Settings['mes_volta'])
	while (int(mes_volta) < int(mes_ida)):
		mes_volta = random.choice(Azul_Settings['mes_volta'])
	dia_volta = random.choice(Azul_Settings['dias_volta'])
	"""
	#get current date
	dia_hj = int(time.strftime("%d"))
	mes_hj = int(time.strftime("%m"))

	valid_day = False
	#random choose holiday
	while(not valid_day):
		ida_ex = random.choice(Azul_Settings['datas'])
		logger.info(ida_ex)
		dia_ida_ex, mes_ida_ex = ida_ex['data'].split("/")
		dia_end_ex, mes_end_ex = ida_ex['end'].split("/")
		#check if holiday has passed
		if mes_hj < int(mes_ida_ex):
			valid_day = True
		elif mes_hj == int(mes_ida_ex) and dia_hj < int(dia_ida_ex):
			valid_day = True
		else:
			valid_day = False

	dia_ida_ex = int(dia_ida_ex)
	dia_end_ex = int(dia_end_ex)
	mes_ida = int(mes_ida_ex)
	mes_volta = int(mes_end_ex)

	#get 1 day before or later as well
	#cant be day 32
	dia_ida = random.choice([dia_ida_ex, dia_ida_ex + 1, dia_ida_ex - 1])
	if dia_ida == 32:
		dia_ida = 1
		mes_ida = mes_ida + 1
			
	#care for volta > ida
	valid_day = False
	if mes_ida == mes_volta:
		while(not valid_day):
			dia_volta = random.choice([dia_end_ex, dia_end_ex + 1, dia_end_ex - 1])
			logger.info(dia_volta)
			if dia_ida < dia_volta:
				valid_day = True
			else:
				valid_day = False	
	else:
		dia_volta = random.choice([dia_end_ex, dia_end_ex + 1, dia_end_ex + 2])
		#diferent months

	origem_air = random.choice(Azul_Settings['origem'])
	destino_air = random.choice(Azul_Settings['destinos'])

	checkMem()
	#get random proxy
	proxy_l = getRandomProxy()
	getFlight(proxy_l[0], proxy_l[1], mes_ida, dia_ida, mes_volta, dia_volta, origem_air, destino_air)



#print html_source