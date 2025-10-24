from django import forms
from .models import Transaction, Category
from .models import RecurringTransaction, CreditCard

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
        # Excluimos 'user' porque lo asignaremos automáticamente
        exclude = ['user'] 
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}), # Un widget de calendario
        }

    def __init__(self, *args, **kwargs):
        # Sacamos el 'user' que le pasaremos desde la vista
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)

        # Esto es clave:
        # Filtramos el queryset del campo 'category' para que 
        # solo muestre las categorías creadas por el usuario logueado.
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
            
# Formulario para Gastos/Ingresos Fijos
class RecurringTransactionForm(forms.ModelForm):
    class Meta:
        model = RecurringTransaction
        exclude = ['user'] # Excluimos al usuario
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # Reutilizamos la misma lógica que en TransactionForm
        # para filtrar las categorías por usuario.
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)

# Formulario para Tarjetas de Crédito
class CreditCardForm(forms.ModelForm):
    class Meta:
        model = CreditCard
        exclude = ['user'] # Excluimos al usuario
        widgets = {
            'due_date': forms.NumberInput(attrs={'min': 1, 'max': 31}),
        }