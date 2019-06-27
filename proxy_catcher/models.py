from django.db import models

# Create your models here.
class Proxy_Connection(models.Model):
	date = models.DateTimeField()
	ip = models.GenericIPAddressField()
	port = models.IntegerField()
	active = models.BooleanField(default=True)

	def salvar(self):
		self.save()

	def get_date(self):
		return self.date

	def get_ip(self):
		return self.ip	

	def get_port(self):
		return self.port		