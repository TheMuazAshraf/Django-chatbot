from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from groq import Groq
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.utils import timezone


client = Groq(api_key="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", base_url="https://api.groq.com")

def ask_groq(message):
    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages = [{"role": "user", "content": message}],
        max_tokens = 150,
        n=1,
        stop = None,
        temperature = 0.7,
    )
    answer = response.choices[0].message.content.strip()
    return answer

# Create your views here.
def index(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST['message']
        response = ask_groq(message)
        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username = username, password = password)
        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})
    else:
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
                error_message = 'Error Creating account'
                return render(request, 'register.html', {'error_message' : error_message})

        else:
            error_message = "password don't match"
            return render(request, 'register.html', {'error_message' : error_message})

    return render(request, 'register.html')


def logout(request):
    auth.logout(request)
    return redirect('login')