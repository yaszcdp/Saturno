from django.db import models
from django.db.models import TextChoices

# -------[ MODELS PERSON -> CLIENT & SUPPLIER  ]-------
class Person(models.Model):
    cuit = models.CharField(max_length=11, null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name='Ciudad')
    
    def __str__(self):
        return f'Cuit: {self.cuit} — Teléfono: {self.phone}'
    

class Client(Person):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    business_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Empresa/Verdulería')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Supplier(Person):
    company = models.CharField(max_length=50, verbose_name='Empresa')
    salesperson = models.CharField(max_length=100, null=True, blank=True, verbose_name='Vendedor')
    administrator = models.CharField(max_length=100, null=True, blank=True, verbose_name='Administrativo')

    def __str__(self):
        return f'{self.company}'

# -------[ MODELS CURRENT ACCOUNT ]-------
class CurrentAccount(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True)
    resumen = models.TextField(blank=True)

    def __str__(self):
        if self.person:
            return f'Cuenta Corriente de {self.person}'
        
        return 'Cuenta Corriente'
    
    '''def get_ledger(self):
        entries = self.entries.all().order_by('date', 'id')
        running = 0
        result = []
        for e in entries:
            running += e.amount
            result.append({
                'date': e.date,
                'ticket_pk': e.ticket_id,
                'description': e.description,
                'amount': e.amount,
                'balance_after': running, 
                'entry': e,
            })
        return result'''
    
'''
class AccountEntry(models.Model):
    ACCOUNT_TYPES = [
        ('SA', 'Sale'),
        ('PU', 'Purchase'),
        ('PA', 'Payment'),
        ('AD', 'Adjustment'),
    ]
    current_account = models.ForeignKey(CurrentAccount, related_name='entries', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    entry_type = models.CharField(max_length=2, choices=ACCOUNT_TYPES)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    ticket = models.ForeignKey('finances.Ticket', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:         
        ordering = ['date', 'id']
        
    def __str__(self):
            return f'{self.date} — {self.entry_type} — ${self.amount}'

'''