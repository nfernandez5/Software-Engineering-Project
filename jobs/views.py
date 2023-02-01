from pickle import FALSE
from queue import Empty
from django.shortcuts import  get_object_or_404, render, redirect
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views import generic
from .forms import *
from django.contrib import messages
from django.views.generic.edit import CreateView, DeleteView, UpdateView, DeletionMixin
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse, HttpResponse
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from datetime import *
def loginPage(request):
    form =loginForm()
    if request.method == 'POST':
        form = loginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],)
            if user is not None:
                login(request,user)
                return HttpResponseRedirect('/home')
            else:
                # return redirect ('jobs/login.html')
                messages.warning(request, f'Login error. The email address and/or password is incorrect.')
    context = {'form': form}
    return render(request, 'jobs/login.html', context)

#homepage for user that successfully logged in
@login_required(login_url='/login/')
def index(request):
    return render(request, 'jobs/index.html')

#default homepage, for user that has not logged in
def homepage(request):
	return render(request, 'jobs/base.html')

def registerPage(request):
    if request.user.is_authenticated:
        messages.info(request, 'You have already signed in!')
        return HttpResponseRedirect('/home')
    else:
        form = UserForm()
        if request.method == 'POST':
            form = UserForm(request.POST)
            if form.is_valid():
                new_user = form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)
                connectionForm = baseConnectionForm({'user' : new_user})
                if connectionForm.is_valid():
                    connectionForm.save()
                new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
                login(request, new_user)
                return HttpResponseRedirect('/account-selection')

        context = {'form': form}
        return render(request, 'registration/register.html', context)

#show success video
def watchVideo(request):
	return render(request, 'jobs/successVideo.html')

"""
    exists=Profile.objects.filter(user=request.user).exists()

    # Profile does exist
    if exists:
        userProfile = Profile.objects.get(user=request.user)
        if workExperience.objects.filter(profile=userProfile).exists():
            experiences = workExperience.objects.filter(profile=userProfile)
"""
@login_required(login_url='/login/')
def jobSection(request):
    context = {}
    savedAppliedJobs = jobStatus.objects.filter(user = request.user).values("associatedJob")
    jobListings = Job.objects.exclude(postedBy = request.user).exclude(id__in=savedAppliedJobs)
    context["jobListings"] = jobListings
    context["savedJobs"] = jobStatus.objects.filter(user = request.user).filter(saved = True)
    context["appliedJobs"] = jobStatus.objects.filter(user = request.user).filter(applied = True)
    context['totalJobsApplied'] = jobStatus.objects.filter(user = request.user).filter(applied = True).count()
    jobsApplied = jobStatus.objects.filter(user = request.user.id)  
    lastJobApplied = jobStatus.objects.filter(user=request.user, applied=True).reverse()
    #check first obj from list (newest job applied)
    if lastJobApplied:
        # firstTime = jobApplication.objects.filter(appliedUser=request.user)[0].appliedTime
        lastApplied = lastJobApplied[0].getTimeCreated()
    else: #list empty => hasnt applied for any
        lastApplied =8
        #new job posted notif check
    user = User.objects.filter(id=request.user.id)[0]
    lastLogin = user.last_login
    if Job.objects.last():
        lastJob = utc.localize(Job.objects.last().getTimeCreated())
        if lastLogin < lastJob:
            context['newJobs'] = True
        else:
            context['newJobs'] = False
    else:
        context['newJobs'] = False
    context['lastApplied'] = lastApplied
    context ['jobsAppliedCheck'] = jobsApplied
    return render(request, 'jobs/job-section.html', context)
@login_required(login_url='/login/')
def applyForJob(request, pk):
    context = {'form': jobApplicationForm()}
    if request.method == 'POST':
        form = jobApplicationForm(request.POST)
        if form.is_valid():
            form.instance.appliedJob = Job.objects.get(id = pk)
            form.instance.appliedUser = request.user
            try:
                form.save() # Save profile to Database
            except:
                messages.error(request, "Job already Exists")
                return redirect('/job-section/') # Redirect user to viewing the job section

            #Update Job status. Done if applying from the Saved Tab
            if jobStatus.objects.filter(associatedJob = pk).exists():
                tempJob = jobStatus.objects.get(associatedJob = pk)
                tempJob.applied = True
                tempJob.saved = False
                tempJob.save()
            else:
                savedJob = jobStatus.objects.create(user = request.user, associatedJob = Job.objects.get(id = pk), saved = False, applied = True)
                savedJob.save()
            return redirect('/job-section/') # Redirect user to viewing the job section

    return render(request, 'jobs/applyForJob.html', context)
