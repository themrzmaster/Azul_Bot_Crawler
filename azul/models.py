from django.db import models

# Create your models here.

class Azul_Trecho(models.Model):
	extracted_date = models.DateTimeField()
	origem = models.CharField(max_length=10)
	destino = models.CharField(max_length=10)
	data_ida = models.DateTimeField()
	data_volta = models.DateTimeField()
	preco_ida = models.DecimalField(max_digits=10, decimal_places=2)
	preco_volta = models.DecimalField(max_digits=10, decimal_places=2)
	azul_code_ida = models.CharField(max_length=10)
	azul_code_volta = models.CharField(max_length=10)

	def salvar(self):
		self.save()
