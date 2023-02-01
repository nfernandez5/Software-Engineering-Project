from django.db import models
from django.contrib.auth.models import User, AbstractUser
import uuid
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.exceptions import PermissionDenied
from django.urls import reverse
import datetime
from simple_history.models import HistoricalRecords
import pytz
from django.utils.translation import gettext_lazy as _

utc=pytz.UTC
class Skill(models.Model):
    skill_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__ (self):
        return self.skill_text

# class User(AbstractUser):
#     skill = models.ManyToManyField(Skill, blank=True)

#     language = models.CharField(max_length=50, blank=True, null=True)
#     emails = models.CharField(max_length=5, default="Yes", blank=True, null=True)
#     sms = models.CharField(max_length=50, default="Yes", blank=True, null=True)
#     ads = models.CharField(max_length=50, default="Yes", blank=True, null=True)

#     major = models.CharField(max_length=50, blank=True, null=True)
#     university = models.CharField(max_length=100, blank=True, null=True)

#     friends = models.ManyToManyField('self', through='Friendship')

#     def __str__(self):
#         return f'{self.last_name}, {self.first_name}'


#user account, 1-to-1 with the User built-in model of Django. might not need now
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    skill = models.ManyToManyField(Skill,blank=True)
    #connections = models.ManyToManyField(User)

    language = models.CharField(max_length=50, blank=True, null=True)
    emails = models.CharField(max_length=5, default="Yes", blank=True, null=True)
    sms = models.CharField(max_length=50, default="Yes", blank=True, null=True)
    ads = models.CharField(max_length=50, default="Yes", blank=True, null=True)

    major = models.CharField(max_length=50, blank=True, null=True)
    university = models.CharField(max_length=100, blank=True, null=True)

    friends = models.ManyToManyField('self', through='Friendship')
    friendRequests = models.ManyToManyField('self', through='FriendRequest')
    plusAccount = models.CharField(max_length=50, default="Standard", blank=False, null=False)


    def lastLogin(self):
        lastLogin = self.last_login
        newJobs = Job.objects.all().reverse()[0].getTimeCreated
        if newJobs - lastLogin >0:
            return True
        else:
            return False
    previous_login = models.DateTimeField(blank=True, null=True)
    
    def newAccount(self):
        lastLogin = self.last_login
        newUser = User.objects.all().reverse()[0].date_joined
        if newUser - lastLogin >0:
            return True
        else:
            return False    
    def __str__(self):
        return f'{self.last_name}, {self.first_name}'
    
# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     try:
#        if created:
#           Account.objects.create(user=instance).save()
#     except Exception as err:
#        print(f'Error creating user profile!\n{err}')

#job, n-to-1 with User
class Job(models.Model):
    description = models.TextField()
    title = models.CharField(max_length=200)
    employer = models.CharField(max_length=100)
    location = models.CharField(max_length=50)
    salary = models.IntegerField()
    postedBy = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    history = HistoricalRecords() #sprint8 updated
    #return datetime of creation
    def getTimeCreated(self):
        first = self.history.first()
        if first ==None:
            return False
        else:
            idx = str(first).find('as of')
            date = datetime.datetime.strptime(str(first)[idx+6:idx+25],'%Y-%m-%d %H:%M:%S')
            return date
    def __str__(self):
        return f'{self.title} - {self.employer}'

    def get_absolute_url(self):
        return reverse("jobs:displayJob", args=[str(self.id), self.title])

#this table will only store jobs that have been applied or saved
class jobStatus(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    associatedJob = models.ForeignKey(Job, on_delete=models.CASCADE)
    saved = models.BooleanField()
    applied = models.BooleanField()
    history = HistoricalRecords()
    def getTimeCreated(self):
        first = self.history.first()
        if first ==None:
            return 0
        else:
            idx = str(first).find('as of')
            date = datetime.datetime.strptime(str(first)[idx+6:idx+16],'%Y-%m-%d').date()
            date = datetime.datetime.today().date() - date
            return date.days
    #sprint8 updated
    def getDetails(self):
        return self.associatedJob.title + " at " + self.associatedJob.employer
    #sprint8 updated to check delete status
    def checkDeleteStatus (self):
        return self.associatedJob.deleted
    def __str__(self):
        return f'{self.user}, {self.associatedJob}'

    # def get_absolute_url(self):
    #     return reverse("article_detail", args=[str(self.id)])

class jobApplication(models.Model):
    appliedJob = models.ForeignKey(Job, on_delete=models.CASCADE, null=True)
    appliedUser = models.ForeignKey(User, on_delete=models.CASCADE)
    gradDate = models.DateTimeField(blank=True, null=True)
    startDate = models.DateTimeField(blank=True, null=True)
    applyParagraph = models.TextField()
    appliedTime = models.DateTimeField(default = datetime.date.today)
    history = HistoricalRecords()#sprint8 updated
    def getTimeCreated(self):
        appliedTime = self.appliedTime
        if appliedTime ==None:
            return 0
        else:
            # idx = str(first).find('as of')
            # date = datetime.datetime.strptime(str(first)[idx+6:idx+16],'%Y-%d-%m').date()
            appliedDate = appliedTime.date()
            date = datetime.datetime.today().date() - appliedTime
            return date.days

    def __str__(self):
        return f'{self.appliedUser}, {self.appliedJob}'

#for the Connections
class Connections(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    another_user = models.ManyToManyField(User, related_name='another_user', blank=True)

#limit only 10 jobs to be posted
@receiver(pre_save, sender=User)
def check_limits(sender, **kwargs):
    if Job.objects.count() > 10:
        raise PermissionDenied

class FriendRequest(models.Model):
    requester = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='requester')
    requested = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='requested')
    dateSent = models.DateTimeField()
    accepted = models.BooleanField(blank=True, null=True)
    dateAccepted = models.DateTimeField(blank=True, null=True)

# for the Friend relationship
class Friendship(models.Model):
    user_one = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='one')
    user_two = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='two')

    def __str__(self):
        return ' and '.join([str(self.user_one), str(self.user_two)])

class Profile(models.Model):
    #1 to 1 on a User
    user = models.OneToOneField(User, on_delete=models.CASCADE) 

    title = models.CharField(max_length=100)
    about = models.TextField(blank=True)

    #this needs to be specially formatted when stored
    major = models.CharField(max_length=100, blank=True)
    
    university = models.CharField(max_length=100, blank=True)
    degree = models.CharField(max_length=100, blank=True)
    yearsAttended = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}\'s Profile'

#Up to three per profile
class workExperience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    employer = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    dateStarted = models.DateTimeField()
    dateEnded = models.DateTimeField(blank=True, null=True)
    
    #Profile and Title must be unique
    class Meta:
        unique_together = (('profile', 'title'),)

    def __str__(self):
        return f'{self.title}, {self.employer}'

class Message(models.Model):
     sender = models.ForeignKey(User, related_name="sender", on_delete=models.CASCADE)
     receiver = models.ForeignKey(User, related_name="receiver", on_delete=models.CASCADE)
     content =  models.CharField(max_length=200, blank=True, default='')
     created_at = models.DateTimeField(auto_now_add=True)

