from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from jobs.forms import jobPosting

from . import views
app_name = 'jobs'
urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.homepage, name='homepage'), #default page, not logged in
    path('register/', views.registerPage, name='register'),
    path('successVideo/', views.watchVideo, name="successvideo"),
    path('home/', views.index, name="home"), #user homepage,
    path('post-a-job/', views.postJob, name="postjob"),
    path('job-section/', views.jobSection, name="jobs"),
    path('logout/', views.logoutUser, name="logout"),
    path('skill-section', views.skillSection),
    path('login/', views.loginPage, name="login"),

    path('connect-section/', views.connectSection, name = "connectionSection"),
    path('search-results/', views.searchResults, name="searchResult"),
    path('browse-incollege/', views.browseIncollege, name="browse"),
    path('business-solutions/', views.businessSolutions, name="businessSol"),
    path('directories/', views.directories, name="directories"),

    path('general/about', views.genAbout, name="genAbout"),
    path('general/blog', views.genBlog, name="genBlog"),
    path('general/careers', views.genCareers, name="genCareers"),
    path('general/developers', views.genDev, name="genDevelopers"),
    path('general/help-center', views.genHelp, name="genHelp"),
    path('general/press', views.genPress, name="genPress"),

    path('important/copyright', views.copyright, name="copyright"),
    path('important/brand', views.brandPolicy, name="brandPol"),
    path('important/cookie', views.cookiePolicy, name="cookiePol"),
    path('important/user-agreement', views.userAgreement, name="userAgr"),
    path('important/accessibility', views.accessibility, name="accessibility"),
    path('important/about', views.about, name="about"),   
    path('important/language', views.language, name="language"),
    path('important/emails', views.privacyEmails, name="privacyEmails"),
    path('important/sms', views.privacySMS, name="privacySMS"),
    path('important/ads', views.privacyAds, name="privacyAds"),

    path('find-friends/', views.findFriendsPage, name="findFriends"),
    path('api/find-friends', views.findFriends, name = "friendResult"),
    path('api/add-friend', views.addFriend, name = "addFriend"),
    path('api/accept-friend', views.acceptFriend),
    path('api/decline-friend', views.declineFriendRequest),
    path('api/remove-friend', views.removeFriend),
    path('friends/', views.friendsPage, name="friends"),
    path('api/get-friends', views.getFriends, name="getFriends"),
    path('api/get-pending-friends', views.getPendingFriends),

    path('profile/', views.profileView, name='profile'),
    path('profile/edit/', views.profileEdit, name='profileEdit'),
    path('profile/addJob', views.addWorkExperience, name='addWorkExperience'),
    path('friend/profile', views.friendProfileView, name='friendProfile'),
    
    path('messages/messageForm/<int:pk>', views.messageForm, name='messageForm'),
    path('messages/', views.MessageView, name='MessageView'),
    path('inbox/', views.MessageInbox, name='MessageInbox'),
    path('messages/processMessage/<int:pk>', views.ProcessMessage, name='ProcessMessage'),

    path('applyForJob/<int:pk>', views.applyForJob, name="applyJob"),
    path('saveJob/<int:pk>', views.saveJob, name="saveJob"),
    path('unsave/<int:pk>', views.unsaveJob, name="unsave"),
    path('displayJob/<int:jobID>/<str:jobName>', views.displayJob, name="displayJob"),
    path('account-selection', views.accountSelection, name = "accountSelection"),

    path('job_text/', views.job_text, name='job_text'),
    path('profiles_text/', views.profiles_text, name='profiles_text'),
    path('users_text/', views.users_text, name='users_text'),
    path('training_text/', views.training_text, name='training_text'),
    path('appliedJobs_text/', views.appliedJobs_text, name='appliedJobs_text'),
    path('savedJobs_text/', views.savedJobs_text, name='savedJobs_text'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

#"/profile/edit"