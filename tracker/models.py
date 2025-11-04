from django.db import models
from django.contrib.auth.models import User
import datetime
from django.db.models import Sum
from dateutil.relativedelta import relativedelta

# ===============================
# MODELO: Category
# ===============================
# Representa una categoría de gasto o ingreso, como "Comida", "Transporte", "Sueldo", etc.
# Cada usuario puede tener sus propias categorías personalizadas.
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario dueño
    name = models.CharField(max_length=100)  # Nombre de la categoría

    def __str__(self):
        return self.name


# ===============================
# MODELO: Account
# ===============================
# Representa una cuenta del usuario: puede ser una cuenta bancaria, efectivo, billetera virtual, etc.
# Se mantiene el saldo actual y se actualiza con cada transacción.
class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario dueño de la cuenta
    name = models.CharField(max_length=100)  # Ejemplo: "Banco Nación", "Efectivo", "Mercado Pago"
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Saldo actual

    def __str__(self):
        return self.name


# ===============================
# MODELO: Transaction
# ===============================
# Registra cada movimiento financiero: ingresos o gastos.
# Está vinculada a una categoría, una cuenta, y opcionalmente a una tarjeta de crédito.
class Transaction(models.Model):
    TYPE_CHOICES = (
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario que realizó la transacción
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)  # Determina si es ingreso o gasto
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Monto del movimiento
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)  # Categoría del movimiento
    description = models.CharField(max_length=255)  # Descripción libre del gasto/ingreso
    date = models.DateField()  # Fecha en que ocurrió la transacción

    # Si la transacción proviene de un gasto fijo (RecurringTransaction)
    recurring_source = models.ForeignKey(
        'RecurringTransaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Si se realizó con una tarjeta de crédito
    tarjeta_usada = models.ForeignKey(
        'CreditCard',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'  # Permite acceder desde la tarjeta a sus transacciones
    )

    # Cuenta desde la cual se registró el movimiento
    cuenta = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,  # Evita que se borre una cuenta con transacciones asociadas
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.type} de {self.amount} - {self.user.username}"


# ===============================
# MODELO: RecurringTransaction
# ===============================
# Define ingresos o gastos que se repiten automáticamente (mensual, semanal, etc.)
# Ejemplo: alquiler, sueldo, abono de internet.
class RecurringTransaction(models.Model):
    TYPE_CHOICES = (
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    )
    FREQUENCY_CHOICES = (
        ('mensual', 'Mensual'),
        ('semanal', 'Semanal'),
        # Se pueden agregar más frecuencias: diario, anual, etc.
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario dueño
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)  # Tipo de movimiento
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Monto fijo
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)  # Categoría del gasto
    description = models.CharField(max_length=255)  # Descripción del ingreso/gasto fijo
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='mensual')  # Frecuencia del movimiento
    start_date = models.DateField()  # Fecha de inicio
    end_date = models.DateField(null=True, blank=True)  # Fecha de fin (opcional)

    def __str__(self):
        return f"Fijo: {self.description} ({self.amount})"


# ===============================
# MODELO: CreditCard
# ===============================
# Representa una tarjeta de crédito y sus datos de resumen.
# Permite calcular el saldo a pagar según las transacciones realizadas entre cierres.
class CreditCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario dueño de la tarjeta
    name = models.CharField(max_length=100)  # Ejemplo: "Visa Santander", "Mastercard Galicia"
    
    closing_date = models.IntegerField(default=1)  # Día del mes en que cierra el resumen (ej: 25)
    due_date = models.IntegerField()  # Día del mes en que vence el pago (ej: 10)
    
    # Ya no se guarda el balance_due: se calcula dinámicamente

    def __str__(self):
        return self.name

    # --- Lógica de cálculo del saldo ---
    @property
    def get_balance_due(self):
        """
        Calcula el saldo a pagar en el próximo vencimiento.
        Busca el último resumen cerrado y suma los gastos hechos entre ese
        y el cierre anterior.
        """
        today = datetime.date.today()

        # 1. Determinar la fecha del último cierre
        # Ejemplo: si hoy es 4/Nov y el cierre es 25 → el último fue 25/Oct.
        if today.day <= self.closing_date:
            last_closing_date = today.replace(day=self.closing_date) - relativedelta(months=1)
        else:
            last_closing_date = today.replace(day=self.closing_date)
        
        # 2. Fecha del cierre anterior
        previous_closing_date = last_closing_date - relativedelta(months=1)

        # 3. Sumar los gastos hechos entre esos dos cierres
        balance = self.transactions.filter(
            date__gt=previous_closing_date,  # Mayor que (excluye la fecha anterior)
            date__lte=last_closing_date,     # Menor o igual que (incluye el cierre)
            type='gasto'
        ).aggregate(Sum('amount'))['amount__sum'] or 0.00
        
        return balance


# ===============================
# MODELO: Budget
# ===============================
# Permite establecer un presupuesto mensual por categoría.
# Por ejemplo: "Comida - $20.000" o "Entretenimiento - $10.000".
class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario al que pertenece
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Categoría asignada
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Monto límite mensual

    def __str__(self):
        return f"Presupuesto de {self.category.name} - {self.user.username}"

    class Meta:
        # Evita presupuestos duplicados en la misma categoría y usuario
        unique_together = ('user', 'category')
