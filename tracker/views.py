from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

# Importamos los modelos y los nuevos formularios
from .models import Transaction, Category
from .forms import TransactionForm, CategoryForm

# Vista Basada en Clase para el Registro (esta queda igual)
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


# --- Nuestra Vista de Dashboard (Index) ---
@login_required
def index(request):

    # Lógica para manejar el envío de formularios (POST)
    if request.method == 'POST':

        # Identificamos qué formulario se envió
        # Usaremos el 'name' del botón 'submit'

        if 'submit_transaction' in request.POST:
            # El usuario está agregando una Transacción
            t_form = TransactionForm(request.POST, user=request.user)
            if t_form.is_valid():
                # Guardamos el formulario pero sin 'commitear' a la DB
                new_transaction = t_form.save(commit=False)
                # Asignamos el usuario logueado
                new_transaction.user = request.user
                # Ahora sí, guardamos en la DB
                new_transaction.save()
                return redirect('index') # Redirigimos a la misma pág

        elif 'submit_category' in request.POST:
            # El usuario está agregando una Categoría
            c_form = CategoryForm(request.POST)
            if c_form.is_valid():
                new_category = c_form.save(commit=False)
                new_category.user = request.user
                new_category.save()
                return redirect('index')

    # Lógica para mostrar la página (GET)

    # Instanciamos los formularios vacíos para pasarlos al template
    # Recordá pasar el 'user' al TransactionForm
    t_form = TransactionForm(user=request.user)
    c_form = CategoryForm()

    # Obtenemos todas las transacciones del usuario, ordenadas por fecha
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    # Obtenemos las categorías del usuario
    categories = Category.objects.filter(user=request.user)

    # Preparamos el 'contexto' para enviar al template
    context = {
        't_form': t_form,
        'c_form': c_form,
        'transactions': transactions,
        'categories': categories,
    }

    return render(request, 'tracker/index.html', context)