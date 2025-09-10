from django.shortcuts import render
from django.http.response import HttpResponseBadRequest, Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST, require_GET
from .utils import choose_eng_word, get_total_eng_words, easy_gpt_check
from .models import EnglishWords
import g4f, re, random, json
from datetime import datetime

@login_required
def index(request):
    user_id = request.user.id
    # words = list(EnglishWords.objects.filter(user__id=user_id))

    return render(
        request, 
        "english/dashboard.html",
        # {'words': words}
    )

@login_required
def quiz_task(request):
    def gpt_func():
        additionalText = ''
        if word.translations:
            additionalText = ', consider the translations that only should be used by you to understand the context you shouldn\'t use them in the question (' + ', '.join(word.translations) + ')'
        match question_type:
            case 0:
                gpt_response = g4f.ChatCompletion.create(
                    model='gpt-3.5-turbo-16k',
                    messages=[{'role': 'user', 'content': 'Give me a task for word "%s" where there is several anwsers with a different word in them, \
                               but the only one correct anwser is this word, \
                               it should fit the question perfectly if possible%s. \
                               Format this like: the question inside [], \
                               the correct answer inside {{}}, and the other answers inside {} each' % (word.word, additionalText)}]
                )
            # case 1:
            #     gpt_response = g4f.ChatCompletion.create(
            #         model='gpt-4o',
            #         messages=[{'role': 'user', 'content': 'Give me a task, which is a sentence where there is a place skipped for word "%s" \
            #                    where there is several anwsers with different word in them, \
            #                    but the only one correct anwser is this word%s, also you can use different forms of it as the correct answer if you want, \
            #                    but in this case use only one form of this word. \
            #                    Only the correct anwser should fit the sentence perfectly if possible. \
            #                    Format this like: the sentence inside [], a place skipped as ___ \
            #                    the correct answer inside {{}}, and the other answers inside {} each' % (word.word, additionalText)}]
            #     )
            case 1:
                gpt_response = g4f.ChatCompletion.create(
                    model='gpt-3.5-turbo-16k',
                    messages=[{'role': 'user', 'content': 'Give me a task for word "%s" where I need to type in this word as the anwser%s. \
                               The anwser should fit the question perfectly, if possible. \
                               Format this like: the question inside [], \
                               the answer inside {{}} without the quotations' % (word.word, additionalText)}]
                )
            # case 3:
            #     gpt_response = g4f.ChatCompletion.create(
            #         model='gpt-4o',
            #         messages=[{'role': 'user', 'content': 'Give me a task, which is a sentence where there is a place skipped for word "%s" where I need to type in this word as an anwser%s, \
            #                    also you can use different forms of it in the correct answer if you want, but in this case use only one form of the word. \
            #                    Only the anwser should fit the sentence perfectly if possible. \
            #                    Format this like: the sentence inside [], a place skipped as ___ \
            #                    the answer inside {{}}' % (word.word, additionalText)}]
            #     )

        print(gpt_response + "not cool")

        question = re.search(r'\[(.*)\]', gpt_response).group(1)

        correct_ansr = (re.search(r'\{\{(.*)\}\}', gpt_response).group(1), True)
        ansrs = [[x, False] for x in re.findall(r'(?<!\{)\{([^\{\}]*)\}(?!\})', gpt_response)]

        ansrs += [correct_ansr]

        random.shuffle(ansrs)

        return question, ansrs, correct_ansr
    
    if get_total_eng_words(request) == 0:
        return HttpResponseBadRequest('There are no words for user currently.')
    
    word = choose_eng_word(request)

    question_type = random.randint(0, 1)

    question, ansrs, correct_ansr = easy_gpt_check(gpt_func)

    print(ansrs)

    return render(request,
        'english/word_form.html',
        {'question': question, 'options': ansrs, 'correct_word': word.word}
    )

