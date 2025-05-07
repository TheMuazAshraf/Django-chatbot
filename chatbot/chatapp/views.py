from django.shortcuts import render, redirect
from django.http import JsonResponse
from groq import Groq
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat, ChatSession
from django.utils import timezone

client = Groq(api_key="your_api_key", base_url="https://api.groq.com")

def ask_groq(message):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},
        ]
    )
    return response.choices[0].message.content.strip()

def index(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Handle session logic
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            active_session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            active_session = ChatSession.objects.create(user=request.user)
    else:
        active_session = ChatSession.objects.filter(user=request.user).order_by('-created_at').first()

    if not active_session:
        active_session = ChatSession.objects.create(user=request.user)

    # Handle chat submission
    if request.method == 'POST':
        message = request.POST['message']
        response = ask_groq(message)
        Chat.objects.create(
            user=request.user,
            session=active_session,
            message=message,
            response=response,
            created_at=timezone.now()
        )
        return JsonResponse({'message': message, 'response': response})

    # Get all chats in the active session
    chats = Chat.objects.filter(session=active_session).order_by('created_at')

    # Get all sessions for sidebar
    chat_sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'chatbot.html', {
        'chats': chats,
        'chat_sessions': chat_sessions,
        'active_session': active_session
    })


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error_message': "Invalid username or password"})
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('index')
            except:
                return render(request, 'register.html', {'error_message': 'Error Creating Account'})
        else:
            return render(request, 'register.html', {'error_message': "Passwords don't match"})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')
