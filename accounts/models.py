from django.db import models
from django.db.models import TextChoices

class TipoChoices(TextChoices):
    CLIENTE = 'C', 'Cliente'
    PROVEEDOR = 'P', 'Proveedor'

# Create your models here.
class Person(models.Model):
    cuit = models.CharField(max_length=11)
    telefono = models.CharField(max_length=15)
    tipo = models.CharField(max_length=1, choices=TipoChoices.choices)
    
    def __str__(self):
        return f'Cuit: {self.cui} — Teléfono: {self.telefono} — Tipo: {self.tipo.get_tipo_display()}'
    

class Client(Person):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return f'Cliente:\n{super().__str__()} — Nombre: {self.nombre}'
    

class Provider(Person):
    empresa = models.CharField(max_length=50)

    def __str__(self):
        return f'Proveedor:\n{super().__str__()} — Empresa: {self.empresa}'
    

class CurrentAccount(models.Model):
    persona = models.ForeignKey(Person, on_delete=models.CASCADE)
    resumen = models.TextField()