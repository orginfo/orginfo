from django.shortcuts import render

def validate(request):
#    periods_with_counter = None
#    setup_date = real_estate.cold_water_counter_setup_date
#    if setup_date:
#        periods_with_counter = Period.objects.order_by('start').filter(start__gte=setup_date)

#    if periods_with_counter and periods_with_counter.count() >= 6:
#        last_period_reading = periods_with_counter.last().coldwaterreading_set.filter(real_estate=real_estate).get()
#        was_reading_in_last_period = last_period_reading is not None
#        if was_reading_in_last_period:
#            next_to_last_period_reading = None
#            i = periods_with_counter.count() - 2
#            while 0 <= i:
#                readings = periods_with_counter[i].coldwaterreading_set.filter(real_estate=real_estate)
#                if readings.count():
#                    next_to_last_period_reading = readings.get()
#                    break
#                i = i - 1
#            if next_to_last_period_reading is None:
#                #print error
#                pass

    return render(request, 'accounting/index.html', {})