@login_required(login_url='/login/')
def saveJob(request, pk):
    if request.method == 'POST':
        savedJob = jobStatus.objects.create(user = request.user, associatedJob = Job.objects.get(id = pk), saved = True, applied = False)
        try:
            savedJob.save() # Save profile to Database
        except:
            messages.error(request, "Job already Exists")

    return redirect('/job-section/') # Redirect user to viewing the job section
@login_required(login_url='/login/')
def unsaveJob(request, pk):
    if request.method == 'POST':
        try:
            jobStatus.objects.get(id = pk).delete()
        except:
            messages.error(request, "Job already Exists")

    return redirect('/job-section/') # Redirect user to viewing the job section
@login_required(login_url='/login/')
def postJob(request):
    form = jobPosting()
    if request.method == 'POST':
        form = jobPosting(request.POST)
        if form.is_valid():
            form.instance.postedBy = request.user #postedBy field filled in here
            form.save()
            return redirect('/job-section/')
    context = {'form': form}
    return render(request, 'jobs/post-a-job.html', context)

#not required now, but add in to check user authenticated view and guest view
def logoutUser(request):
    logout(request)
    return render(request, 'jobs/base.html')

#only display the list of skill for now
@login_required(login_url='/login/')
def skillSection(request):
    Skills= Skill.objects.all()
    return render(request, 'jobs/skill-section.html', {'Skills': Skills})
@login_required(login_url='/login/')
def connectSection(request):
    form = searchForm()
    if request.method == 'POST':
        form = searchForm(request.POST)
        if form.is_valid():
                user = User.objects.filter(first_name = form.cleaned_data['first_name'], last_name = form.cleaned_data['last_name'])
                if user.exists():
                    if request.user.is_authenticated:
                        connectToUser(request, user.first())
                    
                    return render(request, 'jobs/search-results.html', {'value': 1})
                else:
                    return render(request, 'jobs/search-results.html', {'value': 2})
        else:
            return redirect ('jobs/search.html', {'error_message': "Error in submitting form"})
    context = {'form': form}
    return render(request, 'jobs/search.html', context)
@login_required(login_url='/login/')
def connectToUser(request, newConnection):
    session_user = request.user
    if Connections.objects.filter(user = session_user.id).exists():
        check_connection = Connections.objects.get(user = session_user.id)
        is_connected = False
        for item in check_connection.another_user.all():
            if item == newConnection:
                is_connected = True
        if newConnection != session_user and not is_connected:
            check_connection.another_user.add(newConnection.id)
    
    return HttpResponseRedirect('/home')
@login_required(login_url='/login/')
def displayJob(request, jobID, jobName):
    jobToDisplay = Job.objects.get(id = jobID)
    jobPoster = User.objects.get(id = jobToDisplay.postedBy.id)
    return render(request, 'jobs/displayJob.html', {"job": jobToDisplay, "poster": jobPoster})
@login_required(login_url='/login/')
def searchResults(request):
        return render(request, 'jobs/search-results.html')

#useful-links
def browseIncollege(request):
    return render(request, 'useful-links/browse-incollege.html')

def businessSolutions(request):
    return render(request, 'useful-links/business-solutions.html')

def directories(request):
    return render(request, 'useful-links/directories.html')

#general-links
def genAbout(request):
    return render(request, 'useful-links/general-links/about.html')

def genBlog(request):
    return render(request, 'useful-links/general-links/blog.html')

def genCareers(request):
    return render(request, 'useful-links/general-links/careers.html')

def genDev(request):
    return render(request, 'useful-links/general-links/developers.html')

def genHelp(request):
    return render(request, 'useful-links/general-links/help-center.html')

def genPress(request):
    return render(request, 'useful-links/general-links/press.html')

#important-links
def copyright(request):
    return render(request, 'important-links/copyright.html')

def brandPolicy(request):
    return render(request, 'important-links/brand-policy.html')

def accessibility(request):
    return render(request, 'important-links/accessibility.html')

def userAgreement(request):
    return render(request, 'important-links/user-agreement.html')

def cookiePolicy(request):
    return render(request, 'important-links/cookie-policy.html')

