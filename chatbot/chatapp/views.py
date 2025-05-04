from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from groq import Groq


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
def index(request, methods=('POST', 'GET')):
    if request.method == 'POST':
        message = request.POST['message']
        response = ask_groq(message)
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html')


