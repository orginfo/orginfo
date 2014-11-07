﻿from accounting.models import ColdWaterReading, ColdWaterVolume, RealEstate, Period, ServiceClient, Animals, ColdWaterNorm, ColdWaterVolumeODN
import datetime
from robot.errors import ForgottenInitialReadingError
from django.db.models import Sum
from django.db import transaction
from django.db.models import Q


def calculate_share_of_service_usage(real_estate, service, period):
    #отсечь диапозоны, что за границей периода
    #TODO: плохое название ServiceClient
    service_usages = list(ServiceClient.objects.filter((Q(end__gte=period.start) | Q(end=None)) & Q(start__lte=period.end) & Q(real_estate=real_estate)).order_by('start').all())

    if len(service_usages) == 0:
        return 0 #доля равна 0, ведь она не подключена.

    #при необходимости обрезаем до границ period.start и period.end
    if service_usages[0].start < period.start:
        service_usages[0].start = period.start
    last_index = len(service_usages) - 1
    if service_usages[last_index].end is None or service_usages.last().end > period.end:
        service_usages[last_index].end = period.end

    #вычисляем количество дней с услугой и без услуги, берем долю.
    days_in_period = (period.end - period.start).days
    service_usages_days = 0
    for usage in service_usages:
        service_usages_days = service_usages_days + (usage.end - usage.start).days
    share = service_usages_days / days_in_period
    return share

def calculate_individual_cold_water_volume(real_estate, cold_water_norm, residential, residents):
    """Списание средств за холодную воду.

    В ColdWaterReading за один отчетный период хранится только одно показание.
    Как быть в случае, когда установлен счетчик с ненулевым показанием? Ведь
    тогда откуда брать показание, оно будет явно описано в данных, а не будет
    хардкода в алгоритме.
    Возвращает объект в котором содержатся:
    volume-объем индивидуального потребления, включая перерасчет
    перерасчета_volume
    """
    class IndividualColdWaterVolume:
        def __init__(self, individual, recalculated=0):
            self.individual = individual
            self.recalculated = recalculated

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
            return IndividualColdWaterVolume(volume, unconfirmed_reading_volumes)

        second_from_the_end_period_reading = ColdWaterReading.objects.filter(real_estate=real_estate, period=periods_with_counter[periods_with_counter.count()-2]).last()
        third_from_the_end_period_reading = ColdWaterReading.objects.filter(real_estate=real_estate, period=periods_with_counter[periods_with_counter.count()-3]).last()
        was_reading_in_second_or_third_period_from_the_end = second_from_the_end_period_reading or third_from_the_end_period_reading
        if was_reading_in_second_or_third_period_from_the_end:
            last_six_volumes_sum = ColdWaterVolume.objects.filter(real_estate=real_estate, period__serial_number__in=range(periods_with_counter.last().serial_number-6+1, periods_with_counter.last().serial_number+1)).aggregate(Sum('volume'))['volume__sum']
            average_volume = last_six_volumes_sum/6
            return IndividualColdWaterVolume(average_volume)

    share = calculate_share_of_service_usage(real_estate, ServiceClient.COLD_WATER_SERVICE, Period.objects.all().last())
    if residential: #или счетчик меньше 6 периодов, или без счетчика
        #Формула № 4а
        volume = residents * cold_water_norm
        return IndividualColdWaterVolume(volume * share)

    periods = Period.objects.order_by('start')
    start_period_index = periods.count()-6-1
    if start_period_index > 0:
        last_six_volumes_sum = ColdWaterVolume.objects.filter(real_estate=real_estate, period__serial_number__gte=periods[start_period_index].serial_number).aggregate(Sum('volume'))['volume__sum']
        average_volume = last_six_volumes_sum/6
        return IndividualColdWaterVolume(average_volume * share)

    return None #TODO: нужен флаг -- manual

