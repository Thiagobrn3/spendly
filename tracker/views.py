from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404 # Para eliminar
from .models import Transaction, Category, RecurringTransaction, CreditCard, Account, Budget
from .forms import TransactionForm, CategoryForm, RecurringTransactionForm, CreditCardForm, AccountForm, BudgetForm

# Importamos los modelos y los nuevos formularios
from .models import Transaction, Category
from .forms import TransactionForm, CategoryForm
from django.db.models import Sum # Para sumar en la base de datos
import datetime # Para saber el mes actual
from decimal import Decimal
# Para manejar errores (ej. si crea un presupuesto duplicado)
from django.db import IntegrityError
from django.contrib import messages
from django.db.models import Sum # Para sumar en la base de datos
from django.db.models import F
import datetime # Para saber el mes actual
from django.db.models import Sum, F, Q
from django.db.models.functions import TruncMonth
import datetime


# Vista Basada en Clase para el Registro
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


# --- Vista de Dashboard (Index) - SÓLO GET ---
@login_required
def index(request):

    # --- LÓGICA DE FILTRO DE FECHAS (queda igual) ---
    periodo = request.GET.get('periodo', 'este_mes')
    today = datetime.date.today()
    
    if periodo == 'mes_pasado':
        # ... (lógica de mes_pasado) ...
        first_day_current_month = today.replace(day=1)
        last_day_last_month = first_day_current_month - datetime.timedelta(days=1)
        start_date = last_day_last_month.replace(day=1)
        end_date = last_day_last_month
        
        date_filter_query = {
            'date__gte': start_date,
            'date__lte': end_date
        }
    elif periodo == 'este_ano':
        # ... (lógica de este_ano) ...
        start_date = today.replace(month=1, day=1)
        date_filter_query = {
            'date__gte': start_date
        }
    else: 
        # ... (lógica de este_mes) ...
        periodo = 'este_mes'
        start_date = today.replace(day=1)
        date_filter_query = {
            'date__gte': start_date
        }

    # --- LÓGICA GET ---

    # Instanciamos los formularios (los modals los necesitarán)
    t_form = TransactionForm(user=request.user)
    c_form = CategoryForm()

    # --- QUERIES PRINCIPALES ---
    categories = Category.objects.filter(user=request.user)
    cards = CreditCard.objects.filter(user=request.user)
    accounts = Account.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(
        user=request.user,
        **date_filter_query 
    ).order_by('-date')

    # --- CÁLCULOS PARA EL DASHBOARD ---

    # 1. Total Gastado (para el filtro actual)
    total_spent = transactions.filter(type='gasto').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # 2. Total Ganado (para el filtro actual)
    total_earned = transactions.filter(type='ingreso').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # 3. Balance del período (ej. +$352.40 este mes)
    net_change = total_earned - total_spent

    # 4. Saldo Total Disponible (Suma de todas las cuentas)
    total_balance = accounts.aggregate(Sum('balance'))['balance__sum'] or 0.00

    # 5. Datos del Gráfico (basado en total_spent)
    expense_data = transactions.filter(type='gasto').values('category__name').annotate(total=Sum('amount'))
    chart_labels = []
    chart_data = []
    for item in expense_data:
        label = item['category__name'] if item['category__name'] else 'Sin Categoría'
        chart_labels.append(label)
        chart_data.append(float(item['total']))

    # 6. Progreso de Presupuestos
    budgets = Budget.objects.filter(user=request.user).select_related('category')
    budgets_progress = []
    gastos_por_categoria = {
        item['category__name']: item['total'] 
        for item in expense_data 
        if item['category__name']
    }
    for budget in budgets:
        spent = gastos_por_categoria.get(budget.category.name, Decimal('0.00'))
        percentage = 0
        if budget.amount > 0:
            percentage = (spent / budget.amount) * 100
        budgets_progress.append({
            'category_name': budget.category.name,
            'limit': budget.amount,
            'spent': spent,
            'percentage': min(percentage, 100), 
            'over_limit': spent > budget.amount,
        })
    # --- FIN DE CÁLCULOS ---

    context = {
        't_form': t_form,
        'c_form': c_form,
        'transactions': transactions,
        'categories': categories,
        'cards': cards,
        'accounts': accounts, 
        'total_spent': total_spent,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'selected_periodo': periodo,
        'budgets_progress': budgets_progress,
        
        # ¡Nuevos valores para el layout!
        'total_balance': total_balance,
        'net_change': net_change,
    }

    return render(request, 'tracker/index.html', context)
# --- Lista de transacciones ---
@login_required
def transaction_list(request):
    # Obtenemos todas las transacciones del usuario
    # Usamos select_related para optimizar y traer los datos de
    # categoría y cuenta en la misma consulta
    transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('category', 'cuenta').order_by('-date')

    context = {
        'transactions': transactions
    }
    return render(request, 'tracker/transaction_list.html', context)
# --- Agregar Transacción ---
@login_required
@require_POST 
def add_transaction(request):
    t_form = TransactionForm(request.POST, user=request.user)
    if t_form.is_valid():
        new_transaction = t_form.save(commit=False)
        new_transaction.user = request.user
        
        cuenta = new_transaction.cuenta
        amount = new_transaction.amount

        if new_transaction.type == 'ingreso':
            cuenta.balance = F('balance') + amount
        elif new_transaction.type == 'gasto':
            cuenta.balance = F('balance') - amount
            
        cuenta.save()
        new_transaction.save()
    
    return redirect('index')

# --- Agregar Categoría ---
@login_required
@require_POST # Esta vista solo acepta peticiones POST
def add_category(request):
    c_form = CategoryForm(request.POST)
    if c_form.is_valid():
        new_category = c_form.save(commit=False)
        new_category.user = request.user
        new_category.save()
    return redirect('index')

