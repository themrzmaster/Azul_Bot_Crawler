import matplotlib as mpl
mpl.use('Agg')
from django.shortcuts import render
from django_pandas.io import read_frame
from django.apps import apps
from django.http import JsonResponse
from datetime import datetime
import matplotlib.pyplot as plt
import utils

# Create your views here.
df = utils.get_full_dataframe()


def index(request):
	dest_list = utils.get_all_destinations(df)
	ex_dates = utils.get_all_extraction_dates(df, True)
	volta_dates = utils.get_volta_dates(df)
	ida_dates = utils.get_ida_dates(df)
	return render(request, 'airstatus/index.html', {'destinos': dest_list, 'extraction_dates' : ex_dates, 'volta_dates' : volta_dates, 'ida_dates' : ida_dates})

def index2(request):
	dest_list = utils.get_all_destinations(df)
	ex_dates = utils.get_all_extraction_dates(df, True)
	datas = utils.get_all_dates(df)
	dates_ = datas
	return render(request, 'airstatus/grafico2.html', {'destinos': dest_list, 'extraction_dates' : ex_dates, 'dates_' : dates_})	


def AjaxRequest(request):
	destino = request.GET.get('destino', None)
	data_trip_ida = request.GET.get('ida', None)
	data_trip_volta = request.GET.get('volta', None)
	data_extract = request.GET.get('extracao', None)
	get_volta = request.GET.get('get_volta', None)

	data_trip_ida_trimmed = datetime.strptime(data_trip_ida, '%B %d, %Y')
	data_trip_volta_trimmed = datetime.strptime(data_trip_volta, '%B %d, %Y')
	data_extract_trimmed = datetime.strptime(data_extract, '%B %d, %Y')
	if int(get_volta) == 1:
		dx = utils.getPlot1_data(df, data_trip_volta_trimmed.day, data_trip_volta_trimmed.month, data_extract_trimmed.day, data_extract_trimmed.month, destino, False)
		encoded_img = utils.Plot1(dx, destino, False, data_trip_volta, data_extract)
	else:	
		dx = utils.getPlot1_data(df, data_trip_ida_trimmed.day, data_trip_ida_trimmed.month, data_extract_trimmed.day, data_extract_trimmed.month, destino, True)
		encoded_img = utils.Plot1(dx, destino, True, data_trip_ida, data_extract)

	return JsonResponse('<img class="plotimg" src="data:image/png;base64,%s" />' % encoded_img, safe=False)

def AjaxRequest2(request):
	destino = request.GET.get('destino', None)
	data_extract = request.GET.get('extracao', None)
	periodo_inicio = request.GET.get('inicio', None)
	periodo_fim = request.GET.get('fim', None)

	periodo_inicio_trimmed = datetime.strptime(periodo_inicio, '%B %d, %Y')
	periodo_fim_trimmed = datetime.strptime(periodo_fim, '%B %d, %Y')
	data_extract_trimmed = datetime.strptime(data_extract, '%B %d, %Y')

#def getPlot2_data(dx, extraction_day, extraction_month, initial_day, initial_month, end_day, end_month, destino, ida):
	dx = utils.getPlot2_data(df, data_extract_trimmed.day, data_extract_trimmed.month, periodo_inicio_trimmed.day, periodo_inicio_trimmed.month, periodo_fim_trimmed.day, periodo_fim_trimmed.month, destino, True)
	encoded_img = utils.Plot2(dx, destino, True, periodo_inicio, periodo_fim, data_extract)
	return JsonResponse('<img class="plotimg" src="data:image/png;base64,%s" />' % encoded_img, safe=False)


    