def about(request):
    return render(request, 'important-links/about.html')

@login_required(login_url='/login/')
def language(request):
    language = ['English', 'Spanish']
    exists=Account.objects.filter(user=request.user).exists()
    
    account_language = None
    if exists:
        account_language = Account.objects.get(user=request.user)
    if request.method=='GET':
        return render(request, 'important-links/language.html', {'language': language, 'account_language': account_language})
    else:
        language = request.POST['language']
        if exists:
            account_language.language = language
            account_language.save()
        else:
            Account.objects.create(user=request.user, language=language)
    messages.success(request, 'Changes saved')
    return render(request, 'important-links/language.html', {'language': language, 'account_language': account_language})

@login_required(login_url='/login/')
def privacyEmails(request):
    emails = ['Yes', 'No']
    exists=Account.objects.filter(user=request.user).exists()
    
    account_emails = None
    if exists:
        account_emails = Account.objects.get(user=request.user)
    if request.method=='GET':
        return render(request, 'important-links/emails.html', {'emails': emails, 'account_emails': account_emails})
    else:
        emails = request.POST['emails']
        
        if exists:
            account_emails.emails = emails
            account_emails.save()
                       
        else:
            Account.objects.create(user=request.user, emails=emails)
    messages.success(request, 'Changes saved')
    return render(request, 'important-links/emails.html', {'emails': emails, 'account_emails': account_emails})

@login_required(login_url='/login/')
def privacySMS(request):
    sms = ['Yes', 'No']
    exists=Account.objects.filter(user=request.user).exists()
    
    account_sms = None
    
    if exists:
        account_sms = Account.objects.get(user=request.user)

    if request.method=='GET':
        return render(request, 'important-links/emails.html', {'sms': sms, 'account_sms': account_sms})
    else:
        sms = request.POST['sms']
        
        if exists:
            account_sms.sms = sms
            account_sms.save()
                       
        else:
            Account.objects.create(user=request.user, sms=sms)
    messages.success(request, 'Changes saved')
    return render(request, 'important-links/emails.html', {'sms': sms, 'account_sms': account_sms})

@login_required(login_url='/login/')
def privacyAds(request):
    ads = ['Yes', 'No']
    exists=Account.objects.filter(user=request.user).exists()
    
    account_ads = None
    
    if exists:
        account_ads = Account.objects.get(user=request.user)

    if request.method=='GET':
        return render(request, 'important-links/emails.html', {'ads': ads, 'account_ads': account_ads})
    else:
        ads = request.POST['ads']
        
        if exists:
            account_ads.ads = ads
            account_ads.save()
                       
        else:
            Account.objects.create(user=request.user, ads=ads)
    messages.success(request, 'Changes saved')
    return render(request, 'important-links/emails.html', {'ads': ads, 'account_ads': account_ads})

@login_required(login_url='/login/')
def findFriendsPage(request):
    return render(request, 'friends/friend-search.html')

@login_required(login_url='/login/')
def findFriends(request):
    category = request.POST.get('category')
    search = request.POST.get('text')
    response = []
    if category == "name":
        if " " in search:
            firstName = search.split(" ")[0]
            lastName = search.split(" ")[1]
            users = User.objects.filter(first_name__istartswith=firstName, last_name__istartswith=lastName).exclude(id=request.user.id).values()
            accounts = []
            for user in users:
                account = Account.objects.filter(user=user['id']).values()
                accounts.extend(account)
        else:
            users = User.objects.filter(first_name__istartswith=search).exclude(id=request.user.id).values()
            accounts = []
            for user in users:
                account = Account.objects.filter(user=user['id']).values()
                accounts.extend(account)
        response.extend(accounts)
    elif category == "university":
        accounts = Account.objects.filter(university__istartswith=search).exclude(user=request.user.id).values()
        response.extend(accounts)
    else:
        accounts = Account.objects.filter(major__istartswith=search).exclude(user=request.user.id).values()
        response.extend(accounts)
    
    for account in response: # Check if there is a pending friend request
        requesterAccount = Account.objects.get(user=request.user.id)
        friendRequest = FriendRequest.objects.filter(requester=requesterAccount, requested=account['id'], accepted__isnull=True).values()
        if friendRequest.count() > 0: # There is a pending friend request
            account['request_pending'] = True
        else:
            account['request_pending'] = False

    return JsonResponse(response, safe=False)

