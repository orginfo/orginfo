from accounting.models import ColdWaterReading, ColdWaterVolume, RealEstate, Period, ServiceClient, Animals
import datetime
from robot.errors import ForgottenInitialReadingError
from django.db.models import Sum
from django.db import transaction


def calculate_individual_cold_water_volume(real_estate, cold_water_norm, residential, residents):
    """Списание средств за холодную воду.

    В ColdWaterReading за один отчетный период хранится только одно показание.
    Как быть в случае, когда установлен счетчик с ненулевым показанием? Ведь
    тогда откуда брать показание, оно будет явно описано в данных, а не будет
    хардкода в алгоритме.
    """
    periods_with_counter = None
    setup_date = real_estate.cold_water_counter_setup_date
    if setup_date:
        periods_with_counter = Period.objects.order_by('start').filter(start__gte=setup_date)

    if periods_with_counter and periods_with_counter.count() >= 6:
        last_period_reading = periods_with_counter.last().coldwaterreading_set.filter(real_estate=real_estate).get()
        was_reading_in_last_period = last_period_reading is not None
        if was_reading_in_last_period:
            next_to_last_period_reading = None
            i = periods_with_counter.count() - 2
            while 0 <= i:
                readings = periods_with_counter[i].coldwaterreading_set.filter(real_estate=real_estate)
                if readings.count():
                    next_to_last_period_reading = readings.get()
                    break
                i = i - 1
            if next_to_last_period_reading is None:
                raise ForgottenInitialReadingError
            unconfirmed_reading_volumes = ColdWaterVolume.objects.filter(real_estate=real_estate, period__serial_number__in=range(last_period_reading.period.serial_number+1, next_to_last_period_reading.period.serial_number)).aggregate(Sum('volume'))['volume__sum'] or 0
            volume = last_period_reading.value - next_to_last_period_reading.value - unconfirmed_reading_volumes
            return volume

        second_from_the_end_period_reading = ColdWaterReading.objects.filter(real_estate=real_estate, period=periods_with_counter[periods_with_counter.count()-2]).last()
        third_from_the_end_period_reading = ColdWaterReading.objects.filter(real_estate=real_estate, period=periods_with_counter[periods_with_counter.count()-3]).last()
        was_reading_in_second_or_third_period_from_the_end = second_from_the_end_period_reading or third_from_the_end_period_reading
        if was_reading_in_second_or_third_period_from_the_end:
            last_six_volumes_sum = ColdWaterVolume.objects.filter(real_estate=real_estate, period__serial_number__in=range(periods_with_counter.last().serial_number-6+1, periods_with_counter.last().serial_number+1)).aggregate(Sum('volume'))['volume__sum']
            average_volume = last_six_volumes_sum/6
            return average_volume

    if residential:
        #Формула № 4а
        volume = residents * cold_water_norm
        return volume

    periods = Period.objects.order_by('start')
    start_period_index = periods.count()-6-1
    if start_period_index > 0:
        last_six_volumes_sum = ColdWaterVolume.objects.filter(real_estate=real_estate, period__serial_number__gte=periods[start_period_index].serial_number).aggregate(Sum('volume'))['volume__sum']
        average_volume = last_six_volumes_sum/6
        return average_volume

    return None #TODO: нужен флаг -- manual

