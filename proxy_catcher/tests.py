from __future__ import absolute_import, unicode_literals
from .models import Proxy_Connection
from datetime import datetime, timedelta
from random import randint
# Create your tests here.


def main():
	date_hj = datetime.today()
	date_atras = date_hj - timedelta(days=2)

	res = Proxy_Connection.objects.filter(date__range=(date_atras, date_hj))
	t_row = res.count()
	random_index = randint(0, t_row - 1)
	ele_p = res[random_index]
	proxy_ip = ele_p.ip
	proxy_port = ele_p.port
	print proxy_ip, proxy_port

main()	