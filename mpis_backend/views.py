from django.http.response import HttpResponseRedirect
from mpis_backend.models import Jimbo, Sekta, Maoni
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views import View
from mpis_backend import forms
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import json
import requests
from django.core.files.storage import FileSystemStorage


class SektaListView(LoginRequiredMixin, ListView):
    model = Sekta
    template_name = "mpis_backend/majimbo.html"
    context_object_name = 'sekta'


class HomeView(TemplateView):
    template_name = "about.html"


class LoginView(View):
    form_class = forms.LoginAuthenticationForm
    template_name = 'registration/login.html'
    form = forms.LoginAuthenticationForm
    context = {'form': form}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_admin:
                    return redirect('/admin')
                return redirect('/')
            else:
                print(user)
        return HttpResponse('form is not valid')


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('home')


def reply(request, pk):
    form = forms.ReplyForm()
    context = {'form': form, 'pk': pk}
    return render(request, 'mpis_backend/reply.html', context)









def maoni(request):
    maoni_obj = Maoni.objects.filter(status=False)
    context = {'maoni': maoni_obj}
    return render(request, 'majimbo.html', context)


def send_message(request, pk):
    if request.method == "POST":
        oni = Maoni.objects.get(id=pk)
        namba = oni.phone_number
        form = forms.ReplyForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data.get('reply')
            url = "https://rapidpro.ilhasoft.mobi/api/v2/broadcasts.json"
            payload = json.dumps({
                "contacts": [
                    namba,
                ],
                "text": text
            })
            headers = {
                'Authorization': 'Token 1f8fd3a05d6ef30517d74486aa8f173cf34c3127',
                'Content-Type': 'application/json'
            }
            response = requests.request(
                "POST", url, headers=headers, data=payload)
            messages.success(request, 'Successful replied')
            print(response)
            oni.status = True
            oni.save()
            return redirect('/mpis/maoni')


def upload_data_from_file(request):

    if request.method == 'POST' and request.FILES['choose']:
        myfile = request.FILES['choose']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        # uploaded_file_url = fs.url(filename)

        print(forms.UploadDataForm.handle_uploaded_majimbo(myfile))
        return HttpResponseRedirect('/')

    form = forms.UploadDataForm()
    return render(request, 'mpis_backend/add_data_from_csv.html', {'form': form})


def upload_data_sekta(request):

    if request.method == 'POST' and request.FILES['choose']:
        myfile = request.FILES['choose']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        # uploaded_file_url = fs.url(filename)

        print(forms.UploadDataForm.handle_uploaded_sekta(myfile))
        return HttpResponseRedirect('/')

    form = forms.UploadDataForm()
    return render(request, 'mpis_backend/add_data_sekta.html', {'form': form})