@login_required(login_url='/login/')
def addFriend(request):
    requestedUserID = request.POST.get('requestedUserID')
    requesterAccount = Account.objects.get(user=request.user.id)
    requestedAccount = Account.objects.get(user=requestedUserID)
    FriendRequest.objects.create(requester=requesterAccount, requested=requestedAccount, dateSent=date.today())
    friendRequest = FriendRequest.objects.filter(requester=request.user.id, requested=requestedUserID).values()
    return JsonResponse(friendRequest[0], safe=False)

@login_required(login_url='/login/')
def declineFriendRequest(request):
    requesterUserID = request.POST.get('requesterUserID')
    friendRequestID = request.POST.get('friendRequestID')
    requesterAccount = Account.objects.get(user=requesterUserID)
    requestedAccount = Account.objects.get(user=request.user.id)

    friendRequest = FriendRequest.objects.get(id=friendRequestID, requester=requesterAccount, requested=requestedAccount)
    friendRequest.accepted = False
    friendRequest.save()

    userAccount = requestedAccount

    friends1 = Friendship.objects.filter(user_one=userAccount).values()
    friends2 = Friendship.objects.filter(user_two=userAccount).values()
    response = {}
    response['existingFriends'] = []
    response['pendingFriends'] = []

    for friend in friends1:
        friendAccount = Account.objects.get(user=friend['user_two_id'])
        responseEntry = {}
        responseEntry['friendship_id'] = friend['id']
        responseEntry['friend_id'] = friend['user_two_id']
        responseEntry['first_name'] = friendAccount.first_name
        responseEntry['last_name'] = friendAccount.last_name
        responseEntry['major'] = friendAccount.major
        responseEntry['university'] = friendAccount.university
        responseEntry['profile_id'] = -1 # If the friend has not made a profile, the ID will be -1
        try:
            friendProfile = Profile.objects.get(user=friend['user_two_id'])
        except ObjectDoesNotExist:
            friendProfile = None
        if friendProfile != None:
            responseEntry['profile_id'] = friendProfile.id
        response['existingFriends'].append(responseEntry)
    
    for friend in friends2:
        friendAccount = Account.objects.get(user=friend['user_one_id'])
        responseEntry = {}
        responseEntry['friendship_id'] = friend['id']
        responseEntry['friend_id'] = friend['user_one_id']
        responseEntry['first_name'] = friendAccount.first_name
        responseEntry['last_name'] = friendAccount.last_name
        responseEntry['major'] = friendAccount.major
        responseEntry['university'] = friendAccount.university
        responseEntry['profile_id'] = -1
        try:
            friendProfile = Profile.objects.get(user=friend['user_one_id'])
        except ObjectDoesNotExist:
            friendProfile = None
        if friendProfile != None:
            responseEntry['profile_id'] = friendProfile.id
        response['existingFriends'].append(responseEntry)

    pendingFriends = FriendRequest.objects.filter(requested=userAccount, accepted__isnull=True).values()

    for pendingFriend in pendingFriends:
        pendingFriendAccount = Account.objects.get(user=pendingFriend['requester_id'])
        responseEntry = {}
        responseEntry['request_id'] = pendingFriend['id']
        responseEntry['requester_id'] = pendingFriend['requester_id']
        responseEntry['first_name'] = pendingFriendAccount.first_name
        responseEntry['last_name'] = pendingFriendAccount.last_name
        responseEntry['major'] = pendingFriendAccount.major
        responseEntry['university'] = pendingFriendAccount.university
        response['pendingFriends'].append(responseEntry)

    return JsonResponse(response, safe=False)

