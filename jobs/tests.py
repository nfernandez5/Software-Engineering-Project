from xmlrpc.client import DateTime
from django.contrib import auth
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase, tag, client
from django.urls import reverse
from .models import *
from datetime import date
import os

class RegistrationPageTests(TestCase):
    def setUp(self):
        User.objects.create_user(username="testuser", first_name="Test", last_name="Tester", password="top_secret")
        User.objects.create_user(username="johndoe", first_name="John", last_name="Doe", password="helloworld10!")
       
        self.register_url = reverse("jobs:register")

        self.registration = {
            "username": "testuser2",
            "first_name": "Some",
            "last_name": "Name",
            "password1": "unknown_string",
            "password2": "unknown_string"
        }
        self.bad_password_registration = {
            "username": "testuser3",
            "first_name": "Jane",
            "last_name": "Doe",
            "password1": "pie",
            "password2": "pie"
        }
        self.existing_username_registration = {
            "username": "johndoe",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "top_secret",
            "password2": "top_secret"
        }

    def test_register_page_displays(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/register.html")

    def test_can_register_user(self):
        response = self.client.post(self.register_url, self.registration, format="text/html")
        newUser = auth.get_user(self.client)
        self.assertEqual(Connections.objects.filter(user = newUser.id).exists(), True)
        self.assertEqual(response.status_code, 302) # 302 status code means the user was re-directed, as expected

    def test_cant_register_bad_password(self):
        response = self.client.post(self.register_url, self.bad_password_registration, format="text/html")
        self.assertContains(response, "This password is too short. It must contain at least 8 characters.")
        self.assertContains(response, "This password is too common.")

    def test_cant_register_same_username(self):
        response = self.client.post(self.register_url, self.existing_username_registration, format="text/html")
        self.assertContains(response, "A user with that username already exists.")

class DefaultHomePageTests(TestCase):
    def setUp(self):
        self.successvideo_url = reverse("jobs:successvideo")

    def test_default_home_page_renders(self):
        response = self.client.get("/") # Upon launching the app, a GET request is made to the home route ("/"), fetching the default (not logged-in) homepage

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/base.html")

    def test_success_video_plays_when_clicked(self):
        response = self.client.get(self.successvideo_url)

        htmlVideo = "<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/Zuw2zRGD58E\" title=\"YouTube video player\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>"

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/successVideo.html")
        self.assertContains(response, htmlVideo) # If this video is on the page, it will be able to be played when clicked

class UserHomePageTests(TestCase):
    def setUp(self):
        self.login_url = reverse("jobs:login")
        self.homepage_url = reverse("jobs:home")

        User.objects.create_user(username="testuser", first_name="Test", last_name="Tester", password="top_secret")

        self.user_login = {
            "username": "testuser",
            "password": "top_secret"
        }

    def test_user_homepage_renders(self):
        response1 = self.client.post(self.login_url, self.user_login, format="text/html") 

        self.assertEqual(response1.status_code, 302) # A successful login will redirect (status code 302) to the homepage
        user = auth.get_user(self.client)
        assert user.is_authenticated

        response2 = self.client.get(self.homepage_url)

        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "jobs/nav.html") # If this is true, and the user is authenticated, as asserted above, the user navbar will be displayed

class JobPostsTests(TestCase):
    def setUp(self):
        self.login_url = reverse("jobs:login")
        self.job_section_url = reverse("jobs:jobs")
        self.job_post_url = reverse("jobs:postjob")

        User.objects.create_user(username="testuser", first_name="Test", last_name="Tester", password="top_secret")

        self.user_login = {
            "username": "testuser",
            "password": "top_secret"
        }

        self.job_post = {
            "title": "Software Engineer",
            "employer": "InCollege",
            "description": "Be part of an amazing dev team. Develop applications to help college students connect with their peers and find a job after graduation.",
            "location": "Tampa, FL",
            "salary": 80000
        }

    def test_jobs_pages_renders(self):
        response1 = self.client.post(self.login_url, self.user_login, format="text/html")

        self.assertEqual(response1.status_code, 302)
        user = auth.get_user(self.client)
        assert user.is_authenticated

        response2 = self.client.get(self.job_section_url)

        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "jobs/job-section.html")

    def test_can_make_job_post(self):
        response1 = self.client.post(self.login_url, self.user_login, format="text/html")

        self.assertEqual(response1.status_code, 302)
        user = auth.get_user(self.client)
        assert user.is_authenticated

        response2 = self.client.post(self.job_post_url, self.job_post, format="text/html")
        
        self.assertEqual(response2.status_code, 302)

