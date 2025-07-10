from django.db import models
from accounts.models import Client, Supplier, CurrentAccount
from products.models import Product
from django.utils import timezone
from django.core.exceptions import ValidationError


#----------------[ GLOBAL ]----------------

PAYMENT_METHODS_CHOICES = [
    ('CA', 'Cash'),
    ('TR', 'Transfer'),
    ('CH', 'Check'),
    ('AC', 'Account'),
]

PAYMENT_METHODS_DICT = {
    'CA': 'cash',
    'TR': 'transfer',
    'CH': 'check',
    'AC': 'account',
}

TICKET_TYPE_CHOICES = [
    ('S', 'Sale'),
    ('P', 'Purchase'),
    ('E', 'Expense'),
    ('I', 'Income'),
]

STATUS_CHOICES = [
    ('PE', 'Pending'),
    ('CA', 'Canceled'),
    ('CC', 'CurrentAccount'),
    ('PA', 'Paid'),
    ('CO', 'Completed'),
]

#----------------[ CASH REGISTER ]----------------

class CashRegister(models.Model):
    date = models.DateField()
    initial_amounts = models.JSONField(default=dict)
    final_amounts = models.JSONField(default=dict)
    differences = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=[('O', 'Open'), ('C', 'Closed')], default='O')

    def __str__(self):
        return f'Register: {self.date} — Initial: ${self.initial_amounts} — Final: ${self.final_amounts}'


    def init_register(self, amounts):
        #Inicializa la caja registradora
        self.initial_amounts = amounts
        self.date = timezone.now().date()
        self.save()


    def calculate_total_type(self, tickets):
        #Calcula el total de ventas, ingresos y egresos
        total = {'cash': 0, 'transfer': 0, 'check': 0, 'account': 0}
        for ticket in tickets:
            total[PAYMENT_METHODS_DICT[ticket.payment_method]] += ticket.amount
        return total


    def charge_tickets(self):
        #Carga los tickets, calcula los totales y el saldo final
        sales = Sale.objects.filter(date=self.date)
        incomes = Payment.objects.filter(date=self.date, payment_type='I')
        expenses = Payment.objects.filter(date=self.date, payment_type='E')

        total_sales = self.calculate_total_type(sales)
        total_incomes = self.calculate_total_type(incomes)
        total_expenses = self.calculate_total_type(expenses)

        final_cash = self.initial_amounts['cash'] + total_sales['cash'] + total_incomes['cash'] - total_expenses['cash']
        final_transfer = self.initial_amounts['transfer'] + total_sales['transfer'] + total_incomes['transfer'] - total_expenses['transfer']
        final_check = self.initial_amounts['check'] + total_sales['check'] + total_incomes['check'] - total_expenses['check']

        return final_cash, final_transfer, final_check


    def calculate_differences(self, final_amounts):
        #Calcula las diferencias entre los montos finales y los montos esperados
        final_cash, final_transfer, final_check = self.charge_tickets()

        differences = {
            'cash': final_amounts['cash'] - final_cash,
            'transfer': final_amounts['transfer'] - final_transfer,
            'check': final_amounts['check'] - final_check,
        }
        return differences


    def close_register(self, final_amounts):
        #Cierra la caja registradora
        self.final_amounts = final_amounts
        self.differences = self.calculate_differences(final_amounts)
        self.save()


#----------------[ TICKETS ]----------------
class NumTicket(models.Model):
    type = models.CharField(max_length=1, choices=TICKET_TYPE_CHOICES)
    year = models.PositiveIntegerField()
    number = models.PositiveIntegerField()
    code = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"{self.type}{self.year}-{self.number:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code

class Ticket(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_account = models.ForeignKey(CurrentAccount, on_delete=models.CASCADE, null=True, blank=True)
    user_created = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='tickets_created', null=True, blank=True)

    def __str__(self):
        return f'{self.date_time} — Monto: ${self.amount} — Cuenta: {self.current_account}'


class Sale(Ticket):
    ticket_code = models.OneToOneField(NumTicket, on_delete=models.CASCADE, null=True, blank=True)#quitar null y blank una vez reseteada la base de datos
    temporal_name = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='PE')
    payment_method = models.CharField(max_length=2, choices=PAYMENT_METHODS_CHOICES, null=True, blank=True)

    def calculate_total(self):
        total = sum(item.price * item.quantity for item in self.items.all())
        self.amount = total
        self.save()
        return total


class Purchase(Ticket):
    temporal_name = models.CharField(max_length=100, null=True, blank=True)

class Payment(Ticket):
    payment_method = models.CharField(max_length=2, choices=PAYMENT_METHODS_CHOICES, null=True, blank=True)
    payment_type = models.CharField(max_length=2, choices=[('I', 'Income'), ('E', 'Expense')], default='S')


#----------------[ ITEM ]----------------

class Item(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE, null=True, blank=True)
    purchase = models.ForeignKey(Purchase, related_name='items', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name_cache = models.CharField(max_length=100, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'{self.quantity} — {self.product_name_cache} - ${self.price} = ${self.subtotal}'
    
    def calculate_subtotal(self):
        self.subtotal = self.price * self.quantity
        return self.subtotal

    def save(self, *args, **kwargs):
        if not self.product_name_cache:
            self.product_name_cache = self.product.name
        self.calculate_subtotal()
        super().save(*args, **kwargs)