@login_required(login_url='/login/')
def acceptFriend(request):
    requesterUserID = request.POST.get('requesterUserID')
    friendRequestID = request.POST.get('friendRequestID')
    requesterAccount = Account.objects.get(user=requesterUserID)
    requestedAccount = Account.objects.get(user=request.user.id)

    friendRequest = FriendRequest.objects.get(id=friendRequestID, requester=requesterAccount, requested=requestedAccount)
    friendRequest.accepted = True
    friendRequest.dateAccepted = date.today()
    friendRequest.save()

    Friendship.objects.create(user_one=requesterAccount, user_two=requestedAccount)

    userAccount = requestedAccount

    friends1 = Friendship.objects.filter(user_one=userAccount).values()
    friends2 = Friendship.objects.filter(user_two=userAccount).values()
    response = {} # Response will be a dictionary with updated existing friends and pending friends
    response['existingFriends'] = []
    response['pendingFriends'] = []

    for friend in friends1:
        friendAccount = Account.objects.get(user=friend['user_two_id'])
        responseEntry = {}
        responseEntry['friendship_id'] = friend['id']
        responseEntry['friend_id'] = friend['user_two_id']
        responseEntry['first_name'] = friendAccount.first_name
        responseEntry['last_name'] = friendAccount.last_name
        responseEntry['major'] = friendAccount.major
        responseEntry['university'] = friendAccount.university
        responseEntry['profile_id'] = -1
        try:
            friendProfile = Profile.objects.get(user=friend['user_two_id'])
        except ObjectDoesNotExist:
            friendProfile = None
        if friendProfile != None:
            responseEntry['profile_id'] = friendProfile.id
        response['existingFriends'].append(responseEntry)

    for friend in friends2:
        friendAccount = Account.objects.get(user=friend['user_one_id'])
        responseEntry = {}
        responseEntry['friendship_id'] = friend['id']
        responseEntry['friend_id'] = friend['user_one_id']
        responseEntry['first_name'] = friendAccount.first_name
        responseEntry['last_name'] = friendAccount.last_name
        responseEntry['major'] = friendAccount.major
        responseEntry['university'] = friendAccount.university
        responseEntry['profile_id'] = -1
        try:
            friendProfile = Profile.objects.get(user=friend['user_one_id'])
        except ObjectDoesNotExist:
            friendProfile = None
        if friendProfile != None:
            responseEntry['profile_id'] = friendProfile.id
        response['existingFriends'].append(responseEntry)
    
    pendingFriends = FriendRequest.objects.filter(requested=userAccount, accepted__isnull=True).values()

    for pendingFriend in pendingFriends:
        pendingFriendAccount = Account.objects.get(user=pendingFriend['requester_id'])
        responseEntry = {}
        responseEntry['request_id'] = pendingFriend['id']
        responseEntry['requester_id'] = pendingFriend['requester_id']
        responseEntry['first_name'] = pendingFriendAccount.first_name
        responseEntry['last_name'] = pendingFriendAccount.last_name
        responseEntry['major'] = pendingFriendAccount.major
        responseEntry['university'] = pendingFriendAccount.university
        response['pendingFriends'].append(responseEntry)

    return JsonResponse(response, safe=False)

@login_required(login_url='/login/')
def removeFriend(request):
    friendshipID = request.POST.get('friendshipID')
    friendship = Friendship.objects.get(id=friendshipID)
    friendship.delete() # Delete friend

    userAccount = Account.objects.get(user=request.user.id)
    friends1 = Friendship.objects.filter(user_one=userAccount).values()
    friends2 = Friendship.objects.filter(user_two=userAccount).values()
    response = [] # Response will be updated friends

    for friend in friends1:
        friendAccount = Account.objects.get(user=friend['user_two_id'])
        responseEntry = {}
        responseEntry['friendship_id'] = friend['id']
        responseEntry['friend_id'] = friend['user_two_id']
        responseEntry['first_name'] = friendAccount.first_name
        responseEntry['last_name'] = friendAccount.last_name
        responseEntry['major'] = friendAccount.major
        responseEntry['university'] = friendAccount.university
        responseEntry['profile_id'] = -1
        try:
            friendProfile = Profile.objects.get(user=friend['user_two_id'])
        except ObjectDoesNotExist:
            friendProfile = None
        if friendProfile != None:
            responseEntry['profile_id'] = friendProfile.id
        response.append(responseEntry)

    for friend in friends2:
        friendAccount = Account.objects.get(user=friend['user_one_id'])
        responseEntry = {}
        responseEntry['friendship_id'] = friend['id']
        responseEntry['friend_id'] = friend['user_one_id']
        responseEntry['first_name'] = friendAccount.first_name
        responseEntry['last_name'] = friendAccount.last_name
        responseEntry['major'] = friendAccount.major
        responseEntry['university'] = friendAccount.university
        responseEntry['profile_id'] = -1
        try:
            friendProfile = Profile.objects.get(user=friend['user_one_id'])
        except ObjectDoesNotExist:
            friendProfile = None
        if friendProfile != None:
            responseEntry['profile_id'] = friendProfile.id
        response.append(responseEntry)

    return JsonResponse(response, safe=False)