# --- ELiminar categoria ---
@login_required
@require_POST
def category_delete(request, pk):
    # Obtenemos la categoría, asegurándonos de que pertenece al usuario
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    # La eliminamos
    category.delete()
    
    # Redirigimos al dashboard
    return redirect('index')

# --- Editar Transacción ---
@login_required
def transaction_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    old_amount = transaction.amount
    old_type = transaction.type
    old_cuenta = transaction.cuenta
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            
            # 1. Revertimos el valor antiguo (¡SOLO SI HABÍA UNA CUENTA!)
            if old_cuenta:
                if old_type == 'ingreso':
                    old_cuenta.balance = F('balance') - old_amount
                elif old_type == 'gasto':
                    old_cuenta.balance = F('balance') + old_amount
                old_cuenta.save()

            # 2. Aplicamos el valor nuevo
            new_transaction = form.save(commit=False)
            new_cuenta = new_transaction.cuenta
            new_amount = new_transaction.amount
            
            # (La nueva transacción SIEMPRE tendrá una cuenta gracias al form)
            if new_transaction.type == 'ingreso':
                new_cuenta.balance = F('balance') + new_amount
            elif new_transaction.type == 'gasto':
                new_cuenta.balance = F('balance') - new_amount
                
            new_cuenta.save()
            new_transaction.save() 

            return redirect('index') 
    else:
        form = TransactionForm(instance=transaction, user=request.user)
        
    context = {
        'form': form,
        'transaction': transaction
    }
    return render(request, 'tracker/transaction_form.html', context)
# --- Eliminar Transacción ---
@login_required
@require_POST 
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    cuenta = transaction.cuenta
    amount = transaction.amount
    if cuenta:
        if transaction.type == 'ingreso':
            cuenta.balance = F('balance') - amount
        elif transaction.type == 'gasto':
            cuenta.balance = F('balance') + amount
        cuenta.save()
    
    transaction.delete()
    
    return redirect('index')@login_required
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
        # Instanciamos el form con los datos del POST
        form = CreditCardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user # Asignamos el usuario
            card.save()
            return redirect('manage_cards')

    form = CreditCardForm() # Instancia vacía para GET
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

# --- VISTA PARA CUENTAS ---
@login_required
def manage_accounts(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            return redirect('manage_accounts')

    form = AccountForm()
    accounts = Account.objects.filter(user=request.user)
    context = {
        'form': form,
        'accounts': accounts,
    }
    return render(request, 'tracker/manage_accounts.html', context)

@login_required
def delete_account(request, pk):
    account = get_object_or_404(Account, pk=pk, user=request.user)
    
    # Verificamos si la cuenta tiene transacciones
    if account.transaction_set.exists():
        # (Aquí podríamos redirigir con un mensaje de error)
        # Por ahora, simplemente no la borramos si tiene transacciones
        pass
    else:
        if request.method == 'POST':
            account.delete()
            
    return redirect('manage_accounts')

@login_required
def manage_budgets(request):
    if request.method == 'POST':
        # Pasamos el 'user' al formulario para que filtre las categorías
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                budget = form.save(commit=False)
                budget.user = request.user
                budget.save()
                return redirect('manage_budgets')
            except IntegrityError:
                # Esto se activa si el usuario crea un presupuesto para una categoría
                # que ya tiene uno (gracias al 'unique_together' en el modelo)
                messages.error(request, 'Error: Ya existe un presupuesto para esa categoría.')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')

    # Lógica para GET (mostrar la página)
    form = BudgetForm(user=request.user)
    budgets = Budget.objects.filter(user=request.user).select_related('category')
    
    context = {
        'form': form,
        'budgets': budgets,
    }
    return render(request, 'tracker/manage_budgets.html', context)

@login_required
@require_POST # Solo permitimos borrar vía POST
def delete_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    budget.delete()
    return redirect('manage_budgets')

# --- VISTA DE REPORTES ---
@login_required
def reports(request):
    today = datetime.date.today()
    
    # Filtramos las transacciones de este año
    transactions_this_year = Transaction.objects.filter(
        user=request.user,
        date__year=today.year
    )
    
    # Agrupamos por mes y sumamos ingresos y gastos
    report_data = transactions_this_year \
        .annotate(month=TruncMonth('date')) \
        .values('month') \
        .annotate(
            total_ingreso=Sum('amount', filter=Q(type='ingreso')),
            total_gasto=Sum('amount', filter=Q(type='gasto'))
        ) \
        .order_by('month')

    # Preparamos los datos para Chart.js
    
    # Creamos un "mapa" con todos los meses en 0
    month_map = {i: {'ingreso': 0, 'gasto': 0} for i in range(1, 13)}
    
    # Llenamos el mapa con los datos de la consulta
    for item in report_data:
        if item['month']: # Nos aseguramos de que no sea nulo
            month_num = item['month'].month
            month_map[month_num]['ingreso'] = item['total_ingreso'] or 0
            month_map[month_num]['gasto'] = item['total_gasto'] or 0

    # Creamos las listas finales para el gráfico
    labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    chart_labels = []
    chart_ingresos = []
    chart_gastos = []

    for i in range(1, 13):
        # Solo mostramos los meses hasta el mes actual
        if i <= today.month:
            chart_labels.append(labels[i-1])
            chart_ingresos.append(float(month_map[i]['ingreso']))
            chart_gastos.append(float(month_map[i]['gasto']))

    context = {
        'chart_labels': chart_labels,
        'chart_ingresos': chart_ingresos,
        'chart_gastos': chart_gastos,
    }
    
    return render(request, 'tracker/reports.html', context)