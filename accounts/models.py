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
    notes = models.TextField(blank=True, verbose_name='Notas')  # Nuevo campo (antes era resumen)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Cuenta Corriente'
        verbose_name_plural = 'Cuentas Corrientes'

    def __str__(self):
        return f'Cuenta Corriente de {self.person}'
    
    def get_balance(self):
        """Calcula el balance en tiempo real: (ventas pendientes/parciales + compras) - pagos"""
        from django.db.models import Sum
        from finances.models import Sale, Purchase, Payment
        
        # Ventas pendientes o con pago parcial - cliente debe
        # Solo suma ventas con payment_status='PE' (Pendiente) o 'PP' (Pago Parcial)
        # Las ventas con payment_status='PA' (Pagado) NO suman
        sales = Sale.objects.filter(
            person=self.person,
            payment_status__in=['PE', 'PP']  # Solo pendientes y pagos parciales
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Compras a cuenta corriente - nosotros debemos al proveedor
        purchases = Purchase.objects.filter(
            person=self.person
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Pagos recibidos de clientes (positivos) o hechos a proveedores (negativos)
        payments_income = Payment.objects.filter(
            person=self.person,
            payment_type='I'  # Income - pago recibido de cliente
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        payments_expense = Payment.objects.filter(
            person=self.person,
            payment_type='E'  # Expense - pago hecho a proveedor
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Balance = lo que nos deben (ventas) - lo que pagaron + lo que debemos (compras) - lo que pagamos
        balance = (sales - payments_income) + (purchases - payments_expense)
        
        return balance
    
    def get_transactions(self):
        """Obtiene todas las transacciones ordenadas cronológicamente"""
        from finances.models import Ticket
        return Ticket.objects.filter(person=self.person).select_related(
            'sale', 'purchase', 'payment', 'creditnote'
        ).order_by('-date_time')
    
    def get_ledger(self):
        """Genera un libro mayor con balance corriente después de cada transacción"""
        from finances.models import Sale, Purchase, Payment, CreditNote
        
        transactions = []
        running_balance = 0
        
        # Obtener todas las transacciones
        tickets = self.get_transactions().order_by('date_time')
        
        for ticket in tickets:
            # Determinar tipo, monto y código
            trans_type = None
            amount = ticket.amount or 0
            
            if hasattr(ticket, 'sale') and ticket.sale:
                trans_type = 'Venta'
                running_balance += amount  # Cliente debe (siempre que tenga persona asignada)
            elif hasattr(ticket, 'purchase') and ticket.purchase:
                trans_type = 'Compra'
                running_balance += amount  # Nosotros debemos
            elif hasattr(ticket, 'payment') and ticket.payment:
                if ticket.payment.payment_type == 'I':
                    trans_type = 'Pago Recibido'
                    running_balance -= amount  # Cliente pagó
                else:
                    trans_type = 'Pago Realizado'
                    running_balance -= amount  # Nosotros pagamos
            elif hasattr(ticket, 'creditnote') and ticket.creditnote:
                trans_type = 'Nota de Crédito'
                running_balance -= amount
            else:
                continue
            
            if trans_type:
                transactions.append({
                    'date': ticket.date_time,
                    'ticket_id': ticket.id,
                    'type': trans_type,
                    'description': str(ticket),
                    'amount': amount,
                    'balance': running_balance,
                    'ticket': ticket
                })
        
        return transactions
    
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