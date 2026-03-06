import json
import random
from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.views.decorators.csrf import csrf_exempt
from .models import (
    Student, Question, QuestionCategory, Exam, ExamSession, Result,
    Worksheet, StudyMaterial, PracticeTest, PracticeSession, Bookmark,
    Achievement, StudentProgress, QuestionAttempt
)

def is_admin(user):
    return user.is_staff


@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        # Handle both JSON and FormData
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
                'first_name': user.first_name,
                'last_name': user.last_name,
            })
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_logout(request):
    logout(request)
    return JsonResponse({'success': True})


@csrf_exempt
def api_register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        student_id = data.get('student_id')
        department = data.get('department', '')

        if password != confirm_password:
            return JsonResponse({'error': 'Passwords do not match'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        if Student.objects.filter(student_id=student_id).exists():
            return JsonResponse({'error': 'Student ID already registered'}, status=400)

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name
        )
        Student.objects.create(user=user, student_id=student_id, department=department)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def api_user(request):
    return JsonResponse({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'is_staff': request.user.is_staff,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
    })


@login_required
def api_exams(request):
    if request.user.is_staff:
        return JsonResponse({'error': 'Admin user'}, status=403)
    
    student = get_object_or_404(Student, user=request.user)
    today = date.today()
    current_time = datetime.now().time()
    
    available_exams = Exam.objects.filter(
        is_active=True,
        exam_date__gte=today
    )
    
    now = datetime.now()
    filtered_exams = []
    for exam in available_exams:
        if exam.exam_date == today:
            if exam.start_time <= current_time <= exam.end_time:
                filtered_exams.append(exam)
        else:
            filtered_exams.append(exam)
    
    available_exams = filtered_exams
    
    completed_sessions = ExamSession.objects.filter(student=student, is_completed=True)
    available_exams = [exam for exam in available_exams if not completed_sessions.filter(exam=exam).exists()]
    
    return JsonResponse({
        'available': [{
            'id': exam.id,
            'title': exam.title,
            'description': exam.description,
            'exam_date': exam.exam_date.strftime('%Y-%m-%d'),
            'duration_minutes': exam.duration_minutes,
            'number_of_questions': exam.number_of_questions,
            'passing_percentage': exam.passing_percentage,
        } for exam in available_exams]
    })


@login_required
def api_results(request):
    if request.user.is_staff:
        return JsonResponse({'error': 'Admin user'}, status=403)
    
    student = get_object_or_404(Student, user=request.user)
    results = Result.objects.filter(student=student).order_by('-submitted_at')[:10]
    
    completed_count = Result.objects.filter(student=student).count()
    passed_count = Result.objects.filter(student=student, passed=True).count()
    avg_score = Result.objects.filter(student=student).aggregate(Avg('score'))['score__avg'] or 0
    
    return JsonResponse({
        'results': [{
            'id': r.id,
            'exam_title': r.exam.title,
            'score': r.score,
            'passed': r.passed,
            'submitted_at': r.submitted_at.strftime('%Y-%m-%d %H:%M'),
        } for r in results],
        'stats': {
            'completed': completed_count,
            'passed': passed_count,
            'avgScore': round(avg_score, 1),
        }
    })


@login_required
def api_practice_tests(request):
    if request.user.is_staff:
        return JsonResponse({'error': 'Admin user'}, status=403)
    
    category_id = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    
    tests = PracticeTest.objects.filter(is_published=True)
    
    if category_id:
        tests = tests.filter(category_id=category_id)
    if difficulty and difficulty != 'all':
        tests = tests.filter(difficulty=difficulty)
    
    return JsonResponse({
        'tests': [{
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'difficulty': t.difficulty,
            'number_of_questions': t.number_of_questions,
            'is_timed': t.is_timed,
            'time_limit_minutes': t.time_limit_minutes,
            'category': t.category.name if t.category else None,
        } for t in tests]
    })


@login_required
def api_worksheets(request):
    if request.user.is_staff:
        return JsonResponse({'error': 'Admin user'}, status=403)
    
    category_id = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    
    worksheets = Worksheet.objects.filter(is_published=True)
    
    if category_id:
        worksheets = worksheets.filter(category_id=category_id)
    if difficulty and difficulty != 'all':
        worksheets = worksheets.filter(difficulty=difficulty)
    
    return JsonResponse({
        'worksheets': [{
            'id': w.id,
            'title': w.title,
            'description': w.description,
            'difficulty': w.difficulty,
            'number_of_questions': w.number_of_questions,
            'time_limit_minutes': w.time_limit_minutes,
            'category': w.category.name if w.category else None,
        } for w in worksheets]
    })


@login_required
def api_materials(request):
    if request.user.is_staff:
        return JsonResponse({'error': 'Admin user'}, status=403)
    
    category_id = request.GET.get('category')
    material_type = request.GET.get('type')
    
    materials = StudyMaterial.objects.filter(is_published=True)
    
    if category_id:
        materials = materials.filter(category_id=category_id)
    if material_type:
        materials = materials.filter(material_type=material_type)
    
    return JsonResponse({
        'materials': [{
            'id': m.id,
            'title': m.title,
            'description': m.description,
            'material_type': m.material_type,
            'content': m.content,
            'external_link': m.external_link,
            'category': m.category.name if m.category else None,
        } for m in materials]
    })


@login_required
def api_categories(request):
    categories = QuestionCategory.objects.all()
    return JsonResponse([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'color': c.color,
    } for c in categories], safe=False)


