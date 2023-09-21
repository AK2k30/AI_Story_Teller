from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai #type: ignore

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone
from django.contrib.auth.decorators import login_required



openai_api_key = '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'
openai.api_key = openai_api_key

def ask_openai(message):
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Imagine a world where magic is real, and every person possesses a unique, hidden power. You are about to embark on a storytelling journey where you provide the first half of a story, setting the stage with characters, a basic plot, and the initial conflict. The AI will then take your story and transform it into an engaging and captivating narrative that will leave readers eagerly wanting to know how it all unfolds. Get ready to unleash your creativity and watch as the AI weaves your tale into an enchanting adventure!"},
            {"role": "user", "content": message},
        ]
    )
    
    answer = response.choices[0].message.content.strip() #type: ignore
    return answer


# Create your views here.
@login_required
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
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
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')
