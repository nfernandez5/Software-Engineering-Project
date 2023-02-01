from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.models import User
from .models import Account, Job, Skill
from django.core.exceptions import PermissionDenied



@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    try:
       if created:
          Account.objects.create(user=instance).save()
          accCreated = Account.objects.get(user=instance)
          accCreated.first_name = User.objects.get(username=instance.username).first_name
          accCreated.last_name = User.objects.get(username = instance.username).last_name
          accCreated.save()
    except Exception as err:
       print(f'Error creating user profile!\n{err}')

#limit number of account = 10
@receiver(pre_save, sender=User)
def limit_profile(sender, **kwargs):
        if sender.objects.count() > 10:
            raise PermissionDenied