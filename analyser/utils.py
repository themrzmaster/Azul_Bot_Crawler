import matplotlib as mpl
mpl.use('Agg')
from django_pandas.io import read_frame
from django.apps import apps
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
from matplotlib.dates import DayLocator
import matplotlib.gridspec as gridspec
import io
import base64
#output - dataframe with full Azul_Trecho Database
def get_full_dataframe():
	Azul = apps.get_model('azul', 'Azul_Trecho')
	qs = Azul.objects.all()
	return read_frame(qs)

#input - dataframe with extraction dates that wants to extract
#output - list of different date() on dataframe   
def get_all_extraction_dates(dx, ordem):
	dias = []
	dx1 = dx.extracted_date.dt.normalize().value_counts().reset_index()
	dx1.columns = ['data', 'count']
	for d in dx1.data:
		dias.append(d.date())
	if ordem:
		return sorted(dias)
	else:
		return dias	
		

def get_all_extraction_datetimes_and_price(dx, ida):
	if ida:
		return dx[['extracted_date', 'preco_ida']].copy()
	else:
		return dx[['extracted_date', 'preco_volta']].copy()

#input - dataframe with destinations that wants to extract
#output - list of all kind of destinations available on dataframe
def get_all_destinations(dx):
	return dx.destino.unique()

def get_volta_dates(dx):
	dias = []
	dx1 = dx.data_volta.dt.normalize().value_counts().reset_index()
	dx1.columns = ['data', 'count']
	for d in dx1.data:
		dias.append(d.date())
	return dias

def get_ida_dates(dx):
	dias = []
	dx1 = dx.data_ida.dt.normalize().value_counts().reset_index()
	dx1.columns = ['data', 'count']
	for d in dx1.data:
		dias.append(d.date())
	return dias

def get_all_dates(dx):
	dias = []
	d1 = get_ida_dates(dx)
	d2 = get_volta_dates(dx)
	for i in d1:
		dias.append(i)
	for x in d2:
		dias.append(x)
	return sorted(dias)		

#input - dataframe with all kind of destinations
#output- dataframe with only specified destination
def get_by_destination(dx, city):
	return dx[dx['destino'] == city].reset_index() 

#input - dataframe, day to extract, month to extract
#output - dataframe with only specified extraction date
def get_by_extraction_date(dx, day, month):
	return dx.loc[(dx.extracted_date.dt.month == month) & (dx.extracted_date.dt.day == day)]

#input - dataframe, day to extract, month to extract
#output - dataframe with only specified ida date
def get_by_ida_date(dx, day, month):
	return dx.loc[(dx.data_ida.dt.month == month) & (dx.data_ida.dt.day == day)]

#input - dataframe, day to extract, month to extract
#output - dataframe with only specified volta date
def get_by_volta_date(dx, day, month):
	return dx.loc[(dx.data_volta.dt.month == month) & (dx.data_volta.dt.day == day)]

#input - dataframe, initial period, final period
#output - dataframe with only dates between values
def get_between_time(dx, initial_day, initial_month, end_day, end_month, ida):
	now_year = str(datetime.now().year)
	if ida:
		mask = (dx.data_ida.dt.day >= initial_day) & (dx.data_ida.dt.month >= initial_month) & (dx.data_ida.dt.day <= end_day) & (dx.data_ida.dt.month <= end_month)
	else:
		mask = ''

	return dx.loc[mask]

def group_min_value(dx, ida):
	if ida:
		dx['ida_full'] = dx.data_ida.dt.date
		#dx['ida_month'] = dx.data_ida.dt.month
		d1 = dx.groupby([dx.ida_full, dx.origem, dx.destino]).preco_ida.min().reset_index()
		d1.columns = ['data', 'origem', 'destino', 'preco']
		return d1

#input - dx = dataframe, day_trip = dia da viagem, month_trip = mes da viagem, extraction_day = dia a ser extraido, extraction_month = mes a ser extraido, 
#destino = destino do voo, ida = BOOLEAN TRUE = ida ' FALSE = VOLTA
def getPlot1_data(dx, day_trip, month_trip, extraction_day, extraction_month, destino, ida):
	d1 = get_by_destination(dx, destino)
	d2 = get_by_extraction_date(d1, extraction_day, extraction_month)
	if ida:
		d3 = get_by_ida_date(d2, day_trip, month_trip)
	else:
		d3 = get_by_volta_date(d2, day_trip, month_trip)
	return d3

def getPlot2_data(dx, extraction_day, extraction_month, initial_day, initial_month, end_day, end_month, destino, ida):
	d1 = get_by_destination(dx, destino)
	d2 = get_by_extraction_date(d1, extraction_day, extraction_month)
	d4 = get_between_time(d2, initial_day, initial_month, end_day, end_month, ida)
	d3 = group_min_value(d4, ida)
	return d3

#plotter 1

def Plot1(dx, destino, ida, data, extracao):
	plt.clf()
	dates = get_all_extraction_datetimes_and_price(dx, ida)
	if ida:
		plt.plot(dates.extracted_date.dt.time, dates.preco_ida)
		plt.title("To: " + destino + " - " + data + " - Extracao: " + extracao)
	else:
		plt.plot(dates.extracted_date.dt.time, dates.preco_volta)
		plt.title("From: " + destino + " - " + data + " - Extracao: " + extracao)
	plt.ylabel('Preco')
	plt.xlabel('Hora')
	plt.xticks(rotation=55)
	plt.tight_layout()
	f = io.BytesIO()
	plt.savefig(f, format="png", facecolor=(0.95, 0.95, 0.95))
	encoded_img = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
	f.close()
	return encoded_img

def Plot2(dx, destino, ida, data_inicio, data_fim, extracao):
	plt.clf()
	if ida:
		fig, ax = plt.subplots()
		formatter = DateFormatter('%d/%m')
		plt.gcf().axes[0].xaxis.set_major_formatter(formatter) 
		xtick_locator = DayLocator()
		ax.xaxis.set_major_locator(xtick_locator)
		ax.plot(dx.data, dx.preco, markerfacecolor='CornflowerBlue', markeredgecolor='white')
		fig.autofmt_xdate()
		ax.set_xlim(dx['data'].iloc[0], dx['data'].iloc[-1])
		#plt.plot_date(dx.data, dx.preco)
		plt.title("To: " + destino + " - " + data_inicio + " a " + data_fim + " - Extracao: " + extracao)
	else:
		plt.plot(str(dx.dia) + "/" + str(dx.mes), dx.preco)
		plt.title("To: " + destino + " - " + data_inicio + " a " + data_fim + " - Extracao: " + extracao)
		#plt.plot(dates.extracted_date.dt.time, dates.preco_volta)
		#plt.title("From: " + destino + " - " + data + " - Extracao: " + extracao)
	plt.ylabel('Preco')
	plt.xlabel('Dias')
	plt.xticks(rotation=55)
	plt.tight_layout()
	f = io.BytesIO()
	plt.savefig(f, format="png", facecolor=(0.95, 0.95, 0.95))
	encoded_img = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
	f.close()
	return encoded_img
