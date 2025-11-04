from django import forms
from .models import Transaction, Category, RecurringTransaction, CreditCard, Account, Budget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field

# Formulario para crear nuevas Categorías
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ej: Comida, Sueldo'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False # Para que funcione en el Modal
        self.helper.layout = Layout(
            Field('name', css_class='form-control')
        )

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
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}), 
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
            self.fields['tarjeta_usada'].queryset = CreditCard.objects.filter(user=user)
            self.fields['cuenta'].queryset = Account.objects.filter(user=user)

        self.helper = FormHelper()
        self.helper.form_tag = False # Para que funcione en el Modal
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            Row( 
                Column(Field('type', css_class='form-select'), css_class='col-md-6'),
                Column(Field('cuenta', css_class='form-select'), css_class='col-md-6'),
            ), 
            Row(
                Column(Field('amount', css_class='form-control'), css_class='col-md-6'),
                Column(Field('category', css_class='form-select'), css_class='col-md-6'),
            ),
            Field('description', css_class='form-control'), 
            Row(
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
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(Field('type', css_class='form-select'), css_class='col-md-6'),
                Column(Field('amount', css_class='form-control'), css_class='col-md-6')
            ),
            Field('description', css_class='form-control'),
            Field('category', css_class='form-select'),
            Row(
                Column(Field('frequency', css_class='form-select'), css_class='col-md-6'),
                Column(Field('start_date', css_class='form-control'), css_class='col-md-6')
            ),
            Field('end_date', css_class='form-control')
        )

# Formulario para Tarjetas de Crédito
class CreditCardForm(forms.ModelForm):
    class Meta:
        model = CreditCard
        fields = ['name', 'closing_date', 'due_date']
        labels = {
            'name': 'Nombre de la Tarjeta',
            'closing_date': 'Día de Cierre (Ej: 25)',
            'due_date': 'Día de Vencimiento (Ej: 10)',
        }
        widgets = {
            'closing_date': forms.NumberInput(attrs={'min': 1, 'max': 31}),
            'due_date': forms.NumberInput(attrs={'min': 1, 'max': 31}),
            'name': forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name', css_class='form-control'),
            Row(
                Column(Field('closing_date', css_class='form-control'), css_class='col-md-6'),
                Column(Field('due_date', css_class='form-control'), css_class='col-md-6')
            )
        )
        
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
            'name': forms.TextInput(),
            'balance': forms.NumberInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name', css_class='form-control'),
            Field('balance', css_class='form-control')
        )
        
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
            'category': forms.Select(),
            'amount': forms.NumberInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('category', css_class='form-select'),
            Field('amount', css_class='form-control')
        )