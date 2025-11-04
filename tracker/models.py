from django.db import models
from django.contrib.auth.models import User
# --- ¡Nuevos imports para la lógica de cálculo! ---
import datetime
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
# (Asegurate de tener 'pip install python-dateutil' ejecutado)

# Modelo para las Categorías de Gastos
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100) # Ej: "Banco", "Efectivo"
    # Saldo actual, se actualizará con cada transacción
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
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
    recurring_source = models.ForeignKey('RecurringTransaction', on_delete=models.SET_NULL, null=True, blank=True)
    tarjeta_usada = models.ForeignKey(
        'CreditCard', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='transactions' 
    )
    
    cuenta = models.ForeignKey(
        Account, 
        on_delete=models.PROTECT, # ¡Importante!
        null=True, # Lo hacemos nulo temporalmente para migraciones
        blank=True # Lo haremos requerido en el form
    )

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
    
    closing_date = models.IntegerField(default=1) # Día del mes del CIERRE (ej: 25)
    due_date = models.IntegerField() # Día del mes del vencimiento (ej: 10)
    
    # 'balance_due' fue eliminado de la base de datos

    def __str__(self):
        return self.name

    # --- ¡LÓGICA DE CÁLCULO! ---
    @property
    def get_balance_due(self):
        """
        Calcula el saldo a pagar en el próximo vencimiento.
        Busca el último resumen cerrado.
        """
        
        # --- ¡ESTA ES LA LÍNEA QUE FALTABA! ---
        # El error "name 'today' is not defined" significa que
        # esta línea fue omitida.
        today = datetime.date.today()
        
        # 1. Encontrar la fecha del último cierre
        # Si hoy es 4/Nov y el cierre es el 25, el último cierre fue el 25/Oct.
        # Si hoy es 28/Nov y el cierre es el 25, el último cierre fue el 25/Nov.
        if today.day <= self.closing_date:
            # El cierre de este mes aún no pasó. Buscamos el del mes pasado.
            last_closing_date = today.replace(day=self.closing_date) - relativedelta(months=1)
        else:
            # El cierre de este mes ya pasó.
            last_closing_date = today.replace(day=self.closing_date)
            
        # 2. Encontrar la fecha del cierre anterior a ese
        previous_closing_date = last_closing_date - relativedelta(months=1)

        # 3. Sumar todas las transacciones (gastos) entre esas dos fechas
        balance = self.transactions.filter(
            date__gt=previous_closing_date, # Mayor que (excluye)
            date__lte=last_closing_date,   # Menor o igual que (incluye)
            type='gasto'
        ).aggregate(Sum('amount'))['amount__sum'] or 0.00
        
        return balance
class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # El presupuesto está vinculado directamente a una categoría
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # El monto límite (ej: 20000)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # (Para esta primera versión, asumimos que todos los presupuestos son mensuales)

    def __str__(self):
        return f"Presupuesto de {self.category.name} - {self.user.username}"

    class Meta:
        # Esto evita que un usuario cree dos presupuestos para la misma categoría
        unique_together = ('user', 'category')