class SearchUserTests(TestCase):
    def setUp(self):
        self.gamerUser = User.objects.create_user(username="gamerMan", first_name="Gamer", last_name="Man", password="weOutGaming!")
        self.saulUser = User.objects.create_user(username="betterCall", first_name="Saul", last_name="Goodman", password="JimmyMcGill!")
        Connections.objects.create(user = self.saulUser)

        self.login_url = reverse("jobs:login")
        self.searchUrl = reverse("jobs:connectionSection")
        self.searchUrlResults = reverse("jobs:searchResult")

        self.user_login = {
            "username":"betterCall",
            "password":"JimmyMcGill!"
        }
        self.searched_user_success = {
            "first_name": "Gamer", 
            "last_name": "Man"
        }
        self.searched_user_fail = {
            "first_name": "goofy", 
            "last_name": "dude"
        }

    def test_searchPages_render(self):
        response = self.client.get(self.searchUrl)
        self.assertEqual(response.status_code, 302)

    def test_searchResults_render(self):
        response = self.client.get(self.searchUrlResults)
        self.assertEqual(response.status_code, 302)

    #Search for a user that does exist
    def test_search_success_user_authenticated(self):

        #Login to an account
        response1 = self.client.post(self.login_url, self.user_login, format="text/html")
        self.assertEqual(response1.status_code, 302)
        user = auth.get_user(self.client)
        assert user.is_authenticated

        #Then see if the user is added to the connections
        response = self.client.post(self.searchUrl, self.searched_user_success, format="text/html")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "They are a part of the InCollege system")
        self.assertContains(response, "They have been added to your connections")
        for item in Connections.objects.get(user = response.context['user'].id).another_user.all():
            if item == self.gamerUser:
                is_connected = True
        self.assertEqual(is_connected, True)

    def test_search_success_user_unauthenticated(self):
        response = self.client.post(self.searchUrl, self.searched_user_success, format="text/html")
        self.assertEqual(response.status_code, 302)


