from django.db import models
from django.contrib.auth.models import User

# Modelo para las Categorías de Gastos
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Modelo para las Transacciones (Ingresos y Gastos)
class Transaction(models.Model):
    TYPE_CHOICES = (
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return f"{self.type} de {self.amount} - {self.user.username}"

# Modelo para Ingresos/Gastos Fijos
class RecurringTransaction(models.Model):
    TYPE_CHOICES = (
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    )
    FREQUENCY_CHOICES = (
        ('mensual', 'Mensual'),
        ('semanal', 'Semanal'),
        # Podrías agregar más (diario, anual, etc.)
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='mensual')
    start_date = models.DateField()
    # end_date es opcional, por si es un gasto fijo que termina
    end_date = models.DateField(null=True, blank=True) 

    def __str__(self):
        return f"Fijo: {self.description} ({self.amount})"

# Modelo para las Tarjetas de Crédito (resumen de pago)
class CreditCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100) # Ej: "Visa Banco X", "Mastercard Banco Y"
    due_date = models.IntegerField() # Día del mes del vencimiento (ej: 10)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Cuánto tenés que pagar

    def __str__(self):
        return self.name