def write_off():
    """Списание средств с клиентских счетов.

    Списание произодится раз в месяц 26 числа.
    #TODO: за один расчет для одного клиента может быть несколько записей ColdWaterVolume
    """
    try:
        with transaction.atomic():
            for building in RealEstate.objects.filter(type=RealEstate.BUILDING_TYPE):
                periods = Period.objects.order_by('start')
                #TODO: счетчик может отсутствовать
                last_period_reading = periods[periods.count()-1].coldwaterreading_set.filter(real_estate=building).get()
                next_to_last_period_reading = periods[periods.count()-2].coldwaterreading_set.filter(real_estate=building).get()
                cold_water_building_volume = last_period_reading.value - next_to_last_period_reading.value
        
                real_estates = []
                for real_estate in RealEstate.objects.filter(parent=building):
                    real_estates.append(real_estate)
        
                cold_water_volume_clients_sum = 0
                for real_estate in real_estates:
                    if real_estate.type != 'c':
                        client = real_estate.client_set.last()
                        #TODO: как вычислить is_cold_water_service с учетом start/end 
                        is_cold_water_service = client.serviceclient_set.filter(
                            service_name=ServiceClient.COLD_WATER_SERVICE).last()
                        if is_cold_water_service:
                            volume = calculate_individual_cold_water_volume(real_estate, client.type_water_norm.cold_water_norm, client.residential, client.residents)
                            volume_model = ColdWaterVolume(period=periods.last(), real_estate=real_estate, volume=volume, date=datetime.date.today())
                            volume_model.save()
        
                    else:
                        cold_water_norm = 1 #TODO: взять из самого верхнего real_estate.
                        residential = False #TODO: откуда взять этот параметр.
                        total_rooms_volume # Общий объем холодного водоснабжения для коммунальной квартиры/блока офисов/секции общещития.
                        residents = 10 #TODO: можно обсчитать.
                        total_rooms_volume = calculate_individual_cold_water_volume(real_estate, cold_water_norm, residential, residents)
                        
                        # flat_residents - общее количество проживающих в квартире
                        #TODO: У родительского помещения 'parent=real_estate' должа быть указана общая площадь. Создать поле 'area' в  'RealEstate'.
                        flat_residents = 0 #TODO: Подумать, может ли так же хранить для каждого помещения общее количество проживающих?
                        # В 'volume' будет добавлено суммарное количество объема всех комнат. Значение может отличаться от 'total_rooms_volume'. В этом случае, разница объемов будет учтена и рассчитана в расчет ОДН.
                        # Вычисляем общее количество проживающих в помещении (блоке, коммунальной квартире и т.д.)
                        #TODO: Заменить блок вычислений на запрос - агрегацию суммы зарегестрированных в каждом помещении для объектов с 'parent=real_estate'.
                        for room in RealEstate.objects.filter(parent=real_estate):
                            flat_residents = flat_residents + flat_residents.client.residents
        
                        #Вычисляем необходимые объемы для каждого помещения.
                        for room in RealEstate.objects.filter(parent=real_estate):
                            # Вычисляем долю 'комнаты ко всей квартире', в зависимости от типа помещения:
                            # жилое помещение   - тогда количество проживающих в комнате к общему количеству проживающих в квартире;
                            # нежилое помещение - тогда площать комнаты к общей площади квартиры.
                            # proportion - доля комнаты к общей квартире
                            proportion = 1
                            if room.residential:
                                proportion = room.client.residents / flat_residents
                            else:
                                #Вычисление доли по площади.
                                #TODO: Внести в 'RealEstate' поле 'area'.
                                proportion = room.area / real_estate.area
        
                            room_volume = proportion * total_rooms_volume
                            volume_model = ColdWaterVolume(period=periods.last(), real_estate=real_estate, volume=room_volume, date=datetime.date.today())
                            volume_model.save()
                            
                            volume = volume + room_volume;
        
                    # Суммируем объемы помещений. Если квартира коммунальная (или блок общещия, или блок с офисами), тогда используем сумму объемов всех внутренних помещений клиентов.
                    cold_water_volume_clients_sum = cold_water_volume_clients_sum + volume
        
                #расчет общедомовых нужд. Доля объма на помещение определяется от соотношения площади помещения к общей площади всех жилых и нежилых помещений.
                # building_area - общая площадь всех жилых помещений (квартир) и нежилых помещений в многоквартирном доме.
                # TODO: Здание должно иметь параметр area.
                volume = cold_water_building_volume - cold_water_volume_clients_sum
                if volume != 0:
                    for real_estate in real_estates:
                        if real_estate.type != 'c':
                            real_estate_volume = real_estate.area / building.area * volume
                            #TODO: Общедомовые нужды(ОДН) должны храниться в отдельной таблице, так как эти данные будут использоваться при перерасчетах.
                            cold_water_volume = ColdWaterVolume(real_estate=real_estate, volume=volume, date=datetime.date.today())
                            cold_water_volume.save()
                        else:
                            # Вычисляем объем для всей квартиры/блока/секции
                            real_estate_volume = real_estate.area / building.area * volume
                            # Распределяем общий объем между внутренними помещениями клиентов.
                            # TODO: Полагаю, что для распределения требуется не общая площадь квартиры/блока/секции, а общая площадь помещений клиентов. Либо другой вариант- нужно вычислять отношение суммы площади клиента и занимаемой им площади к общей площади квартиры/блока/секции. Использую 1й вариант.
                            # TODO: Необходимо подсчитать сумму площадей помещений, занимаемыми клиентами.  
                            rooms_area = 200
                            for room in RealEstate.objects.filter(parent=real_estate):
                                room_volume = room.area / rooms_area * volume
                                #TODO: ОДН должны храниться в отдельной таблице, так как эти данные будут использоваться при перерасчетах.
                                #TODO: Нужно сохранить объем ОДН в отдельную таблицу по ОДН.
        
                #TODO: списать средства с лицевого счета.
        
            for house in RealEstate.objects.filter(type=RealEstate.HOUSE_TYPE):
                client = house.client
                does_cold_water_counter_exist = False
                if does_cold_water_counter_exist:
                    volume = calculate_individual_cold_water_volume(house, client.type_water_norm.cold_water_norm, client.residential, client.residents)
                    volume_model = ColdWaterVolume(period=periods.last(), real_estate=house, volume=volume, date=datetime.date.today())
                    volume_model.save()
                else:
                    volume = client.residents * client.type_water_norm.cold_water_norm
                    cold_water_volume = ColdWaterVolume(real_estate=client.real_estate, volume=volume, date=datetime.date.today())
                    cold_water_volume.save()
                    
                    #TODO: Вычислить объем для земельного участка и расположенных на нем надворных построек
                    # У клиента могут быть виды сельскохозяйственных животных, направления использования
                    # Вычисляем общий оъбем для видов сельскохозяйственных животных
                    animals_volume = 0
                    animals_for_house = Animals.objects.filter(real_estate=house)
                    for animals in animals_for_house:
                        animals_volume = animals_volume + (animals.count * animals.type.norm)
                    
                    # Вычисляем общий объем для направления использования
                    use_case_volume = 0
                        
                    total_volume = animals_volume + use_case_volume
                    period = Period.objects.last()
                    cold_water_volume = ColdWaterVolume(period=period, real_estate=house, volume=total_volume, date=datetime.date.today())
                    cold_water_volume.save()
                    
                    #TODO: списать средства с лицевого счета.

    except ForgottenInitialReadingError:
        pass