class navBarTests(TestCase):
    def setUp(self):
        self.home = reverse("jobs:homepage")
        self.login_url = reverse("jobs:login")

        #Create fake user info
        self.saulUser = User.objects.create_user(username="betterCall", first_name="Saul", last_name="Goodman", password="JimmyMcGill!")
        Connections.objects.create(user = self.saulUser)

        self.user_login = {
            "username":"betterCall",
            "password":"JimmyMcGill!"
        }

        #General Links

        #First is the reverse, second is the text in the html, third is the html path
        self.generalLinks = [(reverse("jobs:genAbout"), "About", "useful-links/general-links/about.html"), 
                            (reverse("jobs:genBlog"), "Blog", "useful-links/general-links/blog.html"),
                            (reverse("jobs:genCareers"), "Careers", "useful-links/general-links/careers.html"),
                            (reverse("jobs:genHelp"), "Help Center", "useful-links/general-links/help-center.html"),
                            (reverse("jobs:genPress"), "Press", "useful-links/general-links/press.html")]

        #Other Useful Links
        self.otherUsefulLinks = [(reverse("jobs:browse"), "Browse InCollege", "useful-links/browse-incollege.html"),
                                (reverse("jobs:businessSol"), "Business Solutions", "useful-links/business-solutions.html"),
                                (reverse("jobs:directories"), "Directories", "useful-links/directories.html")]

        #Important Links
        #These will need to be fixed to match Nathan's work
        self.importantLinks = [(reverse("jobs:copyright"), "A Copyright Notice", "important-links/copyright.html"),
                                (reverse("jobs:brandPol"), "Brand Policy", "important-links/brand-policy.html"),
                                (reverse("jobs:cookiePol"), "Cookie Policy", "important-links/cookie-policy.html"),
                                (reverse("jobs:userAgr"), "User Agreement", "important-links/user-agreement.html"),
                                (reverse("jobs:accessibility"), "Accessibility", "important-links/accessibility.html"),
                                (reverse("jobs:about"), "About", "important-links/about.html")]

        self.importantLinksUser = [ (reverse("jobs:privacyEmails"), "Email Settings", "important-links/emails.html"),
                                    (reverse("jobs:privacySMS"), "SMS Settings", "important-links/emails.html"),
                                    (reverse("jobs:privacyAds"), "Targeted Ads Settings", "important-links/emails.html"),
                                    (reverse("jobs:language"), "Languages", "important-links/language.html")]

    #loads in page and checks that html is correct
    def loadPageHelper(self, response, html):
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, html)
        self.assertEqual(response.status_code, 200)
    
    #should login user
    def login(self):
        #self.client.login(username=self.user_login["username"], password=self.user_login["password"])
        #self.client.post(self.login_url, self.user_login, format="text/html")
        #user = auth.get_user(self.client)
        #assert user.is_authenticated
        self.client.force_login(self.saulUser)
        

    def test_general_links_notLoggedIn(self):
        response = self.client.get(self.home)
        #for each link
        for ref in self.generalLinks:
            #Check html has the page
            self.assertContains(response, 'href="%s">%s</a>' % (ref[0], ref[1]))

            #check that it uses the right template and that it loads correctly
            self.loadPageHelper(self.client.get(ref[0]), ref[2])

    def test_general_links_LoggedIn(self):
        #login
        self.login()

        response = self.client.get(self.home)
        #for each link
        for ref in self.generalLinks:
            #Check html has the page
            self.assertContains(response, 'href="%s">%s</a>' % (ref[0], ref[1]))

            #check that it uses the right template and that it loads correctly
            self.loadPageHelper(self.client.get(ref[0]), ref[2])

    def test_otherUsefulLinks_notLoggedIn(self):
        response = self.client.get(self.home)
        #for each link
        for ref in self.otherUsefulLinks:
            #Check html has the page
            self.assertContains(response, 'href="%s">%s</a>' % (ref[0], ref[1]))

            #check that it uses the right template and that it loads correctly
            self.loadPageHelper(self.client.get(ref[0]), ref[2])

    def test_otherUsefulLinks_loggedIn(self):
        self.login()

        response = self.client.get(self.home)
        #for each link
        for ref in self.otherUsefulLinks:
            #Check html has the page
            self.assertContains(response, 'href="%s">%s</a>' % (ref[0], ref[1]))

            #check that it uses the right template and that it loads correctly
            self.loadPageHelper(self.client.get(ref[0]), ref[2])

    def test_importantLinks_notLoggedIn(self):
        self.login()
        response = self.client.get(self.home)
        #for each link
        for ref in self.importantLinks:
            #Check html has the page
            self.assertContains(response, 'href="%s">%s</a>' % (ref[0], ref[1]))

            #check that it uses the right template and that it loads correctly
            self.loadPageHelper(self.client.get(ref[0]), ref[2])

    def test_importantLinks_loggedIn(self):
        self.login()
        response = self.client.get(self.home)
        #for each link
        for ref in self.importantLinks:
            #Check html has the page
            self.assertContains(response, 'href="%s">%s</a>' % (ref[0], ref[1]))

            #check that it uses the right template and that it loads correctly
            self.loadPageHelper(self.client.get(ref[0]), ref[2])

        for ref in self.importantLinksUser:
            #Check html has the page
            self.assertContains(response, 'href="%s">%s</a>' % (ref[0], ref[1]))

            #check that it uses the right template and that it loads correctly
            self.loadPageHelper(self.client.get(ref[0]), ref[2])

