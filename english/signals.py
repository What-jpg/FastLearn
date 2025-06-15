from django.dispatch import receiver
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from .models import EnglishWords, TotalEnglishWords
from .utils import TotalEnglishWordsRedisKeys

@receiver(post_save, sender=EnglishWords)
def eng_word_created(sender, instance, created, **kwargs):
    if created:
        usr = instance.user

        tot_words_instance = TotalEnglishWords.objects.filter(user__id=usr.id).first()

        if tot_words_instance:
            tot_words_instance.total_words += 1
            tot_words_instance.save()

            redis_key = TotalEnglishWordsRedisKeys.get_with_id(usr.id)

            if cache.get(redis_key):
                cache.set(redis_key, tot_words_instance.total_words, 60)
        else:
            TotalEnglishWords.objects.create(user=usr, total_words=1)

@receiver(post_delete, sender=EnglishWords)
def eng_word_created(sender, instance, **kwargs):
    usr = instance.user

    tot_words_instance = TotalEnglishWords.objects.filter(user__id=usr.id).first()

    tot_words_instance.total_words -= 1
    tot_words_instance.save()

    redis_key = TotalEnglishWordsRedisKeys.get_with_id(usr.id)

    if cache.get(redis_key):
        cache.set(redis_key, tot_words_instance.total_words, 60)