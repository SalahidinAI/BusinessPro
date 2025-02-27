import random
from django.core.mail import send_mail
from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # Генерация случайного 4-значного кода
    reset_code = random.randint(1000, 9999)

    # Сохраняем код в поле key токена
    reset_password_token.key = str(reset_code)
    reset_password_token.save()

    # Текст сообщения
    email_plaintext_message = f"Ваш код для сброса пароля: {reset_code}"

    # Отправка email
    send_mail(
        "Сброс пароля",  # Тема письма
        email_plaintext_message,  # Текст письма
        "noreply@somehost.local",  # От кого
        [reset_password_token.user.email],  # Список получателей
        fail_silently=False,
    )


from django.db.models.signals import post_save, pre_save
from .models import ProductSize, History, HistoryItem


@receiver(pre_save, sender=ProductSize)
def store_previous_have(sender, instance, **kwargs):
    if instance.pk:
        # Получаем старое значение из базы данных перед сохранением
        previous_instance = ProductSize.objects.get(pk=instance.pk)
        instance._previous_have = previous_instance.have
    else:
        instance._previous_have = instance.have


@receiver(post_save, sender=ProductSize)
def add_to_or_remove_from_history(sender, instance, **kwargs):
    """ После сохранения добавляем или удаляем из истории в зависимости от изменения `have` """
    if hasattr(instance, '_previous_have'):
        # Если `have` изменилось с True на False, добавляем в историю
        if instance._previous_have and not instance.have:
            # Добавляем в History, если `have` изменилось с True на False
            history, created = History.objects.get_or_create(user=instance.product.group.owner)
            HistoryItem.objects.create(
                history=history,
                product=instance.product,
                product_size=instance
            )

        # Если `have` изменилось с False на True, удаляем из истории
        elif not instance._previous_have and instance.have:
            # Удаляем из истории, если `have` изменилось с False на True
            history_items = HistoryItem.objects.filter(
                history__user=instance.product.group.owner,
                product_size=instance
            )
            history_items.delete()  # Удаляет все связанные записи
