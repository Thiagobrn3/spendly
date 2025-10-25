from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404 # Para eliminar
# Importamos los nuevos modelos y formularios
from .models import Transaction, Category, RecurringTransaction, CreditCard
from .forms import TransactionForm, CategoryForm, RecurringTransactionForm, CreditCardForm

# Importamos los modelos y los nuevos formularios
from .models import Transaction, Category
from .forms import TransactionForm, CategoryForm
from django.db.models import Sum # Para sumar en la base de datos
import datetime # Para saber el mes actual

# Vista Basada en Clase para el Registro (esta queda igual)
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


# --- Nuestra Vista de Dashboard (Index) ---
@login_required
def index(request):

    # --- LÓGICA POST ---
    if request.method == 'POST':
        if 'submit_transaction' in request.POST:
            t_form = TransactionForm(request.POST, user=request.user)
            if t_form.is_valid():
                new_transaction = t_form.save(commit=False)
                new_transaction.user = request.user
                new_transaction.save()
                return redirect('index') 

        elif 'submit_category' in request.POST:
            c_form = CategoryForm(request.POST)
            if c_form.is_valid():
                new_category = c_form.save(commit=False)
                new_category.user = request.user
                new_category.save()
                return redirect('index')

    # --- LÓGICA GET

    # Obtenemos el mes actual
    today = datetime.date.today()
    first_day_of_month = today.replace(day=1)

    # Instanciamos los formularios vacíos
    t_form = TransactionForm(user=request.user)
    c_form = CategoryForm()

    # Obtenemos las categorías del usuario
    categories = Category.objects.filter(user=request.user)

    # Obtenemos las tarjetas del usuario
    cards = CreditCard.objects.filter(user=request.user)

    # Lista de Transacciones de este mes
    transactions = Transaction.objects.filter(
        user=request.user,
        date__gte=first_day_of_month 
    ).order_by('-date')

    # Total gastado este mes
    total_spent = Transaction.objects.filter(
        user=request.user,
        type='gasto',
        date__gte=first_day_of_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0.00

    # Datos del gráfico de este mes
    expense_data = Transaction.objects.filter(
        user=request.user,
        type='gasto',
        date__gte=first_day_of_month
    ).values('category__name').annotate(total=Sum('amount'))

    # Separamos los datos para JS
    chart_labels = []
    chart_data = []
    for item in expense_data:
        label = item['category__name'] if item['category__name'] else 'Sin Categoría'
        chart_labels.append(label)
        chart_data.append(float(item['total']))

    # Preparamos el 'contexto' para enviar al template
    context = {
        't_form': t_form,
        'c_form': c_form,
        'transactions': transactions,
        'categories': categories,
        'cards': cards, # <-- NUEVO
        'total_spent': total_spent,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }

    return render(request, 'tracker/index.html', context)

@login_required
def manage_recurring(request):
    if request.method == 'POST':
        form = RecurringTransactionForm(request.POST, user=request.user)
        if form.is_valid():
            recurring = form.save(commit=False)
            recurring.user = request.user
            recurring.save()
            return redirect('manage_recurring')

    form = RecurringTransactionForm(user=request.user)
    items = RecurringTransaction.objects.filter(user=request.user)
    context = {
        'form': form,
        'items': items,
    }
    return render(request, 'tracker/manage_recurring.html', context)

@login_required
def delete_recurring(request, pk):
    # Obtenemos el objeto, asegurándonos que pertenece al usuario
    item = get_object_or_404(RecurringTransaction, pk=pk, user=request.user)
    if request.method == 'POST':
        item.delete()
    return redirect('manage_recurring')

# --- Vista para Tarjetas de Crédito ---
@login_required
def manage_cards(request):
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
            return redirect('manage_cards')

    form = CreditCardForm()
    items = CreditCard.objects.filter(user=request.user)
    context = {
        'form': form,
        'items': items,
    }
    return render(request, 'tracker/manage_cards.html', context)

@login_required
def delete_card(request, pk):
    item = get_object_or_404(CreditCard, pk=pk, user=request.user)
    if request.method == 'POST':
        item.delete()
    return redirect('manage_cards')