def write_off():
    """Списание средств с клиентских счетов.

    Списание произодится раз в месяц 26 числа.
    """
    try:
        with transaction.atomic():
            periods = Period.objects.order_by('start')

            for building in RealEstate.objects.filter(type=RealEstate.BUILDING_TYPE):
                real_estates = []
                for real_estate in RealEstate.objects.filter(parent=building):
                    real_estates.append(real_estate)

                is_cold_water_service = calculate_share_of_service_usage(building, ServiceClient.COLD_WATER_SERVICE, Period.objects.all().last()) > 0
                if is_cold_water_service:
                    #{
                    #{Начало расчета индивидуального потребления:
                    #{
                    cold_water_volume_clients_sum = 0
                    recalculated_volume = 0
                    for real_estate in real_estates:
                        if real_estate.type != RealEstate.FLAT_TYPE and real_estate.type != RealEstate.SHARE_TYPE:
                            raise Exception #TODO: Продумать ошибку.

                        #вычисляем для квартир, комунальных квартир и блоков объем потребления услуги, сохраняем его.
                        cold_water_norm = ColdWaterNorm.objects.filter(residential=real_estate.residential, region=building.region).get()
                        volume = calculate_individual_cold_water_volume(real_estate, cold_water_norm, real_estate.residential, real_estate.residents)
                        volume_model = ColdWaterVolume(period=periods.last(), real_estate=real_estate, volume=volume.individual, date=datetime.date.today())
                        volume_model.save()
                        recalculated_volume = recalculated_volume + volume.recalculated

                        if real_estate.type == RealEstate.SHARE_TYPE:
                            total_rooms_volume = 0 #TODO: если total_rooms_volume != volume, то разница объемов будет учтена и рассчитана в расчет ОДН.
                            residents = 0 #- общее количество проживающих в блоке, коммунальной квартире и т.д.
                            for room in RealEstate.objects.filter(parent=real_estate):
                                residents = residents + room.residents

                            #Вычисляем необходимые объемы для каждого помещения.
                            for room in RealEstate.objects.filter(parent=real_estate):
                                # Вычисляем долю 'комнаты ко всей квартире', в зависимости от типа помещения:
                                # жилое помещение   - тогда количество проживающих в комнате к общему количеству проживающих в квартире;
                                # нежилое помещение - тогда площать комнаты к общей площади квартиры.
                                # proportion - доля комнаты к общей квартире
                                proportion = 1
                                if room.residential:
                                    proportion = room.residents / residents
                                else:
                                    #Вычисление доли по площади.
                                    proportion = room.space / real_estate.space

                                room_volume = proportion * volume
                                volume_model = ColdWaterVolume(period=periods.last(), real_estate=room, volume=room_volume, date=datetime.date.today())
                                volume_model.save()

                                total_rooms_volume = total_rooms_volume + room_volume

                        # Суммируем объемы помещений. Если квартира коммунальная (или блок общещия, или блок с офисами), тогда используем сумму объемов всех внутренних помещений клиентов.
                        cold_water_volume_clients_sum = cold_water_volume_clients_sum + volume
                    #}
                    #}Конец расчета индивидуального потребления
                    #}

                    #{
                    #{Начало расчета общедомовых нужд:
                    #{
                    #расчет общедомовых нужд. Доля объма на помещение определяется от соотношения площади помещения к общей площади всех жилых и нежилых помещений.
                    # building_space - общая площадь всех жилых помещений (квартир) и нежилых помещений в многоквартирном доме.
                    cold_water_building_volume = None
                    building_space = 0
                    for real_estate in real_estates:
                        if real_estate.type == RealEstate.FLAT_TYPE or real_estate.type == RealEstate.SHARE_TYPE:
                            building_space = building_space + real_estate.space

                    setup_date = building.cold_water_counter_setup_date
                    if setup_date:
                        last_period_reading = periods[periods.count()-1].coldwaterreading_set.filter(real_estate=building).get()
                        next_to_last_period_reading = periods[periods.count()-2].coldwaterreading_set.filter(real_estate=building).get()
                        if last_period_reading and next_to_last_period_reading:
                            cold_water_building_volume = last_period_reading.value - next_to_last_period_reading.value
                    #Расчёт по норме.
                    if cold_water_building_volume is None:
                        residents = 0
                        for real_estate in RealEstate.objects.filter(parent=building):
                            if real_estate.type == RealEstate.FLAT_TYPE:
                                residents = residents + real_estate.client_set.last().residents
                            if real_estate.type == RealEstate.SHARE_TYPE:
                                for share in RealEstate.objects.filter(parent=real_estate):
                                    if share.type == RealEstate.ROOM_TYPE:
                                        residents = residents + share.client_set.last().residents

                        norm = ColdWaterNorm.objects.filter(residential=building.residential, region=building.region).get()
                        
                        residential_cold_water_volume = residents * norm

                        #TODO: not_residential_cold_water_volume предоставляется поставщиком услуги
                        not_residential_cold_water_volume = 0
                        cold_water_building_volume = residential_cold_water_volume + not_residential_cold_water_volume

                    volume = cold_water_building_volume - cold_water_volume_clients_sum + recalculated_volume
                    if volume != 0:
                        for real_estate in real_estates:
                            real_estate_volume = 0
                            if setup_date:
                                real_estate_volume = real_estate.space / building.space * volume
                            else:
                                norm = ColdWaterNorm.objects.filter(residential=building.residential, region=building.region).get()
                                real_estate_volume = norm * real_estate.space_of_joint_estate * real_estate.space / building_space #TODO: Проверить, norm на ОДН равна норме холодного водснабжения на здание?
                                #TODO: Нужно ли сохранять объем ОДН для помещений с типом SHARE_TYPE?
                                cold_water_volume = ColdWaterVolumeODN(real_estate=real_estate, volume=real_estate_volume, date=datetime.date.today())
                                cold_water_volume.save()

                            if real_estate.type == RealEstate.SHARE_TYPE:
                                # Распределяем общий объем между внутренними помещениями клиентов.
                                # Для распределения требуется не общая площадь квартиры/блока/секции, а общая площадь помещений клиентов.
                                rooms_space = 0
                                for room in RealEstate.objects.filter(parent=real_estate):
                                    rooms_space = rooms_space + room.space
                                for room in RealEstate.objects.filter(parent=real_estate):
                                    room_volume = room.space / rooms_space * real_estate_volume
                                    cold_water_volume = ColdWaterVolumeODN(real_estate=real_estate, volume=room_volume, date=datetime.date.today())
                                    cold_water_volume.save()
                    #}
                    #}Конец расчета общедомовых нужд
                    #}

            for house in RealEstate.objects.filter(type=RealEstate.HOUSE_TYPE):
                cold_water_norm = ColdWaterNorm.objects.filter(residential=house.residential, region=house.region).get()
                does_cold_water_counter_exist = False
                if does_cold_water_counter_exist:
                    volume = calculate_individual_cold_water_volume(house, cold_water_norm, house.residential, house.residents)
                    volume_model = ColdWaterVolume(period=periods.last(), real_estate=house, volume=volume.individual, date=datetime.date.today())
                    volume_model.save()
                else:
                    volume = house.residents * cold_water_norm
                    cold_water_volume = ColdWaterVolume(real_estate=house, volume=volume, date=datetime.date.today())
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