@login_required
@require_POST
def check_eng_word(request, word):
    print('accessed')
    word = get_object_or_404(EnglishWords.objects.filter(user__id=request.user.id, word=word))
    data = json.loads(request.body)

    if data.get('correct', None):
        word.streak += 1
    else:
        word.streak = 0

    word.total_invokes += 1

    word.last_check = datetime.now()

    word.save()

    return HttpResponse('OK')

@login_required
@require_POST
def add_word(request):
    data = request.POST

    if request.method == 'POST':
        def gpt_func():
            if usr_trans:
                translations = g4f.ChatCompletion.create(
                    model='gpt-4o',
                    messages=[
                        {'role': 'user', 'content': 'Return me the valid translations for word "%s" from list (%s) in format [translation, translation...] if there is no such a values return [], these brackets should be your only response' % (word, ', '.join(usr_trans))}
                    ]
                )
                print("translations: " + translations)
                return re.search(r'\[(.*)\]', translations).group(1).split(', ')
            else:
                translations = g4f.ChatCompletion.create(
                    model='gpt-4o',
                    messages=[
                        {'role': 'user', 'content': 'Return me None if "%s" is a valid word, otherwise return []' % (word)}
                    ]
                )
                print("translations: " + translations)
                matc = re.search(r'\[\]', translations)
                if matc:
                    return []
                return None
        
        word = data.get('word', None)
        if not word:
            return Http404()
        
        word = word.lower()
        
        if EnglishWords.objects.filter(user__id=request.user.id, word=word).exists():
            return HttpResponseBadRequest('The word has been already added')

        usr_trans = data.get('translations', None)

        # translations = easy_gpt_check(gpt_func)

        print(isinstance(usr_trans, str))

        print(usr_trans)

        translations = json.loads(usr_trans) if usr_trans else None

        translations = [x.lower() for x in translations] if translations else None

        # if translations != None or translations[0] == '':
        #     print('The word does not exist or the translations aren\'t correct.')
        #     return HttpResponseBadRequest('The word does not exist or the translations aren\'t correct.')
        
        EnglishWords.objects.create(user=request.user, word=word.lower(), translations=translations)

        return HttpResponse('OK')
    
@login_required
@require_POST
def delete_word(request):
    data = request.POST

    word = data.get('word', None)

    print("word " + word)

    word_instance = get_object_or_404(EnglishWords, word=word, user__id=request.user.id)

    word_instance.delete()

    return HttpResponse(status=204)

@require_GET
@login_required
def search_word(request):
    symbols = request.GET.get('symbols')
    page = request.GET.get('page')

    if symbols:
        words = EnglishWords.objects.filter(word__icontains=symbols, user__id=request.user.id).order_by('-added')
    else:
        words = EnglishWords.objects.filter(user__id=request.user.id).order_by('-added')
    
    paginator = Paginator(words, 25)

    if not page:
        page = 1

    words = paginator.get_page(page)

    print("len " + str(len([{"word": el.word, "translations": el.translations} for el in list(words)])))

    return JsonResponse({'data': [{"word": el.word, "translations": el.translations} for el in list(words)], 'hasNext': words.has_next()}, status=200)



@login_required
@require_GET
def get_translations_check_word(request):
    word = request.GET.get('word')

    if EnglishWords.objects.filter(user__id=request.user.id, word=word).exists():
            return HttpResponseBadRequest('The word has been already added')

    if word:
        translations = g4f.ChatCompletion.create(
                    model='gpt-4o',
                    messages=[
                        {'role': 'user', 'content': 'Create me a translations for word "%s" in format [translation in ukrainian, translation in ukrainan...] if the word does not exist than just return an empty []' % word}
                    ]
                )
        
        translations = re.search(r'\[(.*)\]', translations).group(1).split(', ')

        if translations[0] == '':
            return HttpResponseBadRequest('The word does not exist')
        
        return JsonResponse({'data': translations}, status=200)
    else:
        HttpResponseBadRequest('Must include word query param')
