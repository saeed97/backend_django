#!/home/stepsizestrategies/.local/bin/python3
# -*- coding: utf-8 -*-

from strategies.forms import LoginForm, RegisterForm
from django.shortcuts import render,redirect

from django.contrib.auth import authenticate, login, logout

from django.utils.html import escape

from django.contrib import messages




def index(request):

    return  render(request, 'graphics/index.html')
def profile(request):

    return  render(request, 'graphics/profile.html')

def find(request):

    return  render(request, 'graphics/explore.html')
def listing(request):

    return  render(request, 'graphics/listing.html')
def about(request):

    return  render(request, 'graphics/contact.html')
def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)

        return redirect('index')

    return render(request, 'graphics/login.html')


def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        password = form.cleaned_data.get('password')
        user.set_password(password)
        # user.is_staff = user.is_superuser = True
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        return redirect('index')

    return render(request, 'graphics/register.html')


def logout_view(request):
    logout(request)
    return redirect('login')



     
