from django import forms
from .models import Transaction, Category

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