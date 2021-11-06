from os import times
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from .models import ChatRoom
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound

# Create your views here.
def index(request):
    return render(request, 'chat/index.html')

@login_required
def room(request, room_name):
    try:
        ChatRoom.objects.get(title=room_name).connect_user(user=request.user)
    except:
        return HttpResponseNotFound('404 room not found')
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })
