from django.core.management.base import BaseCommand
from django.utils import timezone
from main.models import Order
import pytz


class Command(BaseCommand):
    help = 'Обновляет статусы заказов по дате доставки (с учётом таймзоны клиента)'

    def handle(self, *args, **options):
        now_utc = timezone.now()
        updated = 0
        skipped = 0

        orders = Order.objects.filter(
            status=Order.STATUS_NEW,
            delivery_date__isnull=False,
        ).select_related('client')

        for order in orders:
            tz_name = order.client.timezone or 'UTC'

            try:
                tz = pytz.timezone(tz_name)
            except pytz.UnknownTimeZoneError:
                self.stdout.write(
                    self.style.WARNING(
                        f'Заказ #{order.id}: неизвестная таймзона "{tz_name}", '
                        f'использую UTC'
                    )
                )
                tz = pytz.UTC

            today_in_client_tz = now_utc.astimezone(tz).date()

            if order.delivery_date <= today_in_client_tz:
                order.status = Order.STATUS_DELIVERED
                order.save(update_fields=['status'])
                updated += 1
                self.stdout.write(
                    f'Заказ #{order.id} ({order.client.company_name}) → Доставлен '
                    f'(delivery_date={order.delivery_date}, '
                    f'today={today_in_client_tz} в {tz_name})'
                )
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Обновлено заказов: {updated}, пропущено: {skipped}'
            )
        )