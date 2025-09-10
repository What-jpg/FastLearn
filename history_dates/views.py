from django.shortcuts import render
from django.http.response import HttpResponseBadRequest, Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST, require_GET
from .utils import choose_history_events_with_correct_anwser, choose_history_dates_with_correct_anwser, choose_history_date, get_total_history_dates, choose_task
from .models import HistoryDate
import g4f, re, random, json
from datetime import datetime

@login_required
def index(request):
    user_id = request.user.id
    # words = list(EnglishWords.objects.filter(user__id=user_id))

    return render(
        request, 
        "history_dates/dashboard.html",
        # {'words': words}
    )

@login_required
def quiz_task(request):
    if get_total_history_dates() == 0:
        return HttpResponseBadRequest('There are no history dates currently.')
    
    question, ansrs, correct_ansr = choose_task()

    ansrs = [[ansr, False] for ansr in ansrs]
    ansrs += [[correct_ansr, True]]

    random.shuffle(ansrs)

    print(question)
    print(ansrs)
    print(correct_ansr)

    return render(request,
        'history_dates/history_date_form.html',
        {'question': question, 'options': ansrs, 'correct_word': correct_ansr}
    )

# @login_required
# @require_POST
# def check_eng_word(request, word):
#     print('accessed')
#     word = get_object_or_404(EnglishWords.objects.filter(user__id=request.user.id, word=word))
#     data = json.loads(request.body)

#     if data.get('correct', None):
#         word.streak += 1
#     else:
#         word.streak = 0

#     word.total_invokes += 1

#     word.last_check = datetime.now()

#     word.save()

#     return HttpResponse('OK')

@login_required
@require_POST
def add_hist_date(request):
    data = request.POST

    if request.method == 'POST':
        date = data.get('date', None)
        events = data.get('events', None)

        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponse("Forbidden", status=403)
        if not date or not events:
            return Http404()
        
        if HistoryDate.objects.filter(date=date).exists():
            return HttpResponseBadRequest('The date has been already added')

        # translations = easy_gpt_check(gpt_func)
        # if translations != None or translations[0] == '':
        #     print('The word does not exist or the translations aren\'t correct.')
        #     return HttpResponseBadRequest('The word does not exist or the translations aren\'t correct.')
        
        HistoryDate.objects.create(date=date, events=events)

        return HttpResponse('OK')
    
@login_required
@require_POST
def delete_hist_date(request):
    data = request.POST

    date = data.get('date', None)

    print(date + " is the date")
    
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponse("Forbidden", status=403)

    date_instance = get_object_or_404(HistoryDate, date=date)

    date_instance.delete()

    return HttpResponse(status=204)

@require_GET
@login_required
def search_hist_date(request):
    symbols = request.GET.get('symbols')
    page = request.GET.get('page')

    if symbols:
        dates = HistoryDate.objects.filter(date__icontains=symbols).order_by('-id')
    else:
        dates = HistoryDate.objects.order_by('-id')
    
    paginator = Paginator(dates, 25)

    if not page:
        page = 1

    dates = paginator.get_page(page)

    print(list(dates)[0].events)

    return JsonResponse({'data': [{"date": el.date, "events": el.events} for el in list(dates)], 'hasNext': dates.has_next()}, status=200)


    
# @csrf_exempt
# @login_required
# @require_GET
# def get_translations_check_word(request):
#     word = request.GET.get('word')

#     if EnglishWords.objects.filter(user__id=request.user.id, word=word).exists():
#             return HttpResponseBadRequest('The word has been already added')

#     if word:
#         translations = g4f.ChatCompletion.create(
#                     model='gpt-4o',
#                     messages=[
#                         {'role': 'user', 'content': 'Create me a translations for word "%s" in format [translation in ukrainian, translation in ukrainan...] if the word does not exist than just return an empty []' % word}
#                     ]
#                 )
        
#         translations = re.search(r'\[(.*)\]', translations).group(1).split(', ')

#         if translations[0] == '':
#             return HttpResponseBadRequest('The word does not exist')
        
#         return JsonResponse({'data': translations}, status=200)
#     else:
#         HttpResponseBadRequest('Must include word query param')
