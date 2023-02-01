from django.contrib import admin

from .models import Skill, Account, Job, Connections, Friendship, FriendRequest, Profile, workExperience, jobApplication, jobStatus

admin.site.register(Skill)
admin.site.register(Account)
admin.site.register(Job)
admin.site.register(Connections)
admin.site.register(Friendship)
admin.site.register(FriendRequest)
admin.site.register(Profile)
admin.site.register(workExperience)
admin.site.register(jobApplication)
admin.site.register(jobStatus)


# Register your models here.
