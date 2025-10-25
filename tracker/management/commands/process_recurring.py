from django.core.management.base import BaseCommand
from django.db.models import Q
from tracker.models import RecurringTransaction, Transaction
import datetime

class Command(BaseCommand):
    help = 'Procesa las transacciones recurrentes y crea las transacciones correspondientes.'

    def handle(self, *args, **kwargs):
        today = datetime.date.today()
        self.stdout.write(f"Iniciando proceso de transacciones recurrentes para {today}...")
        
        created_count = 0
        
        # 1. Buscamos todos los items recurrentes que estén activos
        # (Que hayan empezado hoy o antes)
        # (Y que no tengan fecha de fin, o que la fecha de fin sea hoy o en el futuro)
        active_items = RecurringTransaction.objects.filter(
            start_date__lte=today
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today)
        )

        for item in active_items:
            is_due_today = False
            
            # 2. Verificamos si vence hoy según la frecuencia
            if item.frequency == 'mensual':
                # Si el día del mes de la fecha de inicio es igual al día de hoy
                if item.start_date.day == today.day:
                    is_due_today = True
            
            elif item.frequency == 'semanal':
                # Si el día de la semana de inicio es igual al de hoy
                # (0=Lunes, 1=Martes, ..., 6=Domingo)
                if item.start_date.weekday() == today.weekday():
                    is_due_today = True
            
            # (Aquí podrías agregar 'diario', 'anual', etc. si quisieras)

            # 3. Si no vence hoy, pasamos al siguiente
            if not is_due_today:
                continue

            # 4. ¡Vence hoy! Verificamos que no la hayamos creado ya
            already_exists = Transaction.objects.filter(
                recurring_source=item,
                date=today
            ).exists()

            if not already_exists:
                # 5. No existe, la creamos
                Transaction.objects.create(
                    user=item.user,
                    type=item.type,
                    amount=item.amount,
                    category=item.category,
                    description=item.description, # Usamos la misma descripción
                    date=today,
                    recurring_source=item # ¡La vinculamos!
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  -> Creada transacción para '{item.description}' del usuario {item.user.username}"))
            else:
                self.stdout.write(self.style.WARNING(f"  -> Ya existía transacción para '{item.description}' del usuario {item.user.username}"))

        self.stdout.write(self.style.SUCCESS(f"¡Proceso completado! Se crearon {created_count} nuevas transacciones."))