@login_required(login_url='/login/')
def friendsPage(request):
    context = {}
    user = User.objects.filter(id = request.user.id)[0]
    lastUserLogin = user.last_login
    newUserObj = User.objects.filter().reverse()[0]
    newUserSignup = newUserObj.date_joined
    if newUserSignup < lastUserLogin:
        context['newUser'] = True
    else:
        context['newUser'] = False
    
    return render(request, 'friends/friends.html', context)

@login_required(login_url='/login/')
def getFriends(request):
    userAccount = Account.objects.get(user=request.user.id)
    friends1 = Friendship.objects.filter(user_one=userAccount).values()
    friends2 = Friendship.objects.filter(user_two=userAccount).values()
    response = []

    for friend in friends1:
        friendAccount = Account.objects.get(user=friend['user_two_id'])
        responseEntry = {}
        responseEntry['friendship_id'] = friend['id']
        responseEntry['friend_id'] = friend['user_two_id']
        responseEntry['first_name'] = friendAccount.first_name
        responseEntry['last_name'] = friendAccount.last_name
        responseEntry['major'] = friendAccount.major
        responseEntry['university'] = friendAccount.university
        responseEntry['profile_id'] = -1
        try:
            friendProfile = Profile.objects.get(user=friend['user_two_id'])
        except ObjectDoesNotExist:
            friendProfile = None
        if friendProfile != None:
            responseEntry['profile_id'] = friendProfile.id
        response.append(responseEntry)

    for friend in friends2:
        friendAccount = Account.objects.get(user=friend['user_one_id'])
        responseEntry = {}
        responseEntry['friendship_id'] = friend['id']
        responseEntry['friend_id'] = friend['user_one_id']
        responseEntry['first_name'] = friendAccount.first_name
        responseEntry['last_name'] = friendAccount.last_name
        responseEntry['major'] = friendAccount.major
        responseEntry['university'] = friendAccount.university
        responseEntry['profile_id'] = -1
        try:
            friendProfile = Profile.objects.get(user=friend['user_one_id'])
        except ObjectDoesNotExist:
            friendProfile = None
        if friendProfile != None:
            responseEntry['profile_id'] = friendProfile.id
        response.append(responseEntry)

    return JsonResponse(response, safe=False)

@login_required(login_url='/login/')
def getPendingFriends(request):
    userAccount = Account.objects.get(user=request.user.id)
    pendingFriends = FriendRequest.objects.filter(requested=userAccount, accepted__isnull=True).values()
    response = []
    for pendingFriend in pendingFriends:
        pendingFriendAccount = Account.objects.get(user=pendingFriend['requester_id'])
        responseEntry = {}
        responseEntry['request_id'] = pendingFriend['id']
        responseEntry['requester_id'] = pendingFriend['requester_id']
        responseEntry['first_name'] = pendingFriendAccount.first_name
        responseEntry['last_name'] = pendingFriendAccount.last_name
        responseEntry['major'] = pendingFriendAccount.major
        responseEntry['university'] = pendingFriendAccount.university
        response.append(responseEntry)
    return JsonResponse(response, safe=False)

@login_required(login_url='/login/')
def profileView(request):
    exists=Profile.objects.filter(user=request.user).exists()

    # Profile does exist
    if exists:
        userProfile = Profile.objects.get(user=request.user)
        if workExperience.objects.filter(profile=userProfile).exists():
            experiences = workExperience.objects.filter(profile=userProfile)
            return render(request, 'profile/profileView.html', {'profile': userProfile, 'experiences': experiences})
        else:
            return render(request, 'profile/profileView.html', {'profile': userProfile})

    #profile does not exist
    return render(request, 'profile/profileView.html')

@login_required(login_url='/login/')
def friendProfileView(request):
    profile_id = request.GET.get('id', '')
    profile = Profile.objects.get(id=profile_id)
    if workExperience.objects.filter(profile=profile).exists():
        experiences = workExperience.objects.filter(profile=profile)
        return render(request, 'profile/profileView.html', {'profile': profile, 'experiences': experiences, 'is_friend': True })
    else:
        return render(request, 'profile/profileView.html', { 'profile': profile, 'is_friend': True })

def capitalizeString(input):
    if input == "":
        return ""
    finalString = " ".join(word[0].upper()+word[1:] for word in input.split(" "))
    return finalString