class searchFriendTest(TestCase):
    def setUp(self):
        self.userA = User.objects.create_user(username='jnk2022', first_name = 'Megumi', last_name = 'Fushiguro', password = "N0tZenin~")
        self.userB = User.objects.create_user(username = "kingdom", first_name = 'Ky', last_name = 'Vuong', password = "yyds@Tan1")
        self.accountB = Account.objects.get(user = self.userB.id)
        self.accountB.major = "Electrical Engineering"
        self.accountB.university = "University of Tampa"
        self.accountB.save()
        self.userC = User.objects.create_user(username = "gyukaku", first_name = "Gyudon", last_name = "Tonkotsu", password = "Be3f$teak")
        
        self.loginUrl = reverse("jobs:login")
        self.searchUrl = reverse("jobs:findFriends")
        self.searchUrlResults = reverse("jobs:friendResult")

        self.userLogin ={
            "username":"jnk2022",
            "password":"N0tZenin~"
        }

        self.searchedByNameSuccess = {
            'category': "Name",
            'search' : "Vuong Ky"
        }

        self.searchedByMajorSuccess = {
            "category": "major",
            "search" : "Electrical Engineering"
        }

        self.searchedByUniSuccess = {
            "category": "university",
            "search" : "University of Tampa"
        }

        self.searchedByNameFail = {
            "category" : "name",
            "search" : "John Doe"
        }

        self.searchedByMajorFail = {
            "category" : "major",
            "search" : "Mechanical Engineering"
        }

        self.searchedByUniFail = {
            "category" : "university",
            "search" : "University of South Florida"
        }

    def testPageRender(self):
            response = self.client.get(self.searchUrl)
            self.assertEqual(response.status_code, 302)


    @tag('searchNameS')
    def testSearchedByNameSuccess(self):
        #Login to an account. 
        response1 = self.client.post(self.loginUrl, self.userLogin, format="text/html")
        self.assertEqual(response1.status_code, 302)
        user = auth.get_user(self.client)
        assert user.is_authenticated

        response = self.client.post(self.searchUrl,self.searchedByNameSuccess, format = "text/html")
        self.assertEqual(response.status_code, 200)
        self.assertContains (response, "name primary-text")

    def testSearchedByNameFail(self):
        #Login to an account. 
        response1 = self.client.post(self.loginUrl, self.userLogin, format="text/html")
        self.assertEqual(response1.status_code, 302)
        user = auth.get_user(self.client)
        assert user.is_authenticated

        response = self.client.post(self.searchUrl,self.searchedByNameFail, content_type = "application/json")
        self.assertEqual(response.status_code, 200)
        self.assertContains (response, "No results found...")

    def testSearchedByMajorSuccess(self):
        #Login to an account. 
        response1 = self.client.post(self.loginUrl, self.userLogin, format="text/html")
        self.assertEqual(response1.status_code, 302)
        user = auth.get_user(self.client)
        assert user.is_authenticated

        response = self.client.post(self.searchUrl,self.searchedByMajorSuccess, content_type = "application/json")
        self.assertEqual(response.status_code, 200)
        self.assertContains (response, "major")

    def testSearchedByMajorFail(self):
        #Login to an account. 
        response1 = self.client.post(self.loginUrl, self.userLogin, format="text/html")
        self.assertEqual(response1.status_code, 302)
        user = auth.get_user(self.client)
        assert user.is_authenticated

        response = self.client.post(self.searchUrl,self.searchedByMajorFail, content_type = "application/json")
        self.assertEqual(response.status_code, 200)
        self.assertContains (response, "No results found...")

    def testSearchedByUniSuccess(self):
        #Login to an account. 
        response1 = self.client.post(self.loginUrl, self.userLogin, format="text/html")
        self.assertEqual(response1.status_code, 302)
        user = auth.get_user(self.client)
        assert user.is_authenticated

        response = self.client.post(self.searchUrl,self.searchedByUniSuccess, content_type = "application/json")
        self.assertEqual(response.status_code, 200)
        self.assertContains (response, "university")
        
    def testSearchedByUniFail(self):
        #Login to an account. 
        response1 = self.client.post(self.loginUrl, self.userLogin, format="text/html")
        self.assertEqual(response1.status_code, 302)
        user = auth.get_user(self.client)
        assert user.is_authenticated


        response = self.client.post(self.searchUrl,self.searchedByUniFail, format= "application/json")
        self.assertEqual(response.status_code, 200)
        self.assertContains (response, "No results found...")

