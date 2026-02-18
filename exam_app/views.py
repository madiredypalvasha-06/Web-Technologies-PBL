import random
from django.shortcuts import render
from .models import Question

def start_exam(request):

    if request.method == 'POST':
        score = 0
        question_ids = request.session.get('exam_questions', [])

        questions = Question.objects.filter(id__in=question_ids)

        for question in questions:
            selected_answer = request.POST.get(str(question.id))
            if selected_answer == question.correct_answer:
                score += 1

        return render(request, 'result.html', {
            'score': score,
            'total': len(questions)
        })

    else:
        questions = list(Question.objects.all())
        random_questions = random.sample(questions, min(len(questions), 5))

        # Store question IDs in session
        request.session['exam_questions'] = [q.id for q in random_questions]

        return render(request, 'exam.html', {'questions': random_questions})

