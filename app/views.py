from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm 
from .models import Room, Topic, Message
from .forms import RoomForm

def loginPage(request): 
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username= username)
        except:
            messages.error(request, 'deleted')
        
        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('home')
    context = {'page' : page}
    return render(request, 'app/login_register.html', context)

def logoutPage(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    # page = 'register'
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid:
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Error while Registration")
    return render(request, 'app/login_register.html', {'form' : form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__contains = q) |
        Q(name__icontains = q) | 
        Q(description__icontains = q)
        )
    # rooms = Room.objects.filter(topic__name__icontains = q)
    topics = Topic.objects.all()
    room_count = rooms.count()
    roommessages = Message.objects.filter(Q(room__topic__name__contains = q))

    context = {'rooms' : rooms, 'topics' : topics, 'room_count' : room_count, 'roommessages' : roommessages}
    return render(request, 'app/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    roommessages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        messageobj = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk = room.id)
    context = {'room' : room, 'roommessages' : roommessages, 'participants' : participants}
    return render(request, 'app/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id = pk)
    rooms = user.room_set.all()
    roommessages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user' : user, 'rooms' : rooms, 'roommessages' : roommessages, 'topics' : topics}   
    return render(request, 'app/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm() 
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')
    context = {'form' : form, 'topics' : topics, 'room' : room}
    return render(request, 'app/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse("You're not allowed here..!!")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)
        room.name = request.POST.get('name')
        room.topic = request.POST.get('topic')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context = {'form' : form, 'topics' : topics}
    return render(request, 'app/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id = pk)

    if request.user != room.host:
        return HttpResponse("You're not allowed here..!!")

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'app/delete.html', {'obj' : room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id = pk)

    if request.user != message.user:
        return HttpResponse("You're not allowed here..!!")

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'app/delete.html', {'obj' : message})