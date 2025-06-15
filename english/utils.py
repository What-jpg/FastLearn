from django.core.cache import cache
from django.db.models import F
from .models import TotalEnglishWords, EnglishWords
import random, math

class TotalEnglishWordsRedisKeys:
    def get(request):
        return 'totalengwords:%s' % (request.user.id)
    
    def get_with_id(usr_id):
        return 'totalengwords:%s' % (usr_id)
    
def get_total_eng_words(request):
    usr_id = request.user.id

    tot_words = cache.get(TotalEnglishWordsRedisKeys.get(request))

    if not tot_words:
        tot_words = TotalEnglishWords.objects.filter(user__id=usr_id).first().total_words
    
    cache.set(TotalEnglishWordsRedisKeys.get(request), tot_words, 300)

    print('tot' + str(tot_words))
    
    return tot_words

def random_row(tot_words):
    return random.randint(1, tot_words)

def random_row_arithmetic(tot_words):
    if tot_words == 1:
        return 1
    
    starting_chance = 1
    ending_chance = 9

    tot_sum = (starting_chance + ending_chance)/2 * tot_words
    d = (ending_chance - starting_chance) / (tot_words - 1)

    rand_float = random.uniform(0, tot_sum)

    root_D = math.sqrt(starting_chance - starting_chance*d + (d**2)/4 + 2*d*rand_float)

    n_float = (-starting_chance + root_D)/d + 0.5

    if n_float.is_integer() and n_float != 0:
        return int(n_float)
    else:
        return int(n_float) + 1
    
def random_row_geometric(tot_words):
    if tot_words == 1:
        return 1
    
    starting_chance = 1
    ending_chance = 9

    q = (ending_chance / starting_chance) ** (1/(tot_words - 1))
    tot_sum = starting_chance*(q**tot_words - 1) / (q - 1)

    rand_float = random.uniform(0, tot_sum)

    n_float = math.log(1/q + rand_float/starting_chance - rand_float/(starting_chance*q), q) + 1

    if n_float.is_integer() and n_float != 0:
        return int(n_float)
    else:
        return int(n_float) + 1
    
def choose_eng_word(request, search_opts = ['added', '-added', 'streak', 'last_check', 'newest', 'newest']):
    tot_words = get_total_eng_words(request)
    # if tot_words == 0:
    #     return None
    last_word_checked = EnglishWords.objects.exclude(added=F('last_check')).order_by('-last_check').first()
    print(last_word_checked)
    if last_word_checked and tot_words > 1:
        tot_words -= 1

    rand_opt = random.randint(0, len(search_opts) - 1)
    print(tot_words)
    print("arith: " + str(random_row_arithmetic(tot_words) - 1))
    print('geom: ' + str(random_row_geometric(tot_words) - 1))
    match search_opts[rand_opt]:
        case 'added':
            if last_word_checked:
                word = EnglishWords.objects.exclude(id=last_word_checked.id)\
                    .order_by('added')[random_row_arithmetic(tot_words) - 1]
            else:
                word = EnglishWords.objects\
                    .order_by('added')[random_row_arithmetic(tot_words) - 1]
        case '-added':
            if last_word_checked:
                word = EnglishWords.objects.exclude(id=last_word_checked.id)\
                    .order_by('-added')[random_row_arithmetic(tot_words) - 1]
            else:
                word = EnglishWords.objects\
                    .order_by('-added')[random_row_arithmetic(tot_words) - 1]
        case 'streak':
            if last_word_checked:
                word = EnglishWords.objects.exclude(id=last_word_checked.id)\
                    .order_by('streak')[random_row_geometric(tot_words) - 1]
            else:
                word = EnglishWords.objects\
                    .order_by('streak')[random_row_geometric(tot_words) - 1]
        case 'last_check':
            if last_word_checked:
                word = EnglishWords.objects.exclude(id=last_word_checked.id)\
                    .order_by('last_check')[random_row_geometric(tot_words) - 1]
            else:
                word = EnglishWords.objects\
                    .order_by('last_check')[random_row_geometric(tot_words) - 1]
        case 'newest':
            words = EnglishWords.objects.filter(total_invokes__lte=5)
            if last_word_checked:
                words.exclude(id=last_word_checked.id)

            words_count = words.count()

            if words_count == 0:
                word = choose_eng_word(request, [x for x in search_opts if x != 'newest'])
            else: 
                word = words[random_row(words_count) - 1]

    return word

def easy_gpt_check(func, cycles_count = 5):
    try:
        return func()
    except Exception:
        if cycles_count > 1:
            return easy_gpt_check(func, cycles_count - 1)
        else:
            raise Exception('Too many times incorrect returns from AI, maybe the prompt is bad')