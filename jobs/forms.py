from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
class UserForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'

        self.helper.add_input(Submit('submit', 'Submit'))
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1']

#simple job posting template.
class jobPosting(forms.ModelForm):
    title = forms.CharField(max_length=50)
    employer = forms.CharField(max_length=50)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows":"5"}))
    location = forms.CharField(max_length=20)
    salary = forms.IntegerField()
    class Meta:
        model =Job
        fields = ['title', 'employer', 'description', 'location', 'salary']
        #dont have postedBy field cuz we dont want to display it now

#form for login page
class loginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput()) #not showing actual password

#form for searching people
class searchForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'

        self.helper.add_input(Submit('submit', 'Submit'))
    
class baseConnectionForm(forms.ModelForm):
    class Meta:
        model = Connections
        fields = ['user']

class profileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['title', 'about', 'major', 'university', 'degree', 'yearsAttended']

class workExperienceForm(forms.ModelForm):
    class Meta:
        model = workExperience
        fields = ['title', 'employer', 'location', 'description', 'dateStarted', 'dateEnded']

class jobApplicationForm(forms.ModelForm):
    class Meta:
        model = jobApplication
        fields = ['applyParagraph', 'gradDate', 'startDate']
class messageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields=['content']