class addFriendTest (TestCase):
    def setUp(self):
        self.userA = User.objects.create_user(username='jnk2022', first_name = 'Megumi', last_name = 'Fushiguro', password = "N0tZenin~")
        self.userB = User.objects.create_user(username = "kingdom", first_name = 'Ky', last_name = 'Vuong', password = "yyds@Tan1")
        self.accountB = Account.objects.get(user = self.userB.id)
        self.accountB.major = "Electrical Engineering"
        self.accountB.university = "University of Tampa"
        self.accountB.save()
        
        self.accountA = Account.objects.get(user = self.userA.id)
        self.accountA.major = "Mechanical Engineering"
        self.accountA.university = "University of South Florida"
        self.accountA.save()

        self.loginUrl = reverse("jobs:login")
        self.searchUrl = reverse("jobs:findFriends")
        self.searchUrlResults = reverse("jobs:friendResult")
        self.addFriendUrl = reverse("jobs:addFriend")

        self.userLogin ={
            "username":"jnk2022",
            "password":"N0tZenin~"
        }

        self.findFriend= {
            "option" :"name",
            "search" : 'Electr'
        }

        self.findFriendNotFound = {
            'requester': self.accountA.id,
            'requested':self.accountB.id,
            'dateSent' : date.today()
        }
    
    def testAddFriendSuccess(self):
        response1 = self.client.post(self.loginUrl, self.userLogin, format="text/html")
        self.assertEqual(response1.status_code, 302)
        user = auth.get_user(self.client)
        assert user.is_authenticated

        response = self.client.get(self.searchUrl, self.findFriendNotFound, format = 'text/html')
        self.assertEqual(response.status_code, 200)
        self.friendRequest = FriendRequest.objects.create (requester=self.accountA, requested = self.accountB, dateSent = date.today(),  accepted = False)


class UserFeaturesTests(TestCase):
    def setUp(self):
        self.login_url = reverse("jobs:login")
        self.ads_url = reverse("jobs:privacyAds")
        self.email_url = reverse("jobs:privacyEmails")
        self.sms_url = reverse("jobs:privacySMS")
        self.language_url = reverse("jobs:language")
        User.objects.create_user(username="testuser", first_name="Test", last_name="Tester", password="top_secret")

        self.user_login = {
            "username": "testuser",
            "password": "top_secret"
        }    
        self.emails = {
            "emails": "No",
        }
        self.ads = {
            "ads": "No", 
        }
        self.sms = {
            "sms":  "No"
        }
        self.language = {
            "language": "Spanish"
        }
    def test_guest_controls(self):
        response0 = self.client.post(self.login_url, self.user_login, format="text/html")
        self.assertEqual(response0.status_code, 302)
        user = auth.get_user(self.client)
        assert user.is_authenticated
        response1 = self.client.post(self.ads_url, self.ads, format="text/html")
        response2 = self.client.post(self.email_url, self.emails, format="text/html")
        response3 = self.client.post(self.sms_url, self.sms, format="text/html")
        self.assertEqual(response1.status_code, 200)
        self.assertContains(response1, 'No')
        
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, 'No')

        self.assertEqual(response3.status_code, 200)
        self.assertContains(response3, 'No')

    def test_language_selection(self):
        response0 = self.client.post(self.login_url, self.user_login, format="text/html")
        self.assertEqual(response0.status_code, 302)
        user = auth.get_user(self.client)
        assert user.is_authenticated
        response1 = self.client.post(self.language_url, self.language, format="text/html")
        self.assertContains(response1, 'Spanish')

