from xmlrpc.client import DateTime
from django.contrib import auth
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase, tag, client
from django.urls import reverse
from .models import Connections, Friendship, Job, Account, FriendRequest, Profile, jobStatus, Message
from datetime import date
import pytz
from datetime import datetime, timedelta



class notificationsTests(TestCase):
    def setUp(self):
        self.login_url = reverse("jobs:login")
        self.logout_url = reverse("jobs:logout")
        self.job_post_url = reverse("jobs:postjob")
        self.job_section_url = reverse("jobs:jobs")

        #Create fake user info
        self.saulUser = User.objects.create_user(username="betterCall", first_name="Saul", last_name="Goodman", password="JimmyMcGill!")
        self.testUser = User.objects.create_user(username="testuser", first_name="paul", last_name="gaming", password="top_secret")

        self.job_post = {
            "title": "Defense Attorney",
            "employer": "Walter White",
            "description": "Become the crooked Lawyer you were meant to be.",
            "location": "Albuquerque , New Mexico",
            "salary": 1000000
        }

        self.job_post2 = {
            "title": "Software Engineer",
            "employer": "InCollege",
            "description": "Be part of an amazing dev team. Develop applications to help college students connect with their peers and find a job after graduation.",
            "location": "Tampa, FL",
            "salary": 80000
        }

        self.user_login = {
            "username":"betterCall",
            "password":"JimmyMcGill!"
        }


        self.user_login2 = {
            "username": "testuser",
            "password": "top_secret"
        }

    def testNewJobNotif(self):
        #create a new job
        Job.objects.create(postedBy_id = User.objects.get(first_name = "paul").id, title="testJob", salary = 1)

        #login as a user
        self.client.post(self.login_url, self.user_login, format="text/html")
        user = auth.get_user(self.client)

        #go back in time a bit
        user.last_login -= timedelta(hours = 3)
        user.save()

        response = self.client.get(self.job_section_url)

        self.assertContains(response,  "There are some new jobs posted since your last visit") #7 job so far!
    
    def testNumJobsApplied(self):
        #create a new job
        Job.objects.create(postedBy_id = User.objects.get(first_name = "paul").id, title="testJob", salary = 1)

        #login as a user
        self.client.post(self.login_url, self.user_login, format="text/html")
        requestUser = auth.get_user(self.client)

        jobStatus.objects.create(user = requestUser, associatedJob = Job.objects.get(title="testJob"), applied = True, saved=False)

        response = self.client.get(self.job_section_url)

        self.assertContains(response,  "You have applied for 1 job so far!") 

    def test7DaysSinceApplied(self):
        # The logic behind this is no jobs applied to == havent applied in 7 days

        self.client.post(self.login_url, self.user_login, format="text/html")

        response = self.client.get(self.job_section_url)

        self.assertContains(response,  "You haven't applied for any job in the past 7 days")

class messageTests(TestCase):
    def setUp(self):
        self.login_url = reverse("jobs:login")
        self.logout_url = reverse("jobs:logout")
        self.job_post_url = reverse("jobs:postjob")
        self.job_section_url = reverse("jobs:jobs")
        self.inbox = reverse("jobs:MessageInbox")

        #Create fake user info
        self.saulUser = User.objects.create_user(username="betterCall", first_name="Saul", last_name="Goodman", password="JimmyMcGill!")
        
        self.testUser = User.objects.create_user(username="testuser", first_name="paul", last_name="gaming", password="top_secret")

        self.saulAccount = Account.objects.get(user_id = self.saulUser.pk)
        self.saulAccount.plusAccount = "Plus"

        self.testAccount = Account.objects.get(user_id = self.testUser.pk)

        self.saul_login = {
            "username":"betterCall",
            "password":"JimmyMcGill!"
        }

        self.test_login = {
            "username": "testuser",
            "password": "top_secret"
        }

        #friend info

        # self.friendship = Friendship.objects.create(user_one)
    def testCreateMessage(self):
        # The logic behind this is no jobs applied to == havent applied in 7 days

        self.client.post(self.login_url, self.saul_login, format="text/html")
        user = auth.get_user(self.client)
        #userAccount = Account.objects.get(user_id = user.id)

        processMessageUrl = reverse('jobs:ProcessMessage', kwargs={'pk':self.testUser.pk})

        self.client.post(processMessageUrl, {"content":"testMessage"})
        #print(Message.objects.get(sender = user).content)

        response = self.client.get(self.inbox, format="text/html")

        self.assertEqual(Message.objects.get(sender = user).content, "testMessage")
        self.assertContains(response, "testMessage")