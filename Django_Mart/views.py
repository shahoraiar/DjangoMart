from django.shortcuts import render

def home(request) : 
    if not request.session.session_key:
        request.session.create()
    return render(request , 'index.html')