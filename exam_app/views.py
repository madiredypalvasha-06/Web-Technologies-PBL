import random
from django.shortcuts import render
from .models import Question

def start_exam(request):
    questions = list(Question.objects.all())
    random_questions = random.sample(questions, min(len(questions), 5))

    if request.method == 'POST':
        score = 0
        
        for question in random_questions:
            selected_answer = request.POST.get(str(question.id))
            
            if selected_answer == question.correct_answer:
                score += 1

        return render(request, 'result.html', {
            'score': score,
            'total': len(random_questions)
        })

    return render(request, 'exam.html', {'questions': random_questions})
