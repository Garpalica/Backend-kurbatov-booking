from django.shortcuts import render

def index(request):
    return render(request, 'lab4/index.html')
