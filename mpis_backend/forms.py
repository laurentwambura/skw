from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django import forms
from django.contrib.auth import get_user_model
import csv
# from pathlib import Path
from mpis.settings import MEDIA_ROOT
from mpis_backend.models import *

User = get_user_model()


class LoginAuthenticationForm(forms.Form):
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', ]

    def clean_password(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user


class ReplyForm(forms.Form):
    reply = forms.CharField(widget=forms.Textarea)


class UploadDataForm(forms.Form):
    choose = forms.FileField()

    def handle_uploaded_majimbo(file):
        with open(MEDIA_ROOT+'/'+file.name) as jimbo:
            jimbo_csv = list(csv.DictReader(jimbo))
        for oni in jimbo_csv:
            del oni['id']
            m = Jimbo(**oni)
            m.save()
        return 'done '

    def handle_uploaded_sekta(file):
        with open(MEDIA_ROOT+'/'+file.name) as sekta:
            sekta_csv = list(csv.DictReader(sekta))
        for oni in sekta_csv:
            m = Sekta(**oni)
            m.save()
        return 'done '