class FriendProfileTests(TestCase):
    def setUp(self):
        self.login_url = reverse("jobs:login")
        self.friends_url = reverse("jobs:friends")
        self.get_friends_url = reverse("jobs:getFriends")
        self.friend_profile_url = reverse("jobs:friendProfile")

        # Set up the users for testing
        User.objects.create_user(username="johndoe", first_name="John", last_name="Doe", password="top_secret")
        User.objects.create_user(username="rockydbull", first_name="Rocky", last_name="Bull", password="GoBulls!")

        self.user_a = User.objects.get(username="johndoe")
        self.user_b = User.objects.get(username="rockydbull")

        # Set up the accounts for testing
        self.account_a = Account.objects.get(user=self.user_a)
        self.account_b = Account.objects.get(user=self.user_b)

        # Set fields in the account entries
        self.account_a.first_name = "John"
        self.account_a.last_name = "Doe"
        self.account_a.major = "Computer Science"
        self.account_a.university = "University of South Florida"
        self.account_a.save()

        self.account_b.first_name = "Rocky"
        self.account_b.last_name = "Bull"
        self.account_b.major = "English"
        self.account_b.university = "University of South Florida"
        self.account_b.save()

        self.friendship = Friendship.objects.create(user_one=self.account_a, user_two=self.account_b) # Make the friendship

        # Set up profiles for the accounts
        self.profile_a = Profile.objects.create(user=self.user_a, title="3rd Year Computer Science Student", about="This is a test", major="Computer Science", university="University of South Florida")
        self.profile_b = Profile.objects.create(user=self.user_b, title="4th Year English Student", about="Go Bulls!", major="English", university="University of South Florida")

        # In this test, the user logged in will be the one whose username is johndoe
        self.user_login = {
            "username": "johndoe",
            "password": "top_secret"
        }

    def test_friends_page_renders(self):
        response1 = self.client.post(self.login_url, self.user_login, format="text/html") 

        self.assertEqual(response1.status_code, 302) # A successful login will redirect (status code 302) to the homepage
        user = auth.get_user(self.client)
        assert user.username == "johndoe"

        response2 = self.client.get(self.friends_url)
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "friends/friends.html")

        response3 = self.client.get(self.get_friends_url).json() # A reqyest is made to the api/get-friends endpoint after oading the friends page

        expectedResponse = [
            {
                "friendship_id": self.friendship.id,
                "friend_id": self.friendship.user_two_id,
                "first_name": self.account_b.first_name,
                "last_name": self.account_b.last_name,
                "major": self.account_b.major,
                "university": self.account_b.university,
                "profile_id": self.profile_b.id
            }
        ]

        self.assertEqual(response3, expectedResponse) # Check that the response matches the expected response, so that friend's information would be displayed on the page

    def test_friends_profile_page_renders(self):
        response1 = self.client.post(self.login_url, self.user_login, format="text/html") 

        self.assertEqual(response1.status_code, 302) # A successful login will redirect (status code 302) to the homepage
        user = auth.get_user(self.client)
        assert user.username == "johndoe"

        response2 = self.client.get(self.friends_url)
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "friends/friends.html")

        response3 = self.client.get(self.get_friends_url).json() # A reqyest is made to the api/get-friends endpoint after oading the friends page
    
        expectedResponse = [
            {
                "friendship_id": self.friendship.id,
                "friend_id": self.friendship.user_two_id,
                "first_name": self.account_b.first_name,
                "last_name": self.account_b.last_name,
                "major": self.account_b.major,
                "university": self.account_b.university,
                "profile_id": self.profile_b.id
            }
        ]

        self.assertEqual(response3, expectedResponse) # Check that the response matches the expected response, so that friend's information would be displayed on the page

        response4 = self.client.get(self.friend_profile_url, {"id": self.profile_b.id})
        self.assertEqual(response4.status_code, 200)
        self.assertTemplateUsed(response4, "profile/profileView.html")
        self.assertContains(response4, "4th Year English Student") # Checking the correct title was included for that friend's profile

class ProfileCheckTest(TestCase):
    def setUp(self):
        self.loginUrl = reverse("jobs:login")
        self.profile_url = reverse("jobs:profile")
        self.profileEdit_url = reverse("jobs:profileEdit")

        # Set up the users for testing
        User.objects.create_user(username="johndoe", first_name="John", last_name="Doe", password="top_secret")
        User.objects.create_user(username="johnpoe", first_name="John", last_name="Poe", password="secret_top")

        self.user_a = User.objects.get(username="johndoe")
        self.user_b = User.objects.get(username="johnpoe")

        # Set up profiles for the accounts
        self.profile_a = Profile.objects.create(user=self.user_a, title="3rd Year Computer Science Student", about="This is a test", major="Computer Science", university="University of South Florida", degree="Bachelors of Science", yearsAttended="4")
        self.profile_b = Profile.objects.create(user=self.user_b, title="4th Year Computer Science Student", university="University of South Florida")

        # In this test, the user logged in will be the one whose username is johndoe
        self.user_login = {
            "username": "johndoe",
            "password": "top_secret"
        }
        
        self.user_login2 = {
            "username": "johnpoe",
            "password": "secret_top"
        }
        
        
    def test_profile_page_renders(self):
        response1 = self.client.post(self.loginUrl, self.user_login, format="text/html")
        
        self.assertEqual(response1.status_code, 302)# successful login with code 302
        user = auth.get_user(self.client)
        assert user.username == "johndoe"

        response2 = self.client.get(self.profile_url)
        self.assertEqual(response2.status_code, 200)# checks to see that profile page loads


    def test_profile_appear(self):
        response1 = self.client.post(self.loginUrl, self.user_login, format="text/html")
        
        self.assertEqual(response1.status_code, 302)# successful login with code 302
        user = auth.get_user(self.client)
        assert user.username == "johndoe"

        #checks that each individual item is set to the proper element
        self.assertEqual(self.profile_a.title, "3rd Year Computer Science Student")
        self.assertEqual(self.profile_a.about, "This is a test")
        self.assertEqual(self.profile_a.major, "Computer Science")
        self.assertEqual(self.profile_a.university, "University of South Florida")
        self.assertEqual(self.profile_a.degree, "Bachelors of Science")
        self.assertEqual(self.profile_a.yearsAttended, "4")

    def test_partial_profile(self):
        response1 = self.client.post(self.loginUrl, self.user_login2, format="text/html")
        
        self.assertEqual(response1.status_code, 302) # successful login with code 302
        user = auth.get_user(self.client)
        assert user.username == "johnpoe"
        
        self.assertEqual(self.profile_b.title, "4th Year Computer Science Student")
        self.assertEqual(self.profile_b.about, "")
        self.assertEqual(self.profile_b.major, "")
        self.assertEqual(self.profile_b.university, "University of South Florida")
        self.assertEqual(self.profile_b.degree, "")

