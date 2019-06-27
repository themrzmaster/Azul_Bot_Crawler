from __future__ import absolute_import, unicode_literals
from selenium.webdriver import FirefoxProfile
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from django.apps import apps
from datetime import datetime, timedelta
from random import randint
from airtrick.extract_settings import Azul_Settings
from .models import Azul_Trecho
import logging
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
#timezone.activate(pytz.timezone("America/Sao_Paulo"))

def private_connection(PROXY_HOST,PROXY_PORT):
	fp = FirefoxProfile()
	o = Options()
	o.add_argument('-private')
	fp.set_preference("network.proxy.type", 1)
	fp.set_preference("network.proxy.http",PROXY_HOST)
	fp.set_preference("network.proxy.http_port",int(PROXY_PORT))
	fp.set_preference("network.proxy.ssl",PROXY_HOST)
	fp.set_preference("network.proxy.ssl_port",int(PROXY_PORT))
	fp.set_preference("general.useragent.override","iPhone")
	fp.update_preferences()
	return Firefox(firefox_profile=fp, firefox_options=o)

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
		proc = subprocess.call("find /tmp -name '*rust_mozprofile*' -exec rm -r {} \;", shell=True)
		proc = subprocess.call("find /tmp -name '*tmpaddon*' -exec rm -r {} \;", shell=True)
 		logger.info("Memory usage is too high... killing processes and starting over")
 		resetXvfb()

def resetXvfb():
	proc = subprocess.call('killall firefox', shell=True)
	proc = subprocess.call('killall Xvfb', shell=True)
	proc = subprocess.call('killall geckodriver', shell=True)
	sp = subprocess.call('nohup Xvfb :99 -screen 0 375x667x8 &', shell=True)
	#xvfb = subprocess.Popen(['Xvfb', ':99'])
	time.sleep(2)
	os.environ["DISPLAY"]=":99"
	logger.info('Xvfb reset!')



