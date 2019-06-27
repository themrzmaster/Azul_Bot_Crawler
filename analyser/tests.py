from django.test import TestCase
from django_pandas.io import read_frame
from django.apps import apps


Azul = apps.get_model('azul', 'Azul_Trecho')
qs = Azul.objects.all()
df = read_frame(qs)

df['ex_day'] = df.extracted_date.dt.day
df['ex_month'] = df.extracted_date.dt.month

#menores precos por data e localidades

d1 = df.groupby([df.data_ida.dt.day, df.origem, df.destino]).preco_ida.min().reset_index()
d1.columns = ['data', 'origem', 'destino', 'preco']
d2 = df.groupby([df.data_volta.dt.day, df.destino, df.origem]).preco_volta.min().reset_index()
d2.columns = ['data', 'origem', 'destino', 'preco']

d3 = df.groupby([df.ex_day, df.ex_month, df.data_volta.dt.day, df.destino, df.origem]).preco_volta.min().reset_index()
d3.columns = ['ex_dia', 'ex_mes', 'dia', 'origem', 'destino', 'preco']

d4 = df.groupby([df.ex_day, df.ex_month, df.data_volta.dt.day, df.origem, df.destino]).preco_ida.min().reset_index()
d4.columns = ['ex_dia', 'ex_mes', 'dia', 'origem', 'destino', 'preco']

d5 = d4[d4['destino'] == 'GRU']
d6 = d4[d4['destino'] == 'CFB']
d7 = d4[d4['destino'] == 'BPS']




# Create your tests here.