@login_required
def api_progress(request):
    if request.user.is_staff:
        return JsonResponse({'error': 'Admin user'}, status=403)
    
    student = get_object_or_404(Student, user=request.user)
    
    progress = StudentProgress.objects.filter(student=student)
    total_attempted = sum(p.total_questions_attempted for p in progress)
    total_correct = sum(p.correct_answers for p in progress)
    
    return JsonResponse({
        'total_attempted': total_attempted,
        'correct': total_correct,
        'wrong': total_attempted - total_correct,
        'accuracy': round((total_correct / total_attempted * 100), 1) if total_attempted > 0 else 0,
    })


@login_required
def api_bookmarks(request):
    if request.user.is_staff:
        return JsonResponse({'error': 'Admin user'}, status=403)
    
    student = get_object_or_404(Student, user=request.user)
    bookmarks = Bookmark.objects.filter(student=student).select_related('question')
    
    return JsonResponse({
        'bookmarks': [{
            'id': b.id,
            'question_id': b.question.id,
            'question_text': b.question.question_text,
            'option1': b.question.option1,
            'option2': b.question.option2,
            'option3': b.question.option3,
            'option4': b.question.option4,
            'correct_answer': b.question.correct_answer,
            'notes': b.notes,
        } for b in bookmarks]
    })


