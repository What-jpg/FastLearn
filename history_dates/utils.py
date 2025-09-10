from django.core.cache import cache
from django.db.models import F
from .models import TotalHistoryDates, HistoryDate
import random, math

class TotalHistoryDatesRedisKeys:
    def get():
        return 'totalhistorydates'
    
def get_total_history_dates():
    tot_dates = cache.get(TotalHistoryDatesRedisKeys.get())

    if not tot_dates:
        tot_dates = TotalHistoryDates.objects.first().total_dates
    
    cache.set(TotalHistoryDatesRedisKeys.get(), tot_dates, 300)

    print('tot' + str(tot_dates))
    
    return tot_dates

def choose_task():
    rand = random.randint(0, 2)

    match rand:
        case 0:
            return choose_history_events_with_correct_anwser()
        case 1:
            return choose_history_dates_with_correct_anwser()
        case 2:
            return choose_history_date()

def choose_history_events_with_correct_anwser():
    ansrsCount = get_total_history_dates()
    if (ansrsCount > 4):
        ansrsCount = random.randint(4, 5)

    indexes = random.sample(range(0, get_total_history_dates()), k=ansrsCount)

    dates = HistoryDate.objects.all()

    dates = [dates[e] for e in indexes]

    correct_date = random.choice(dates)

    dates.remove(correct_date)

    return [correct_date.date, [date.events for date in dates], correct_date.events]

def choose_history_dates_with_correct_anwser():
    ansrsCount = get_total_history_dates()
    if (ansrsCount > 4):
        ansrsCount = random.randint(4, 5)

    indexes = random.sample(range(0, get_total_history_dates()), k=ansrsCount)

    dates = HistoryDate.objects.all()

    dates = [dates[e] for e in indexes]

    correct_date = random.choice(dates)

    dates.remove(correct_date)

    return [correct_date.events, [date.date for date in dates], correct_date.date]

def choose_history_date():
    date = HistoryDate.objects.all()[random.randint(0, get_total_history_dates() - 1)]

    return [date.events, [], date.date]