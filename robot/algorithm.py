from accounting.models import Client, ColdWaterCounter, ColdWaterValue
import datetime
from django.db.models import Sum

def get_all_clients():
    return Client.objects.all()

#from accounting.models import Client, ColdWaterCounter, ColdWaterValue
#import datetime
#from django.db.models import Sum
#client = Client.objects.all().last()
def write_of_cold_water_service(client):
    use_norms = False
    setup_date = client.real_estate.cold_water_counter_setup_date
    days_in_6_months = 2 * 30
    if setup_date and (datetime.date.today() - setup_date).days > days_in_6_months:
        readings = ColdWaterCounter.objects.filter(real_estate=client.real_estate).order_by('date')
        last_reading = readings.last()
        was_reading_in_this_period = last_reading.date.month == datetime.date.today().month and\
            last_reading.date.year == datetime.date.today().year and\
            last_reading.date.day >= 20 and last_reading.date.day <= 25
        if was_reading_in_this_period:
            previous_reading = readings[readings.count()-2]
            value = last_reading.value - previous_reading.value
            cold_water_value = ColdWaterValue(real_estate=client.real_estate, value=value, date=datetime.date.today())
            cold_water_value.save()
            tariff = ColdWaterTariff.objects.filter(client=client).last()
            client.amount = client.amount - value * tariff.value
            client.save()
            if (last_reading.date - previous_reading.date).days > 30:
                #TODO: Необходимо вычислять даты :(
                recalculated_value = ColdWaterValue.objects.order_by('date').filter(real_estate=client.real_estate, date__range=(previous_reading.date, last_reading.date)).aggregate(Sum('value'))['value__sum']
                cold_water_value = ColdWaterValue(real_estate=client.real_estate, value=value, date=datetime.date.today())
                cold_water_value.save()
                client.amount = client.amount + recalculated_value * tariff.value
                client.save()
        date_3_months_ago = datetime.date.today() - datetime.timedelta(3*365/12)
        was_reading_in_3_last_months = readings.filter(date__gte=date_3_months_ago).count() > 0
        if was_reading_in_3_last_months:
            six_months_ago = datetime.date.today() - datetime.timedelta(6*365/12)
            value_sum = ColdWaterValue.objects.order_by('date').filter(real_estate=client.real_estate, date__gte=six_months_ago).aggregate(Sum('value'))['value__sum']
            cold_water_value = ColdWaterValue(real_estate=client.real_estate, value=value_sum/6, date=datetime.date.today())
            cold_water_value.save()
            #TODO: должна учитываться сумма в какой-то таблице.
            client.amount = client.amount + value_sum / 6 * tariff.value
            client.save()
        else:
            use_norms = True
    else:
        use_norms = True
    if use_norms and client.residential:
        six_months_ago_values = ColdWaterValue.objects.order_by('date').filter(real_estate=client.real_estate, date__gte=six_months_ago)
        was_six_periods = six_months_ago_values.count() == 6
        if was_six_periods:
            value = six_months_ago_values.aggregate(Sum('value'))['value__sum']
            cold_water_value = ColdWaterValue(real_estate=client.real_estate, value=value, date=datetime.date.today())
            cold_water_value.save()
            #TODO: должна учитываться сумма в какой-то таблице.
            client.amount = client.amount - value * tariff.value
            client.save()
        else:
            #TODO: нужен флаг -- manual
            cold_water_value = ColdWaterValue(real_estate=client.real_estate, value=0, date=datetime.date.today())
            cold_water_value.save()

def write_off():
    """Списание средств с клиентских счетов.

    Списание произодится раз в месяц 25 числа.
    """
    for client in Client.objects.all():
        is_cold_water_service = client.serviceclient_set.filter(
            service_name="Холодное водоснабжение").last()
        if is_cold_water_service:
            write_of_cold_water_service(client)
