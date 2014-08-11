from accounting.models import Client, ColdWaterReading, ColdWaterVolume, ColdWaterTariff, RealEstate, Period
import datetime
from django.db.models import Sum

def get_all_clients():
    return Client.objects.all()

def how_many_periods_was_from(date):
    """Сколько отчетных периодов прошло с указанной даты.
    today
    """
    return 6

how_many_periods_was_from(datetime.date.today())

#from accounting.models import Client, ColdWaterReading, ColdWaterValue, RealEstate
#import datetime
#from django.db.models import Sum
#client = Client.objects.all().last()
def write_of_cold_water_service(client):
    """Списание средств за холодную воду.

    В ColdWaterReading за один отчетный период хранится только одно показание.
    Как быть в случае, когда установлен счетчик с ненулевым показанием? Ведь
    тогда откуда брать показание, оно будет явно описано в данных, а не будет
    хардкода в алгоритме.
    """
    use_norms = False
    
    #last_six_periods = (None, last_periods)[last_periods.count() == 3]#TODO:
    setup_date = client.real_estate.cold_water_counter_setup_date
    if setup_date:
        periods_with_counter = Period.objects.order_by('start').filter(start__gte=setup_date)
        count = periods_with_counter.count()
    counter_exists = setup_date is not None
    if counter_exists and count >= 3:
        readings = ColdWaterReading.objects.filter(real_estate=client.real_estate).order_by('date')
        last_reading = readings.last()
        was_reading_in_last_period = how_many_periods_was_from(last_reading.date) == 1
        if was_reading_in_last_period:
            next_to_last_reading = readings[readings.count()-2]
            volume = last_reading.value - next_to_last_reading.value
            volume_model = ColdWaterVolume(real_estate=client.real_estate, volume=volume, date=datetime.date.today())
            volume_model.save()
            #if last_reading.period.number - next_to_last_reading.period.number > 1:
            if (last_reading.date - next_to_last_reading.date).days > 30:
                #TODO: Необходимо вычислять даты :(
                #В ColdWaterVolume может быть несколько объемов по одной дате,
                #потому что необходимо учитывать еще и перерасчеты. Но
                #перерасчетов не будет в периоды не подтвержденные счетчиками.
                #Поэтому мы можем спокойно использовать выборку из базы на
                #основании дат и быть уверены что в них присутствуют объемы,
                #вычисленные по норме.
                recalculated_value = ColdWaterVolume.objects.order_by('date').filter(real_estate=client.real_estate, date__range=(next_to_last_reading.date, last_reading.date)).aggregate(Sum('value'))['value__sum']
                cold_water_value = ColdWaterVolume(real_estate=client.real_estate, value=recalculated_value, date=datetime.date.today())
                cold_water_value.save()
                tariff = ColdWaterTariff.objects.filter(client=client).last()
                client.amount = client.amount + recalculated_value * tariff.value
                client.save()
        date_3_months_ago = datetime.date.today() - datetime.timedelta(3*365/12)
        was_reading_in_3_last_months = readings.filter(date__gte=date_3_months_ago).count() > 0
        if was_reading_in_3_last_months:
            six_months_ago = datetime.date.today() - datetime.timedelta(6*365/12)
            value_sum = ColdWaterVolume.objects.order_by('date').filter(real_estate=client.real_estate, date__gte=six_months_ago).aggregate(Sum('value'))['value__sum']
            cold_water_value = ColdWaterVolume(real_estate=client.real_estate, value=value_sum/6, date=datetime.date.today())
            cold_water_value.save()
            #TODO: должна учитываться сумма в какой-то таблице.
            client.amount = client.amount + value_sum / 6 * tariff.value
            client.save()
        else:
            use_norms = True
    else:
        use_norms = True
    if use_norms and client.residential:
#        six_months_ago_values = ColdWaterVolume.objects.order_by('date').filter(real_estate=client.real_estate, date__gte=six_months_ago)
#        was_six_periods = six_months_ago_values.count() == 6
#        if was_six_periods:
#            value = six_months_ago_values.aggregate(Sum('value'))['value__sum']
#            cold_water_value = ColdWaterVolume(real_estate=client.real_estate, value=value, date=datetime.date.today())
#            cold_water_value.save()
#            #TODO: должна учитываться сумма в какой-то таблице.
#            client.amount = client.amount - value * tariff.value
#            client.save()
#        else:
#            #TODO: нужен флаг -- manual
#            cold_water_value = ColdWaterVolume(real_estate=client.real_estate, value=0, date=datetime.date.today())
#            cold_water_value.save()
        pass

def calculate_multiplicity():
    for apartment_building in RealEstate.objects.filter(apartment_building=True):
        real_estates = []
        for flat in RealEstate.objects.filter(parent=apartment_building):
            if flat.communal:
                for room in RealEstate.objects.filter(parent=flat):
                    real_estates.append(room)
            else:
                real_estates.append(flat)

        #TODO: тестовая дата. Изменить.
        today=datetime.date.today()
        date = datetime.date(year=today.year,month=1,day=25)

        value = ColdWaterVolume.objects.filter(real_estate__in=real_estates, date=date).aggregate(Sum('value'))['value__sum']
        #TODO: необходима таблица перерасчетов?
        recalculated_value = 0

def write_off():
    """Списание средств с клиентских счетов.

    Списание произодится раз в месяц 25 числа.
    """
    for client in Client.objects.all():
        is_cold_water_service = client.serviceclient_set.filter(
            service_name="Холодное водоснабжение").last()
        if is_cold_water_service:
            write_of_cold_water_service(client)