@login_required(login_url='/login/')
def profileEdit(request):
    #check if user exists already in DB
    exists=Profile.objects.filter(user=request.user).exists()

    #If we have a profile already, and are posting
    if exists and request.method == 'POST':
        form = profileEditForm(request.POST, instance = Profile.objects.get(user=request.user))
        if form.is_valid():
            form.instance.major = capitalizeString(form.cleaned_data['major'])
            form.instance.university = capitalizeString(form.cleaned_data['university'])
            form.save() # Save profile to Database
            return redirect('/profile/') # Redirect user to viewing their profile
    
    #No profile, am creating it for the first time
    elif request.method == 'POST':
        form = profileEditForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user #instance=my_record
            form.instance.major = capitalizeString(form.cleaned_data['major'])
            form.instance.university = capitalizeString(form.cleaned_data['university'])
            form.save() # Save profile to Database

            return redirect('/profile/') # Redirect user to viewing their profile
    
    #Profile exists, is viewing the page
    elif exists:
        form = profileEditForm(instance = Profile.objects.get(user=request.user))
    
    #No profile, is viewing page
    else:
        form = profileEditForm()

    return render(request, 'profile/profileEdit.html', {'form': form})

@login_required(login_url='/login/')
#Have to check that we dont allow more than 3
def addWorkExperience(request):
    form = workExperienceForm()
    if request.method == 'POST':
        form = workExperienceForm(request.POST)
        if len(workExperience.objects.filter(profile = Profile.objects.get(user=request.user))) >= 3:
            messages.error(request, "Reached Max number of allotted work experiences. (3)")
            return redirect('/profile/addJob') # Redirect user to viewing their profile
        if form.is_valid():
            print(form.cleaned_data['employer'])
            form.instance.profile = Profile.objects.get(user=request.user)
            try:
                form.save() # Save profile to Database
            except:
                messages.error(request, "Job already Exists")
                return redirect('/profile/addJob') # Redirect user to viewing their profile
            title = form.cleaned_data.get('title') 
            messages.success(request, f'Account created for {title}!') # Show sucess message when account is created
            return redirect('/profile/') # Redirect user to viewing their profile

    return render(request, 'profile/addWorkExperience.html', {'form': form})

@login_required(login_url='/login/')
def accountSelection(request):
    choice = ['Standard', 'Plus']
    exists=Account.objects.filter(user=request.user).exists()
    
    account_choice = None
    
    if exists:
        account_choice = Account.objects.get(user=request.user)

    if request.method=='GET':
        return render(request, 'registration/plusAcc.html', {'choice': choice, 'account_choice': account_choice})
    else:
        choice = request.POST['choice']
        
        if exists:
            account_choice.plusAccount = choice
            account_choice.save()
            print (account_choice.plusAccount)
            return HttpResponseRedirect('/home')
                       
        else:
            Account.objects.create(user=request.user, plusAccount=choice)
    messages.success(request, 'Changes saved')

    return render(request, 'registration/plusAcc.html', {'choice': choice, 'account_choice': account_choice})

#Message views
# def Messagesview(request):
#         accounts = Account.objects.all()
#         return render(request, 'messages/messages.html', {'accounts': accounts})
@login_required(login_url='/login/')
def messageForm(request, pk):
        receiver = Account.objects.get(id = pk)
        sender = Account.objects.get(user = request.user)
        return render(request, 'messages/form.html',{'receiver': receiver})
        if(sender.plusAccount == "Plus"):
            return render(request, 'messages/form.html',{'receiver': receiver})
        elif(Friendship.objects.filter(user_one = sender, user_two = receiver)):
            return render(request, 'messages/form.html',{'receiver': receiver})
        else:
            messages.info(request, 'The person you are trying to send a message is not in your friend group so message cannot be sent.')
            return redirect('/messages')
@login_required(login_url='/login/')        
def MessageView(request):
    account_list = Account.objects.all()
    return render(request,'messages/messages.html',{"account_list": account_list})
@login_required(login_url='/login/')
def ProcessMessage(request, pk):
    receiver = User.objects.get(id = pk)
    sent_message = Message()
    sent_message.sender = request.user
    sent_message.receiver = receiver
    sent_message.content = request.POST.get('content')
    sent_message.created_at =  date.today()
    sent_message.save()
    messages.info(request, 'Message Sent!')
    return redirect('jobs:MessageInbox')