class JobsTest(TestCase):
    def setUp(self):
        self.login_url = reverse("jobs:login")
        self.logout_url = reverse("jobs:logout")
        self.job_post_url = reverse("jobs:postjob")
        self.job_section_url = reverse("jobs:jobs")

        # Set up the users for testing
        User.objects.create_user(username="johndoe", first_name="John", last_name="Doe", password="top_secret")
        User.objects.create_user(username="rockydbull", first_name="Rocky", last_name="Bull", password="top_secret")

        self.user_login = {
            "username": "johndoe",
            "password": "top_secret"
        }

        self.user_login2 = {
            "username": "rockydbull",
            "password": "top_secret"
        }

        self.job_post = {
            "title": "Software Engineer",
            "employer": "InCollege",
            "description": "Be part of an amazing dev team. Develop applications to help college students connect with their peers and find a job after graduation.",
            "location": "Tampa, FL",
            "salary": 80000
        }

    def test_jobs_max_is_10(self):
        response1 = self.client.post(self.login_url, self.user_login, format="text/html")
        
        self.assertEqual(response1.status_code, 302) # Successful login with code 302

        user = auth.get_user(self.client)
        assert user.username == "johndoe"

        for i in range(0, 10): # Post a job 10 times
            self.job_post["title"] = "Software Engineer " + str(i + 1)
            self.client.post(self.job_post_url, self.job_post, format="text/html")

        for i in range(0, 10): # Check that all 10 jobs are in database
            title = "Software Engineer " + str(i + 1)
            self.assertTrue(Job.objects.filter(title=title).exists())
        
    def test_can_see_jobs(self):
        response1 = self.client.post(self.login_url, self.user_login, format="text/html")
        
        self.assertEqual(response1.status_code, 302) # Successful login with code 302

        user = auth.get_user(self.client)
        assert user.username == "johndoe"

        self.client.post(self.job_post_url, self.job_post, format="text/html")

        response2 = self.client.get(self.logout_url)
        self.assertEqual(response2.status_code, 200) # Logout was successful

        response3 = self.client.post(self.login_url, self.user_login2, format="text/html") # Second user logs in to be able to apply for the job the first user posted

        self.assertEqual(response3.status_code, 302)
        
        user = auth.get_user(self.client)
        assert user.username == "rockydbull"

        response4 = self.client.get(self.job_section_url)

        self.assertEqual(response4.status_code, 200)
        self.assertContains(response4, "Applied")
        self.assertContains(response4, "Saved")
        self.assertContains(response4, "Not Applied")

        self.assertContains(response4, "Software Engineer")
        self.assertContains(response4, "Apply")