@login_required
@csrf_exempt
def api_toggle_bookmark(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        student = get_object_or_404(Student, user=request.user)
        question_id = data.get('question_id')
        question = get_object_or_404(Question, id=question_id)
        
        bookmark, created = Bookmark.objects.get_or_create(
            student=student,
            question=question
        )
        
        if not created:
            bookmark.delete()
            return JsonResponse({'bookmarked': False})
        
        return JsonResponse({'bookmarked': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
@user_passes_test(is_admin)
def api_admin_students(request):
    if request.method == 'GET':
        students = Student.objects.select_related('user').all()
        return JsonResponse({
            'students': [{
                'id': s.id,
                'user_id': s.user.id,
                'username': s.user.username,
                'email': s.user.email,
                'first_name': s.user.first_name,
                'last_name': s.user.last_name,
                'student_id': s.student_id,
                'department': s.department,
                'is_active': s.user.is_active,
                'date_joined': s.user.date_joined.strftime('%Y-%m-%d'),
            } for s in students]
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@user_passes_test(is_admin)
@csrf_exempt
def api_admin_student_update(request, student_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        student = get_object_or_404(Student, id=student_id)
        user = student.user
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        if 'department' in data:
            student.department = data['department']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        user.save()
        student.save()
        
        return JsonResponse({'success': True})
    
    if request.method == 'DELETE':
        student = get_object_or_404(Student, id=student_id)
        user = student.user
        student.delete()
        user.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@user_passes_test(is_admin)
def api_admin_exams(request):
    if request.method == 'GET':
        exams = Exam.objects.all().order_by('-exam_date')
        return JsonResponse({
            'exams': [{
                'id': e.id,
                'title': e.title,
                'description': e.description,
                'exam_date': e.exam_date.strftime('%Y-%m-%d'),
                'start_time': e.start_time.strftime('%H:%M'),
                'end_time': e.end_time.strftime('%H:%M'),
                'duration_minutes': e.duration_minutes,
                'number_of_questions': e.number_of_questions,
                'passing_percentage': e.passing_percentage,
                'is_active': e.is_active,
                'total_attempts': ExamSession.objects.filter(exam=e).count(),
            } for e in exams]
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@user_passes_test(is_admin)
@csrf_exempt
def api_admin_exam_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        exam = Exam.objects.create(
            title=data['title'],
            description=data.get('description', ''),
            exam_date=data['exam_date'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            duration_minutes=data['duration_minutes'],
            number_of_questions=data['number_of_questions'],
            passing_percentage=data['passing_percentage'],
            is_active=data.get('is_active', True),
        )
        return JsonResponse({'id': exam.id, 'success': True})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@user_passes_test(is_admin)
@csrf_exempt
def api_admin_exam_update(request, exam_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        exam = get_object_or_404(Exam, id=exam_id)
        
        exam.title = data.get('title', exam.title)
        exam.description = data.get('description', exam.description)
        exam.exam_date = data.get('exam_date', exam.exam_date)
        exam.start_time = data.get('start_time', exam.start_time)
        exam.end_time = data.get('end_time', exam.end_time)
        exam.duration_minutes = data.get('duration_minutes', exam.duration_minutes)
        exam.number_of_questions = data.get('number_of_questions', exam.number_of_questions)
        exam.passing_percentage = data.get('passing_percentage', exam.passing_percentage)
        exam.is_active = data.get('is_active', exam.is_active)
        exam.save()
        
        return JsonResponse({'success': True})
    
    if request.method == 'DELETE':
        exam = get_object_or_404(Exam, id=exam_id)
        exam.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@user_passes_test(is_admin)
def api_admin_questions(request):
    if request.method == 'GET':
        questions = Question.objects.select_related('category').all()
        return JsonResponse({
            'questions': [{
                'id': q.id,
                'question_text': q.question_text,
                'option1': q.option1,
                'option2': q.option2,
                'option3': q.option3,
                'option4': q.option4,
                'correct_answer': q.correct_answer,
                'explanation': q.explanation,
                'difficulty': q.difficulty,
                'category': q.category.name if q.category else None,
                'is_active': q.is_active,
            } for q in questions]
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@user_passes_test(is_admin)
@csrf_exempt
def api_admin_question_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        category = QuestionCategory.objects.get(id=data['category']) if data.get('category') else None
        
        question = Question.objects.create(
            question_text=data['question_text'],
            option1=data['option1'],
            option2=data['option2'],
            option3=data['option3'],
            option4=data['option4'],
            correct_answer=data['correct_answer'],
            explanation=data.get('explanation', ''),
            difficulty=data.get('difficulty', 'medium'),
            category=category,
            is_active=data.get('is_active', True),
        )
        return JsonResponse({'id': question.id, 'success': True})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@user_passes_test(is_admin)
@csrf_exempt
def api_admin_question_update(request, question_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = get_object_or_404(Question, id=question_id)
        
        question.question_text = data.get('question_text', question.question_text)
        question.option1 = data.get('option1', question.option1)
        question.option2 = data.get('option2', question.option2)
        question.option3 = data.get('option3', question.option3)
        question.option4 = data.get('option4', question.option4)
        question.correct_answer = data.get('correct_answer', question.correct_answer)
        question.explanation = data.get('explanation', question.explanation)
        question.difficulty = data.get('difficulty', question.difficulty)
        question.is_active = data.get('is_active', question.is_active)
        
        if data.get('category'):
            question.category = QuestionCategory.objects.get(id=data['category'])
        
        question.save()
        return JsonResponse({'success': True})
    
    if request.method == 'DELETE':
        question = get_object_or_404(Question, id=question_id)
        question.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@user_passes_test(is_admin)
def api_admin_dashboard(request):
    total_students = Student.objects.count()
    total_exams = Exam.objects.count()
    total_questions = Question.objects.count()
    total_results = Result.objects.count()
    
    recent_results = Result.objects.select_related('student__user', 'exam').order_by('-submitted_at')[:10]
    
    return JsonResponse({
        'stats': {
            'total_students': total_students,
            'total_exams': total_exams,
            'total_questions': total_questions,
            'total_results': total_results,
        },
        'recent_results': [{
            'id': r.id,
            'student_name': f"{r.student.user.first_name} {r.student.user.last_name}",
            'exam_title': r.exam.title,
            'score': r.score,
            'passed': r.passed,
            'submitted_at': r.submitted_at.strftime('%Y-%m-%d %H:%M'),
        } for r in recent_results]
    })


@login_required
def api_exam_detail(request, exam_id):
    if request.user.is_staff:
        return JsonResponse({'error': 'Admin user'}, status=403)
    
    exam = get_object_or_404(Exam, id=exam_id)
    return JsonResponse({
        'id': exam.id,
        'title': exam.title,
        'description': exam.description,
        'duration_minutes': exam.duration_minutes,
        'number_of_questions': exam.number_of_questions,
        'passing_percentage': exam.passing_percentage,
    })


@login_required
def api_exam_start(request, exam_id):
    if request.user.is_staff:
        return JsonResponse({'error': 'Admin user'}, status=403)
    
    student = get_object_or_404(Student, user=request.user)
    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    
    if ExamSession.objects.filter(student=student, exam=exam, is_completed=False).exists():
        return JsonResponse({'error': 'Exam already in progress'}, status=400)
    
    session = ExamSession.objects.create(
        student=student,
        exam=exam,
        started_at=timezone.now()
    )
    
    return JsonResponse({'session_id': session.id})


@login_required
def api_exam_take(request, exam_id):
    if request.user.is_staff:
        return JsonResponse({'error': 'Admin user'}, status=403)
    
    student = get_object_or_404(Student, user=request.user)
    session = get_object_or_404(ExamSession, student=student, exam_id=exam_id, is_completed=False)
    
    import random
    exam = session.exam
    all_questions = list(Question.objects.filter(is_active=True))
    questions = random.sample(all_questions, min(len(all_questions), exam.number_of_questions))
    
    time_remaining = exam.duration_minutes * 60 - (timezone.now() - session.started_at).seconds
    
    return JsonResponse({
        'session_id': session.id,
        'time_remaining': max(0, time_remaining),
        'questions': [{
            'id': q.id,
            'question_text': q.question_text,
            'option1': q.option1,
            'option2': q.option2,
            'option3': q.option3,
            'option4': q.option4,
        } for q in questions]
    })


@login_required
@csrf_exempt
def api_exam_submit(request, exam_id):
    if request.user.is_staff:
        return JsonResponse({'error': 'Admin user'}, status=403)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        student = get_object_or_404(Student, user=request.user)
        session = get_object_or_404(ExamSession, id=data.get('session_id'), student=student, exam_id=exam_id)
        
        answers = data.get('answers', {})
        
        correct_count = 0
        total_questions = len(answers)
        
        for q_id, answer in answers.items():
            question = Question.objects.get(id=q_id)
            if question.correct_answer == answer:
                correct_count += 1
        
        score = (correct_count / total_questions * 100) if total_questions > 0 else 0
        passing = score >= session.exam.passing_percentage
        
        session.is_completed = True
        session.completed_at = timezone.now()
        session.score = score
        session.save()
        
        Result.objects.create(
            student=student,
            exam=session.exam,
            score=score,
            passed=passing,
            submitted_at=timezone.now()
        )
        
        return JsonResponse({
            'score': round(score, 1),
            'passed': passing,
            'correct': correct_count,
            'total': total_questions
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
@csrf_exempt
def api_exam_violation(request, exam_id):
    if request.user.is_staff:
        return JsonResponse({'error': 'Admin user'}, status=403)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        student = get_object_or_404(Student, user=request.user)
        
        try:
            session = ExamSession.objects.get(student=student, exam_id=exam_id, is_completed=False)
            session.violation_count += 1
            session.save()
        except ExamSession.DoesNotExist:
            pass
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
