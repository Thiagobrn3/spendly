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

    # --- LÓGICA POST (esta parte queda igual) ---
    if request.method == 'POST':
        if 'submit_transaction' in request.POST:
            t_form = TransactionForm(request.POST, user=request.user)
            if t_form.is_valid():
                new_transaction = t_form.save(commit=False)
                new_transaction.user = request.user
                new_transaction.save()
                # Redirigimos a la misma URL (conservando los filtros GET si existen)
                return redirect(request.path_info + '?' + request.GET.urlencode())

        elif 'submit_category' in request.POST:
            c_form = CategoryForm(request.POST)
            if c_form.is_valid():
                new_category = c_form.save(commit=False)
                new_category.user = request.user
                new_category.save()
                return redirect(request.path_info + '?' + request.GET.urlencode())

    # --- LÓGICA GET (esta parte la actualizamos) ---

    # 1. Determinar el rango de fechas
    today = datetime.date.today()
    # Valores predeterminados: el mes actual
    default_start_date = today.replace(day=1)
    default_end_date = today 

    # 2. Leer las fechas del request.GET
    # Si no existen, usamos los valores predeterminados
    start_date_str = request.GET.get('start_date', default_start_date.strftime('%Y-%m-%d'))
    end_date_str = request.GET.get('end_date', default_end_date.strftime('%Y-%m-%d'))

    # 3. Convertir los strings de fecha a objetos 'date' para la base de datos
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        # Si el formato es inválido (ej. URL manipulada), volvemos a los defaults
        start_date = default_start_date
        end_date = default_end_date
        start_date_str = default_start_date.strftime('%Y-%m-%d')
        end_date_str = default_end_date.strftime('%Y-%m-%d')

    # Instanciamos los formularios vacíos
    t_form = TransactionForm(user=request.user)
    c_form = CategoryForm()

    # Obtenemos las categorías del usuario (esto no cambia)
    categories = Category.objects.filter(user=request.user)

    # --- ACTUALIZAMOS LAS CONSULTAS PARA USAR EL RANGO DE FECHAS ---

    # 1. Lista de Transacciones (filtrada por el rango)
    transactions = Transaction.objects.filter(
        user=request.user,
        date__gte=start_date, # >= Fecha Desde
        date__lte=end_date      # <= Fecha Hasta
    ).order_by('-date')

    # 2. Total gastado (filtrado por el rango)
    # (Renombramos la variable de 'total_spent_month' a 'total_spent')
    total_spent = Transaction.objects.filter(
        user=request.user,
        type='gasto',
        date__gte=start_date,
        date__lte=end_date
    ).aggregate(Sum('amount'))['amount__sum'] or 0.00

    # 3. Datos del gráfico (filtrados por el rango)
    expense_data = Transaction.objects.filter(
        user=request.user,
        type='gasto',
        date__gte=start_date,
        date__lte=end_date
    ).values('category__name').annotate(total=Sum('amount'))

    # 4. Separamos los datos para JS (esto queda igual)
    chart_labels = []
    chart_data = []
    for item in expense_data:
        label = item['category__name'] if item['category__name'] else 'Sin Categoría'
        chart_labels.append(label)
        chart_data.append(float(item['total']))

    # --------------------------------------------------

    # Preparamos el 'contexto' para enviar al template
    context = {
        't_form': t_form,
        'c_form': c_form,
        'transactions': transactions,
        'categories': categories,

        # Pasamos el nuevo total
        'total_spent': total_spent,
        'chart_labels': chart_labels,
        'chart_data': chart_data,

        # ¡Importante! Pasamos los strings de las fechas de vuelta
        # para que el formulario "recuerde" lo que el usuario filtró.
        'start_date_str': start_date_str,
        'end_date_str': end_date_str,
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