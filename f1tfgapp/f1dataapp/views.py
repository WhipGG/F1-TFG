from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, 'f1dataapp/index.html')


def predictions(request):
    return render(request, 'f1dataapp/index.html')