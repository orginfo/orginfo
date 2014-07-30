from accounting.models import Client, ColdWaterCounter
import datetime

def get_all_clients():
    return Client.objects.all()

def write_of_cold_water_service(client):
    setup_date = client.real_estate.cold_water_counter_setup_date
    days_in_6_months = 2 * 30
    if setup_date and (datetime.date.today() - setup_date).days > days_in_6_months:
        last_reading_date = ColdWaterCounter.objects.filter(real_estate=client.real_estate).order_by('date').last().date
        was_reading_in_this_period = last_reading_date.month == datetime.date.today().month and
            last_reading_date.year == datetime.date.today().year and
            last_reading_date.day >= 20 and last_reading_date.day <= 25
        if was_reading_in_this_period:
            pass

def write_off():
    """Списание средств с клиентских счетов.

    Списание произодится раз в месяц 25 числа.
    """
    for client in Client.objects.all():
        is_cold_water_service = client.serviceclient_set.filter(
            service_name="Холодное водоснабжение").last()
        if is_cold_water_service:
            write_of_cold_water_service(client)
