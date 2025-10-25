from django import forms
from .models import Transaction, Category
from .models import RecurringTransaction, CreditCard
# ¡Quitamos las importaciones de crispy_forms que ya no usamos!

# Formulario para crear nuevas Categorías (queda igual)
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ej: Comida, Sueldo'}),
        }

# Formulario para crear nuevas Transacciones (MODIFICADO)
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ['user', 'recurring_source'] 
        
        # ETIQUETAS (labels)
        labels = {
            'type': 'Tipo',
            'amount': 'Monto',
            'category': 'Categoría',
            'description': 'Descripción',
            'date': 'Fecha',
        }
        
        # --- ¡AQUÍ ESTÁ LA SOLUCIÓN! ---
        # Definimos el widget y sus atributos HTML para cada campo
        widgets = {
            'type': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'amount': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),
            'category': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'description': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ), 
        }

    def __init__(self, *args, **kwargs):
        # Esta parte la dejamos como estaba, está perfecta
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
        
# --- (El resto de forms.py queda exactamente igual) ---

# Formulario para Gastos/Ingresos Fijos
class RecurringTransactionForm(forms.ModelForm):
    # ... (esta clase queda igual) ...
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

# Formulario para Tarjetas de Crédito
class CreditCardForm(forms.ModelForm):
    # ... (esta clase queda igual) ...
    class Meta:
        model = CreditCard
        exclude = ['user']
        widgets = {
            'due_date': forms.NumberInput(attrs={'min': 1, 'max': 31}),
        }