from django.db import models
from django.db.models import TextChoices

# -------[ MODELS PERSON -> CLIENT & SUPPLIER  ]-------
class Person(models.Model):
    cuit = models.CharField(max_length=11, null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name='Ciudad')
    
    def get_full_name(self):
        """Retorna el nombre completo/empresa según el tipo de persona"""
        try:
            # Intentar obtener como Client
            client = Client.objects.get(pk=self.pk)
            return f"{client.first_name} {client.last_name}" if client.last_name else client.first_name
        except Client.DoesNotExist:
            try:
                # Intentar obtener como Supplier
                supplier = Supplier.objects.get(pk=self.pk)
                return supplier.company
            except Supplier.DoesNotExist:
                return str(self)
    
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
    account_number = models.PositiveIntegerField(unique=True, null=True, blank=True, verbose_name='Número de Cuenta')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True, verbose_name='Notas')  # Nuevo campo (antes era resumen)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Cuenta Corriente'
        verbose_name_plural = 'Cuentas Corrientes'
    
    def save(self, *args, **kwargs):
        # Solo asignar número automáticamente si es nueva cuenta y no tiene número
        if not self.pk and self.account_number is None:
            # Obtener el último número de cuenta
            last_account = CurrentAccount.objects.all().order_by('-account_number').first()
            if last_account and last_account.account_number is not None:
                self.account_number = last_account.account_number + 1
            else:
                self.account_number = 1  # Primera cuenta corriente
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Cuenta Corriente #{self.account_number} - {self.person}'
    
    def get_balance(self):
        """Calcula el balance en tiempo real: (ventas pendientes/parciales + compras) - pagos"""
        from django.db.models import Sum
        from finances.models import Sale, Purchase, Payment

        # Ventas PE/PP: usar get_pending_amount() para reflejar pagos parciales correctamente
        sales_qs = Sale.objects.filter(
            person=self.person,
            payment_status__in=['PE', 'PP']
        )
        sales_balance = sum(s.get_pending_amount() for s in sales_qs)

        # Compras a cuenta corriente - nosotros debemos al proveedor
        purchases = Purchase.objects.filter(
            person=self.person
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Pagos standalone recibidos/realizados (no vinculados a ventas específicas)
        payments_income = Payment.objects.filter(
            person=self.person,
            payment_type='I'
        ).aggregate(total=Sum('amount'))['total'] or 0

        payments_expense = Payment.objects.filter(
            person=self.person,
            payment_type='E'
        ).aggregate(total=Sum('amount'))['total'] or 0

        balance = (sales_balance - payments_income) + (purchases - payments_expense)
        return balance
    
    def get_transactions(self):
        """Obtiene todas las transacciones ordenadas cronológicamente"""
        from finances.models import Ticket
        return Ticket.objects.filter(person=self.person).select_related(
            'sale', 'purchase', 'payment', 'creditnote'
        ).order_by('-date_time')
    
    def get_ledger(self):
        """Genera un libro mayor con balance corriente después de cada transacción"""
        from finances.models import Sale, Purchase, Payment, CreditNote, PaymentDetail

        transactions = []
        running_balance = 0

        # Construir lista combinada: tickets + PaymentDetails, ordenados por datetime
        tickets = self.get_transactions().order_by('date_time')
        all_events = [(t.date_time, 'ticket', t) for t in tickets]

        pds = PaymentDetail.objects.filter(
            sale__person=self.person,
            is_reverted=False
        ).select_related('sale', 'sale__ticket_code').order_by('created_at')
        all_events += [(pd.created_at, 'pd', pd) for pd in pds]

        all_events.sort(key=lambda x: x[0])

        for _dt, entry_type, entry in all_events:
            if entry_type == 'ticket':
                ticket = entry
                trans_type = None
                amount = ticket.amount or 0

                if hasattr(ticket, 'sale') and ticket.sale:
                    if ticket.sale.status == 'CA':
                        continue
                    trans_type = 'Venta'
                    running_balance += amount
                elif hasattr(ticket, 'purchase') and ticket.purchase:
                    if ticket.purchase.status == 'CA':
                        continue
                    trans_type = 'Compra'
                    running_balance += amount
                elif hasattr(ticket, 'payment') and ticket.payment:
                    if ticket.payment.status == 'CA':
                        continue
                    if ticket.payment.payment_type == 'I':
                        trans_type = 'Pago Recibido'
                        running_balance -= amount
                    else:
                        trans_type = 'Pago Realizado'
                        running_balance -= amount
                elif hasattr(ticket, 'creditnote') and ticket.creditnote:
                    if ticket.creditnote.status == 'CA':
                        continue
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
                        'ticket': ticket,
                        'is_payment_detail': False,
                        'sale_code': '',
                    })

            else:  # 'pd' — PaymentDetail
                pd = entry
                amount = pd.amount  # Decimal, compatible con running_balance
                running_balance -= amount
                sale_code = pd.sale.ticket_code.code if pd.sale.ticket_code else '-'
                transactions.append({
                    'date': pd.created_at,
                    'ticket_id': None,
                    'type': f'Cobro ({pd.get_payment_method_display()})',
                    'description': f'${pd.amount} — {pd.get_payment_method_display()}',
                    'amount': amount,
                    'balance': running_balance,
                    'ticket': None,
                    'is_payment_detail': True,
                    'sale_code': sale_code,
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