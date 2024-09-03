from django.db import models
from django.db.models import TextChoices

# -------[ MODELS PERSON -> CLIENT & SUPPLIER  ]-------
class Person(models.Model):
    cuit = models.CharField(max_length=11, null=True, blank=True)
    phone = models.IntegerField(max_length=15, null=True, blank=True)
    
    def __str__(self):
        return f'Cuit: {self.cuit} — Teléfono: {self.phone}'
    

class Client(Person):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f'Cliente: {self.first_name} {self.last_name} — {super().__str__()}'

class Supplier(Person):
    company = models.CharField(max_length=50)

    def __str__(self):
        return f'Proveedor: {self.company} — {super().__str__()}'

# -------[ MODELS CURRENT ACCOUNT ]-------
class CurrentAccount(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True)
    resumen = models.TextField()

    def __str__(self):
        if self.client:
            return f'Cuenta Corriente de: {self.client.first_name} Deuda: ${self.resumen}'
        elif self.supplier:
            return f'Cuenta Corriente de: {self.supplier.company} Deuda: ${self.resumen}'
        
        return 'Cuenta Corriente'
    
    