def MessageInbox(request):
    received_messages = Message.objects.filter(receiver = request.user.id)
    sent_messages = Message.objects.filter(sender = request.user.id)
    return render(request, 'messages/inbox.html', {'received_messages': received_messages,'sent_messages' : sent_messages})


def job_text(request):
    response = HttpResponse(content_type='plain/text')
    response['Content-Disposition'] = 'attachment; filename=MyCollege_job.txt'
    
    #designate the model
    jobs = Job.objects.all()
    
    #create blank list
    lines = []
    
    #loop through and output
    for job in jobs:
        lines.append(f'Title: {job.title}\nDescription: {job.description}\nEmployer: {job.employer}\nLocation: {job.location}\nSalary: {job.salary}\n======\n')
        
    #write to text file
    response.writelines(lines)
    return response

def profiles_text(request):
    response = HttpResponse(content_type='plain/text')
    response['Content-Disposition'] = 'attachment; filename=MyCollege_profiles.txt'
    
    #designate the model
    profiles = Profile.objects.all()
    
    #create blank list
    lines = []
    
    #loop through and output
    for profile in profiles:
        lines.append(f'Title: {profile.title}\nMajor: {profile.major}\nUniversity Name: {profile.university}\nAbout: {profile.about}\nExperience: {profile.yearsAttended}\nEducation: {profile.yearsAttended}\n======\n')
        
    #write to text file
    response.writelines(lines)
    return response

def users_text(request):
    response = HttpResponse(content_type='plain/text')
    response['Content-Disposition'] = 'attachment; filename=MyCollege_users.txt'
    
    #designate the model
    accounts = Account.objects.all()
    
    #create blank list
    lines = []
    
    #loop through and output
    for account in accounts:
        lines.append(f'Username: {account.user}\nAccount Type: {account.plusAccount}\n======\n')
        
    #write to text file
    response.writelines(lines)
    return response

def training_text(request):
    response = HttpResponse(content_type='plain/text')
    response['Content-Disposition'] = 'attachment; filename=MyCollege_training.txt'
    
    #designate the model
    skills = Account.objects.all()
    
    #create blank list
    lines = []
    
    #loop through and output
    for account in skills:
        lines.append(f'Username: {account.user}\nSkills: ')
        for s in account.skill.all():
            lines.append(f'{s}, ')
        lines.append(f'\n======\n')    
            
        
    #write to text file
    response.writelines(lines)
    return response

def appliedJobs_text(request):
    response = HttpResponse(content_type='plain/text')
    response['Content-Disposition'] = 'attachment; filename=MyCollege_appliedJobs.txt'
    
    #designate the model
    appliedJobs = jobApplication.objects.all()
    
    #create blank list
    lines = []
    
    #loop through and output
    for appliedJob in appliedJobs:
        lines.append(f'Job Name: {appliedJob.appliedJob.title}\nApplicant Username: {appliedJob.appliedUser}\nParagraph: {appliedJob.applyParagraph}\n=====\n')
        
    #write to text file
    response.writelines(lines)
    return response

def savedJobs_text(request):
    response = HttpResponse(content_type='plain/text')
    response['Content-Disposition'] = 'attachment; filename=MyCollege_savedJobs.txt'
    
    #designate the model
    savedJobs = jobStatus.objects.all()
    
    #create blank list
    lines = []
    
    #loop through and output
    for savedJob in savedJobs:
        if savedJob.saved:    
            lines.append(f'Username: {savedJob.user}\nTitle: {savedJob.associatedJob.title}\n=====\n')
        
        
    #write to text file
    response.writelines(lines)
    return response

#move job notification to job-section view
@login_required(login_url='/login/')
def jobNotifView (request): #list of job noti
    jobsApplied = jobStatus.objects.filter(user = request.user.id)  
    lastJobApplied = jobStatus.objects.filter(user=request.user, applied=True).reverse()
    #check first obj from list (newest job applied)
    if lastJobApplied:
        # firstTime = jobApplication.objects.filter(appliedUser=request.user)[0].appliedTime
        lastApplied = lastJobApplied[0].getTimeCreated()
    else: #list empty => hasnt applied for any
        lastApplied =8
    return render(request, 'jobs/notification.html', {'jobsAppliedCheck': jobsApplied, 'lastApplied' : lastApplied})