def getFlight(proxy_ip, proxy_port, mes_ida, ida_dia, mes_volta, volta_dia, origem_air, destino_air):
	#create browser (proxy)
	logger.info('Initializing Azul Flight extraction at :' + str(datetime.now()))
	logger.info(proxy_ip + ":" + str(proxy_port))

	try:
		browser = private_connection(proxy_ip, proxy_port)
		browser.get('https://m.voeazul.com.br/MobileSite/Booking/Search')
	except WebDriverException as e:
		if 'netTimeout' in str(e):
			#remove proxy if webdriver too long (TODO)
			logger.info('Connection timeout, marking proxy as unactive!')
			p = Proxy_Connection.objects.filter(ip=proxy_ip, port=proxy_port)
			for i in p:
				i.active = False
				i.salvar()

			new_proxy = getRandomProxy()
			browser = private_connection(new_proxy[0], new_proxy[1])
			browser.get('https://m.voeazul.com.br/MobileSite/Booking/Search')

		else:
			try:
				browser.quit()
			except:
				logger.info("cant quit driver.. maybe not running..")	
			resetXvfb()
			browser = private_connection(proxy_ip, proxy_port)
			browser.get('https://m.voeazul.com.br/MobileSite/Booking/Search')
		#except:
			#logger.error('Xvfb reseted, but still not working')
			#return
			
			
	#find selecao de cidade
	btnOrigem = browser.find_element_by_id("btnVooOrigem")
	btnOrigem.click()
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
	cidade2 = browser.find_element_by_partial_link_text(destino_air)
	cidade2.click()

	#IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA IDA

	#data ida btnVooDataIda
	btnIda = browser.find_element_by_id("btnVooDataIda")
	btnIda.click()

	#month changer

	mes_atual = browser.find_element_by_class_name("ui-datepicker-month").text

	while meses[unidecode.unidecode(mes_atual)] != mes_ida:
		#click next month .ui-datepicker-next
		browser.find_element_by_class_name("ui-datepicker-next").click()
		mes_atual = browser.find_element_by_class_name("ui-datepicker-month").text
		#print mes_atual

	#day ida
	dataida = browser.find_element_by_link_text(str(ida_dia))
	dataida.click()

	#VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA

	#data volta btnVooDataVolta
	btnVolta = browser.find_element_by_id("btnVooDataVolta")
	btnVolta.click()

	mes_atual = browser.find_element_by_class_name("ui-datepicker-month").text

	while meses[unidecode.unidecode(mes_atual)] != mes_volta:
		#click next month .ui-datepicker-next
		browser.find_element_by_class_name("ui-datepicker-next").click()
		mes_atual = browser.find_element_by_class_name("ui-datepicker-month").text
		#print mes_atual

	#day volta
	datavolta = browser.find_element_by_link_text(str(volta_dia))
	datavolta.click()

	#divPesquisar
	btnPesquisa= browser.find_element_by_id("divPesquisar")
	btnPesquisa.click()

	#wait page to load after click submission
	try:
		myElem = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'divVooEspacoAzul')))
	except TimeoutException as ex:
		#timeout exception
		WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'divVooEspacoAzul')))

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
			best_val_ida = cur_val
			best_trecho = trecho

	try:
		cod_ida = str(best_trecho['farebasiscode'])
		#price ida
		best_val_ida_str = str(best_val_ida)
		#print best_trecho['journeysellkey']

		dat = between(best_trecho['journeysellkey'], origem_air+"~", "~"+destino_air)
		datetime_object_ida = datetime.strptime(dat, '%m/%d/%Y %H:%M')
		#date ida
		data_ida_obj = str(datetime_object_ida)
	except ValueError:
		logger.error('Data nao disponivel...')
		return
			

	#VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA VOLTA
	best_val_volta = 99999
	for trecho in volta_elemento.find_all("div", class_="divSelectFlightTypeFaresMaisAzul"):
		#GET CHEAPEAST FLIGHT
		cur_val = float(trecho['amountadt'].replace(',', '.'))
		if (cur_val < best_val_volta):
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
		logger.error('Data nao disponivel...')
		return

	browser.quit()
	logger.info('Data extracted: ' + str(now_date) + origem_air + destino_air + data_ida_obj + data_volta_obj + best_val_ida_str + best_val_volta_str + str(cod_ida) + str(cod_volta))
	#exit and clean
	
	a_obj = Azul_Trecho.objects.create(extracted_date=now_date,origem=origem_air,destino=destino_air,data_ida=data_ida_obj,data_volta=data_volta_obj,preco_ida=best_val_ida_str,preco_volta=best_val_volta_str,azul_code_ida=cod_ida,azul_code_volta=cod_volta)
	a_obj.salvar()
	#browser.close()
	#cleanFirefox()


def getRandomProxy():
	resp=[]
	date_hj = datetime.today()
	date_atras = date_hj - timedelta(days=2)

	res = Proxy_Connection.objects.filter(date__range=(date_atras, date_hj), active=1)
	t_row = res.count()
	random_index = randint(0, t_row - 1)
	ele_p = res[random_index]
	resp.append(ele_p.ip)
	resp.append(ele_p.port)
	return resp


@task()
def get_azul():

	mes_ida = Azul_Settings['mes_ida']
	dia_ida = random.choice(Azul_Settings['dias_ida'])
	
	mes_volta = Azul_Settings['mes_volta']
	dia_volta = random.choice(Azul_Settings['dias_ida'])
	
	origem_air = random.choice(Azul_Settings['origem'])
	destino_air = random.choice(Azul_Settings['destinos'])
	
	checkMem()
	#get random proxy
	proxy_l = getRandomProxy()
	getFlight(proxy_l[0], proxy_l[1], mes_ida, dia_ida, mes_volta, dia_volta, origem_air, destino_air )



#print html_source