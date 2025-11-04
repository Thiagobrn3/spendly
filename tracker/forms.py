from django import forms
from .models import Transaction, Category
from .models import RecurringTransaction, CreditCard
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field
from .models import Transaction, Category, RecurringTransaction, CreditCard, Account, Budget

# Formulario para crear nuevas Categorías
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ej: Comida, Sueldo'}),
        }

# Formulario para crear nuevas Transacciones
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ['user', 'recurring_source'] 
        
        labels = {
            'type': 'Tipo',
            'amount': 'Monto',
            'category': 'Categoría',
            'description': 'Descripción',
            'date': 'Fecha',
            'tarjeta_usada': 'Usando Tarjeta (Opcional)',
            'cuenta': 'Cuenta', 
        }
        
        # Este widget de 'date' es el único que realmente 
        # necesitamos definir acá.
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date'}
            ), 
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
            self.fields['tarjeta_usada'].queryset = CreditCard.objects.filter(user=user)
            self.fields['cuenta'].queryset = Account.objects.filter(user=user)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # --- ESTE ES EL ÚNICO LAYOUT QUE NECESITÁS ---
        # Este layout usa 'Field' para aplicar las clases CSS 
        # que tus estilos de base.html esperan.
        self.helper.layout = Layout(
            Row( 
                # Forzamos la clase 'form-select'
                Column(Field('type', css_class='form-select'), css_class='col-md-6'),
                Column(Field('cuenta', css_class='form-select'), css_class='col-md-6'),
            ), 
            Row(
                # Forzamos la clase 'form-control'
                Column(Field('amount', css_class='form-control'), css_class='col-md-6'),
                Column(Field('category', css_class='form-select'), css_class='col-md-6'),
            ),
            # Forzamos la clase 'form-control'
            Field('description', css_class='form-control'), 
            Row(
                # Forzamos 'form-control' y usamos el widget de 'date'
                Column(Field('date', css_class='form-control'), css_class='col-md-6'),
                Column(Field('tarjeta_usada', css_class='form-select'), css_class='col-md-6'),
            ),
        )

# Formulario para Gastos/Ingresos Fijos
class RecurringTransactionForm(forms.ModelForm):
    class Meta:
        model = RecurringTransaction
        exclude = ['user']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            # Aplicamos las clases de Bootstrap 5 aquí también
            'type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)

# Formulario para Tarjetas de Crédito
class CreditCardForm(forms.ModelForm):
    class Meta:
        model = CreditCard
        # Quitamos 'balance_due' y agregamos 'closing_date'
        fields = ['name', 'closing_date', 'due_date']
        
        # Agregamos etiquetas y widgets para los campos nuevos/modificados
        labels = {
            'name': 'Nombre de la Tarjeta',
            'closing_date': 'Día de Cierre (Ej: 25)',
            'due_date': 'Día de Vencimiento (Ej: 10)',
        }
        widgets = {
            'closing_date': forms.NumberInput(attrs={'min': 1, 'max': 31, 'class': 'form-control'}),
            'due_date': forms.NumberInput(attrs={'min': 1, 'max': 31, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
# --- FORMULARIO DE CUENTAS ---
class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'balance']
        labels = {
            'name': 'Nombre de la Cuenta (Ej: Banco, Efectivo)',
            'balance': 'Saldo Inicial',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
# --- FORMULARIO DE PRESUPUESTOS ---
class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount']
        labels = {
            'category': 'Categoría',
            'amount': 'Monto Límite Mensual',
        }
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Obtenemos el usuario de los argumentos de la vista
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filtramos el dropdown para que solo muestre las categorías de este usuario
            self.fields['category'].queryset = Category.objects.filter(user=user)