class MembershipTypesTest(TestCase):
    def setUp(self):
        self.login_url = reverse("jobs:login")
        self.membership_selection_url = reverse("jobs:accountSelection")

        # Set up the user for testing
        self.user = User.objects.create_user(username="johndoe", first_name="John", last_name="Doe", password="top_secret")

        self.user_login = {
            "username": "johndoe",
            "password": "top_secret"
        }

        self.standard_membership_selection = {
            "choice": "Standard"
        }
        
        self.plus_membership_selection = {
            "choice": "Plus"
        }

    def test_membership_page_renders(self):
        response1 = self.client.post(self.login_url, self.user_login, format="text/html")
        
        self.assertEqual(response1.status_code, 302) # Successful login with code 302

        user = auth.get_user(self.client)
        assert user.username == "johndoe"

        response2 = self.client.get(self.membership_selection_url) # Go to membershiip selection page

        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "registration/plusAcc.html")

    def test_membership_selection_standard(self):
        response1 = self.client.post(self.login_url, self.user_login, format="text/html")
        
        self.assertEqual(response1.status_code, 302) # Successful login with code 302

        user = auth.get_user(self.client)
        assert user.username == "johndoe"

        response2 = self.client.get(self.membership_selection_url) # Go to membershiip selection page

        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "registration/plusAcc.html")

        response3 = self.client.post(self.membership_selection_url, self.standard_membership_selection, format="text/html")

        self.assertEqual(response3.status_code, 302)

        account = Account.objects.get(user=self.user)
        
        self.assertEqual(account.plusAccount, "Standard")

    def test_membership_selection_plus(self):
        response1 = self.client.post(self.login_url, self.user_login, format="text/html")
        
        self.assertEqual(response1.status_code, 302) # Successful login with code 302

        user = auth.get_user(self.client)
        assert user.username == "johndoe"

        response2 = self.client.get(self.membership_selection_url) # Go to membershiip selection page

        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "registration/plusAcc.html")

        response3 = self.client.post(self.membership_selection_url, self.plus_membership_selection, format="text/html")

        self.assertEqual(response3.status_code, 302)

        account = Account.objects.get(user=self.user)

        self.assertEqual(account.plusAccount, "Plus")
    
class OutputAPITest(TestCase):
    def setUp(self):

        self.home = reverse("jobs:homepage")
        self.login_url = reverse("jobs:login")

        #Create fake user info
        self.saulUser = User.objects.create_user(username="betterCall", first_name="Saul", last_name="Goodman", password="JimmyMcGill!")
        Connections.objects.create(user = self.saulUser)

        self.user_login = {
            "username":"betterCall",
            "password":"JimmyMcGill!"
        }

        self.job1 = Job.objects.create(title= "Software Engineer",
            employer="InCollege",
            description="Be part of an amazing dev team. Develop applications to help college students connect with their peers and find a job after graduation.",
            location="Tampa, FL",
            salary=80000)
        
        self.job2 = Job.objects.create(title= "Front-end Developer",
            employer="InCollege",
            description="Be part of an amazing dev team. Develop applications to help college students connect with their peers and find a job after graduation.",
            location="Tampa, FL",
            salary=70000)
        self.saveJob1 = jobStatus.objects.create(user=self.user, associatedJob = self.job1, saved=True, applied = False)
        self.saveJob2 = jobStatus.objects.create(user=self.user, associatedJob = self.job1, saved=False, applied = True)

        self.profile = Profile.objects.create()
        #General Links

        #First is the reverse, second is the text in the html, third is the html path
        self.apiOutput = [(reverse("jobs:job_text"), "MyCollege Jobs", "MyCollege_job.txt"), 
                            (reverse("jobs:profiles_text"), "MyCollege Profiles", "MyCollege_profiles.txt"),
                            (reverse("jobs:users_text"), "MyCollege Users", "MyCollege_users.txt"),
                            (reverse("jobs:appliedJobs_text"), "MyCollege Applied Jobs", "MyCollege_appliedJobs.txt"),
                            (reverse("jobs:savedJobs_text"), "MyCollege_savedJobs.txt")]
                            
    def downloadTest(self):
        self.login()
        response = self.client.get(self.home)
        #for each link
        for ref in self.apiOutput:
            #Check html has the page
            self.assertContains(response, '<a href="%s">%s</a>' % (ref[0], ref[1]))

            response2 = self.client.get(ref[0])

            #check that it uses the right template and that it loads correctly
            attachment = "attachment; filename=" + ref[2]
            self.assertEquals(response.get('Content-Disposition'), attachment)

