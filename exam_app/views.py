import random
from django.shortcuts import render
from .models import Question

def start_exam(request):
    questions = list(Question.objects.all())
    
    # Select 5 random questions
    random_questions = random.sample(questions, min(len(questions), 5))
    
    return render(request, 'exam.html', {'questions': random_questions})
