import random
import json
from datetime import datetime, date, time, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Avg, Max, Min, F
from .models import Student, Question, QuestionCategory, Exam, ExamSession, Result, Worksheet, StudyMaterial, PracticeTest, PracticeSession, Bookmark, Achievement, StudentProgress, QuestionAttempt
from django.views.decorators.csrf import csrf_exempt

def is_admin(user):
    return user.is_staff

def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('student_dashboard')
    return redirect('login')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        student_id = request.POST.get('student_id')
        department = request.POST.get('department', '')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'register.html')

        if Student.objects.filter(student_id=student_id).exists():
            messages.error(request, 'Student ID already registered')
            return render(request, 'register.html')

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name
        )
        Student.objects.create(user=user, student_id=student_id, department=department)
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')

    return render(request, 'register.html')

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def student_dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    student = get_object_or_404(Student, user=request.user)
    today = date.today()
    current_time = datetime.now().time()
    
    # Get available exams (all active exams)
    available_exams = Exam.objects.filter(is_active=True)
    
    # Filter out completed exams
    completed_sessions = ExamSession.objects.filter(student=student, is_completed=True)
    available_exams = [exam for exam in available_exams if not completed_sessions.filter(exam=exam).exists()]
    
    # Get results with stats
    results = Result.objects.filter(student=student).order_by('-submitted_at')[:10]
    completed_count = completed_sessions.count()
    
    total_passed = Result.objects.filter(student=student, passed=True).count()
    total_attempts = Result.objects.filter(student=student).count()
    avg_score = Result.objects.filter(student=student).aggregate(Avg('score'))['score__avg'] or 0
    
    # Get upcoming exams
    upcoming_exams = Exam.objects.filter(
        is_active=True,
        exam_date__gte=today
    ).order_by('exam_date', 'start_time')[:5]
    
    return render(request, 'student_app.html', {
        'student': student,
        'available_exams': available_exams,
        'results': results,
        'completed_count': completed_count,
        'total_passed': total_passed,
        'total_attempts': total_attempts,
        'avg_score': round(avg_score, 1),
        'upcoming_exams': upcoming_exams
    })

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get statistics
    total_students = Student.objects.count()
    total_questions = Question.objects.count()
    total_exams = Exam.objects.count()
    total_results = Result.objects.count()
    
    # Calculate pass rate
    pass_rate = 0
    if total_results > 0:
        passed = Result.objects.filter(passed=True).count()
        pass_rate = round((passed / total_results) * 100, 1)
    
    # Get recent data
    recent_results = Result.objects.order_by('-submitted_at')[:10]
    questions = Question.objects.order_by('-created_at')[:10]
    exams = Exam.objects.order_by('-created_at')[:10]
    students = Student.objects.order_by('-created_at')[:10]
    results = Result.objects.order_by('-submitted_at')
    categories = QuestionCategory.objects.all()
    
    # Analytics - pass rate by exam
    pass_by_exam = []
    for exam in Exam.objects.all()[:5]:
        exam_results = Result.objects.filter(exam=exam)
        if exam_results.exists():
            passed = exam_results.filter(passed=True).count()
            total = exam_results.count()
            pass_by_exam.append({
                'title': exam.title,
                'pass_rate': round((passed / total) * 100, 1) if total > 0 else 0
            })
    
    # Score distribution
    score_distribution = {
        '90-100': Result.objects.filter(score__gte=90).count(),
        '70-89': Result.objects.filter(score__gte=70, score__lt=90).count(),
        '50-69': Result.objects.filter(score__gte=50, score__lt=70).count(),
        '0-49': Result.objects.filter(score__lt=50).count(),
    }
    
    return render(request, 'admin_app.html', {
        'total_students': total_students,
        'total_questions': total_questions,
        'total_exams': total_exams,
        'total_results': total_results,
        'pass_rate': pass_rate,
        'recent_results': recent_results,
        'questions': questions,
        'exams': exams,
        'students': students,
        'results': results,
        'categories': categories,
        'pass_by_exam': pass_by_exam,
        'score_distribution': score_distribution
    })

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def api_add_category(request):
    if request.method == 'POST':
        try:
            # Handle JSON
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                # Handle form data
                data = request.POST.dict()
            QuestionCategory.objects.create(
                name=data.get('name'),
                description=data.get('description', ''),
                color=data.get('color', '#6366f1')
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def api_add_question(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
                
            category = QuestionCategory.objects.get(id=data.get('category')) if data.get('category') else None
        
            # Get random questions from category if specified
            question_text = data.get('question_text')
            option1 = data.get('option1')
            option2 = data.get('option2')
            option3 = data.get('option3')
            option4 = data.get('option4')
            correct_answer = data.get('correct_answer')
            
            # Shuffle options for randomization
            options = [
                {'text': option1, 'is_correct': correct_answer == option1},
                {'text': option2, 'is_correct': correct_answer == option2},
                {'text': option3, 'is_correct': correct_answer == option3},
                {'text': option4, 'is_correct': correct_answer == option4},
            ]
            random.shuffle(options)
            
            Question.objects.create(
                question_text=question_text,
                option1=options[0]['text'],
                option2=options[1]['text'],
                option3=options[2]['text'],
                option4=options[3]['text'],
                correct_answer=correct_answer,
                category=category,
                marks=data.get('marks', 1),
                difficulty=data.get('difficulty', 'medium')
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def api_delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    question.delete()
    return JsonResponse({'success': True})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def api_add_exam(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
            category = QuestionCategory.objects.get(id=data.get('category')) if data.get('category') else None
            Exam.objects.create(
                title=data.get('title'),
                description=data.get('description', ''),
                category=category,
                duration_minutes=int(data.get('duration_minutes', 30)),
                number_of_questions=int(data.get('number_of_questions', 10)),
                passing_percentage=int(data.get('passing_percentage', 50)),
                exam_date=data.get('exam_date'),
                start_time=data.get('start_time'),
                end_time=data.get('end_time'),
                randomize_questions=data.get('randomize_questions', True),
                show_results=data.get('show_results', True)
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def api_delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    exam.delete()
    return JsonResponse({'success': True})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def api_toggle_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    exam.is_active = not exam.is_active
    exam.save()
    return JsonResponse({'success': True, 'is_active': exam.is_active})

@login_required
def start_exam(request, exam_id):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    student = get_object_or_404(Student, user=request.user)
    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    
    # Check if already completed
    existing_session = ExamSession.objects.filter(student=student, exam=exam, is_completed=True).first()
    if existing_session:
        messages.error(request, 'You have already completed this exam')
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        tab_switch_count = int(request.POST.get('tab_switch_count', 0))
        
        session = ExamSession.objects.filter(student=student, exam=exam, is_completed=False).first()
        if not session:
            # Random question generation
            questions = list(Question.objects.filter(
                Q(category=exam.category) | Q(category__isnull=True),
                is_active=True
            ))
            
            if exam.randomize_questions:
                # Shuffle and select random questions
                random.shuffle(questions)
                selected_questions = questions[:exam.number_of_questions]
            else:
                selected_questions = questions[:exam.number_of_questions]
            
            # Shuffle answer options for each question
            randomized_questions = []
            for q in selected_questions:
                q_dict = {
                    'id': q.id,
                    'question_text': q.question_text,
                    'option1': q.option1,
                    'option2': q.option2,
                    'option3': q.option3,
                    'option4': q.option4,
                    'correct_answer': q.correct_answer,
                    'marks': q.marks
                }
                # Shuffle options
                options = [
                    q.option1, q.option2, q.option3, q.option4
                ]
                random.shuffle(options)
                q_dict['shuffled_options'] = options
                randomized_questions.append(q_dict)
            
            session = ExamSession.objects.create(
                student=student, exam=exam,
                questions=[q['id'] for q in randomized_questions],
                answers={},
                ip_address=request.META.get('REMOTE_ADDR', '')
            )
        
        # Collect answers
        for q_id in session.questions:
            selected_answer = request.POST.get(str(q_id))
            if selected_answer:
                session.answers[str(q_id)] = selected_answer
        
        # Calculate score
        questions = Question.objects.filter(id__in=session.questions)
        score = 0
        total_marks = 0
        correct = 0
        wrong = 0
        
        for question in questions:
            total_marks += question.marks
            if session.answers.get(str(question.id)) == question.correct_answer:
                score += question.marks
                correct += 1
            else:
                wrong += 1
        
        percentage = int((score / total_marks) * 100) if total_marks > 0 else 0
        passed = percentage >= exam.passing_percentage
        
        time_taken = int((timezone.now() - session.started_at).total_seconds() / 60)
        
        session.score = score
        session.total_marks = total_marks
        session.passed = passed
        session.is_completed = True
        session.submitted_at = timezone.now()
        session.save()
        
        # Get violations from form
        violations_data = {'tabSwitch': 0, 'copyPaste': 0, 'rightClick': 0, 'focusLost': 0, 'screenshot': 0}
        violations_json = request.POST.get('violations_data')
        print(f"DEBUG: violations_json received: {violations_json}")
        if violations_json:
            try:
                violations_data = json.loads(violations_json)
                print(f"DEBUG: violations_data parsed: {violations_data}")
            except Exception as e:
                print(f"DEBUG: Error parsing violations: {e}")
        
        total_violations = sum(violations_data.values())
        print(f"DEBUG: total_violations: {total_violations}")
        
        # Create result with violations
        Result.objects.create(
            student=student, exam=exam, score=percentage,
            total_questions=len(session.questions), correct_answers=correct,
            wrong_answers=wrong, passing_percentage=exam.passing_percentage,
            passed=passed, time_taken=int(time_taken),
            violations_tab_switch=violations_data.get('tabSwitch', 0),
            violations_copy_paste=violations_data.get('copyPaste', 0),
            violations_right_click=violations_data.get('rightClick', 0),
            violations_focus_lost=violations_data.get('focusLost', 0),
            violations_screenshot=violations_data.get('screenshot', 0),
            total_violations=total_violations,
            violations_json=violations_data
        )
        
        return render(request, 'result.html', {
            'score': score, 'total': total_marks,
            'percentage': percentage, 'passed': passed,
            'exam_title': exam.title, 'correct': correct,
            'wrong': wrong, 'time_taken': int(time_taken),
            'total_violations': total_violations,
            'violations_data': violations_data
        })
    
    # Get or create exam session
    active_session = ExamSession.objects.filter(student=student, exam=exam, is_completed=False).first()
    
    if active_session:
        questions = Question.objects.filter(id__in=active_session.questions)
        # Shuffle options for display randomization
        question_list = []
        for q in questions:
            options = [q.option1, q.option2, q.option3, q.option4]
            random.shuffle(options)
            question_list.append({
                'id': q.id,
                'question_text': q.question_text,
                'option1': options[0],
                'option2': options[1],
                'option3': options[2],
                'option4': options[3],
                'marks': q.marks
            })
    else:
        # Random question generation - fetch and shuffle
        questions = list(Question.objects.filter(
            Q(category=exam.category) | Q(category__isnull=True),
            is_active=True
        ))
        
        if exam.randomize_questions:
            random.shuffle(questions)
            selected_questions = questions[:exam.number_of_questions]
        else:
            selected_questions = questions[:exam.number_of_questions]
        
        # Shuffle options for each question
        question_list = []
        for q in selected_questions:
            options = [q.option1, q.option2, q.option3, q.option4]
            random.shuffle(options)
            question_list.append({
                'id': q.id,
                'question_text': q.question_text,
                'option1': options[0],
                'option2': options[1],
                'option3': options[2],
                'option4': options[3],
                'marks': q.marks
            })
        
        active_session = ExamSession.objects.create(
            student=student, exam=exam,
            questions=[q['id'] for q in question_list],
            answers={},
            ip_address=request.META.get('REMOTE_ADDR', '')
        )

    remaining_time = exam.duration_minutes * 60
    
    return render(request, 'exam.html', {
        'questions': question_list,
        'exam': exam,
        'session': active_session,
        'remaining_time': remaining_time
    })

@login_required
def view_my_results(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    student = get_object_or_404(Student, user=request.user)
    results = Result.objects.filter(student=student).order_by('-submitted_at')
    return render(request, 'student_app.html', {
        'student': student, 'results': results, 'show_results_only': True
    })

@login_required
@user_passes_test(is_admin)
def api_get_analytics(request):
    if request.method == 'GET':
        exam_id = request.GET.get('exam_id')
        if exam_id:
            exam = Exam.objects.get(id=exam_id)
            results = Result.objects.filter(exam=exam)
            data = {
                'total_attempts': results.count(),
                'pass_rate': round((results.filter(passed=True).count() / results.count() * 100), 1) if results.exists() else 0,
                'avg_score': round(results.aggregate(Avg('score'))['score__avg'] or 0, 1),
                'highest_score': results.aggregate(Max('score'))['score__max'] or 0,
                'lowest_score': results.aggregate(Min('score'))['score__min'] or 0,
            }
        else:
            data = {
                'total_students': Student.objects.count(),
                'total_questions': Question.objects.count(),
                'total_exams': Exam.objects.count(),
                'total_results': Result.objects.count(),
                'pass_rate': round((Result.objects.filter(passed=True).count() / Result.objects.count() * 100), 1) if Result.objects.exists() else 0,
            }
        return JsonResponse(data)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def practice_hub(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    student = get_object_or_404(Student, user=request.user)
    
    practice_tests = PracticeTest.objects.filter(is_published=True)[:6]
    worksheets = Worksheet.objects.filter(is_published=True)[:6]
    study_materials = StudyMaterial.objects.filter(is_published=True)[:6]
    
    recent_sessions = PracticeSession.objects.filter(student=student).order_by('-started_at')[:5]
    
    progress = StudentProgress.objects.filter(student=student)
    total_attempted = sum(p.total_questions_attempted for p in progress)
    total_correct = sum(p.correct_answers for p in progress)
    
    bookmarks = Bookmark.objects.filter(student=student).count()
    achievements = Achievement.objects.filter(student=student).count()
    
    return render(request, 'practice_hub.html', {
        'student': student,
        'practice_tests': practice_tests,
        'worksheets': worksheets,
        'study_materials': study_materials,
        'recent_sessions': recent_sessions,
        'total_attempted': total_attempted,
        'total_correct': total_correct,
        'accuracy': round((total_correct / total_attempted * 100), 1) if total_attempted > 0 else 0,
        'bookmarks': bookmarks,
        'achievements': achievements,
    })


@login_required
def practice_tests(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    student = get_object_or_404(Student, user=request.user)
    
    category_id = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    
    practice_tests = PracticeTest.objects.filter(is_published=True)
    
    if category_id:
        practice_tests = practice_tests.filter(category_id=category_id)
    if difficulty and difficulty != 'all':
        practice_tests = practice_tests.filter(difficulty=difficulty)
    
    categories = QuestionCategory.objects.all()
    recent_results = PracticeSession.objects.filter(student=student, is_completed=True).order_by('-completed_at')[:10]
    
    return render(request, 'practice_tests.html', {
        'student': student,
        'practice_tests': practice_tests,
        'categories': categories,
        'recent_results': recent_results,
    })


@login_required
def worksheets(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    student = get_object_or_404(Student, user=request.user)
    
    category_id = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    
    worksheets_list = Worksheet.objects.filter(is_published=True)
    
    if category_id:
        worksheets_list = worksheets_list.filter(category_id=category_id)
    if difficulty and difficulty != 'all':
        worksheets_list = worksheets_list.filter(difficulty=difficulty)
    
    categories = QuestionCategory.objects.all()
    
    return render(request, 'worksheets.html', {
        'student': student,
        'worksheets': worksheets_list,
        'categories': categories,
    })


@login_required
def study_materials(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    student = get_object_or_404(Student, user=request.user)
    
    category_id = request.GET.get('category')
    material_type = request.GET.get('type')
    
    materials = StudyMaterial.objects.filter(is_published=True)
    
    if category_id:
        materials = materials.filter(category_id=category_id)
    if material_type:
        materials = materials.filter(material_type=material_type)
    
    categories = QuestionCategory.objects.all()
    
    return render(request, 'study_materials.html', {
        'student': student,
        'materials': materials,
        'categories': categories,
    })


@login_required
def start_practice_test(request, test_id):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    student = get_object_or_404(Student, user=request.user)
    practice_test = get_object_or_404(PracticeTest, id=test_id, is_published=True)
    
    questions = Question.objects.filter(
        Q(category=practice_test.category) | Q(category__isnull=True),
        is_active=True
    )
    if practice_test.difficulty != 'all':
        questions = questions.filter(difficulty=practice_test.difficulty)
    
    questions = list(questions)
    random.shuffle(questions)
    
    # Get number of questions from worksheet or use default
    num_questions = 10
    if practice_test.worksheet:
        num_questions = practice_test.worksheet.number_of_questions
    
    selected_questions = questions[:num_questions]
    
    session = PracticeSession.objects.create(
        student=student,
        practice_test=practice_test,
        questions=[q.id for q in selected_questions]
    )
    
    question_list = []
    for q in selected_questions:
        options = [q.option1, q.option2, q.option3, q.option4]
        random.shuffle(options)
        question_list.append({
            'id': q.id,
            'question_text': q.question_text,
            'option1': options[0],
            'option2': options[1],
            'option3': options[2],
            'option4': options[3],
            'correct_answer': q.correct_answer if practice_test.show_answers_immediately else None,
            'marks': q.marks
        })
    
    is_bookmarked = Bookmark.objects.filter(student=student, question_id__in=[q.id for q in selected_questions]).values_list('question_id', flat=True)
    
    return render(request, 'practice_exam.html', {
        'student': student,
        'practice_test': practice_test,
        'session': session,
        'questions': question_list,
        'is_bookmarked': list(is_bookmarked),
        'show_answers': practice_test.show_answers_immediately,
    })


@login_required
def submit_practice_test(request):
    if request.method == 'POST' and request.user.is_authenticated:
        student = get_object_or_404(Student, user=request.user)
        session_id = request.POST.get('session_id')
        session = get_object_or_404(PracticeSession, id=session_id, student=student)
        
        answers = json.loads(request.POST.get('answers', '{}'))
        session.answers = answers
        
        questions = Question.objects.filter(id__in=session.questions)
        
        score = 0
        total_marks = 0
        correct = 0
        wrong = 0
        
        for q in questions:
            total_marks += q.marks
            selected = answers.get(str(q.id))
            
            if selected == q.correct_answer:
                score += q.marks
                correct += 1
            elif selected:
                wrong += 1
            
            QuestionAttempt.objects.create(
                student=student,
                question=q,
                practice_test=session.practice_test,
                selected_answer=selected or '',
                is_correct=(selected == q.correct_answer),
            )
        
        session.score = score
        session.total_marks = total_marks
        session.is_completed = True
        session.completed_at = timezone.now()
        session.save()
        
        percentage = int((score / total_marks) * 100) if total_marks > 0 else 0
        
        progress, _ = StudentProgress.objects.get_or_create(
            student=student,
            category=session.practice_test.category
        )
        progress.total_questions_attempted += len(questions)
        progress.correct_answers += correct
        progress.wrong_answers += wrong
        progress.save()
        
        if percentage == 100:
            Achievement.objects.get_or_create(
                student=student,
                achievement_type='perfect_score',
                defaults={
                    'title': 'Perfect Score',
                    'description': 'Achieved 100% in a practice test',
                    'icon': 'star'
                }
            )
        
        return render(request, 'practice_result.html', {
            'session': session,
            'score': score,
            'total': total_marks,
            'percentage': percentage,
            'correct': correct,
            'wrong': wrong,
            'show_answers': session.practice_test.show_answers_immediately,
            'questions': [{'id': q.id, 'question_text': q.question_text, 'option1': q.option1, 
                          'option2': q.option2, 'option3': q.option3, 'option4': q.option4,
                          'correct_answer': q.correct_answer} for q in questions],
        })
    
    return redirect('practice_hub')


@login_required
def toggle_bookmark(request):
    if request.method == 'POST' and request.user.is_authenticated:
        student = get_object_or_404(Student, user=request.user)
        question_id = request.POST.get('question_id')
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
def my_bookmarks(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    student = get_object_or_404(Student, user=request.user)
    
    bookmarks = Bookmark.objects.filter(student=student).select_related('question')
    
    return render(request, 'bookmarks.html', {
        'student': student,
        'bookmarks': bookmarks,
    })


@login_required
def my_progress(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    student = get_object_or_404(Student, user=request.user)
    
    progress_by_category = StudentProgress.objects.filter(student=student).select_related('category')
    
    total_attempted = sum(p.total_questions_attempted for p in progress_by_category)
    total_correct = sum(p.correct_answers for p in progress_by_category)
    total_wrong = sum(p.wrong_answers for p in progress_by_category)
    
    attempts = QuestionAttempt.objects.filter(student=student).order_by('-created_at')[:50]
    
    achievements = Achievement.objects.filter(student=student)
    
    return render(request, 'progress.html', {
        'student': student,
        'progress_by_category': progress_by_category,
        'total_attempted': total_attempted,
        'total_correct': total_correct,
        'total_wrong': total_wrong,
        'accuracy': round((total_correct / total_attempted * 100), 1) if total_attempted > 0 else 0,
        'attempts': attempts,
        'achievements': achievements,
    })


@login_required
def practice_result(request, session_id):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    student = get_object_or_404(Student, user=request.user)
    session = get_object_or_404(PracticeSession, id=session_id, student=student)
    
    if not session.is_completed:
        return redirect('practice_hub')
    
    questions = Question.objects.filter(id__in=session.questions)
    percentage = int((session.score / session.total_marks) * 100) if session.total_marks > 0 else 0
    
    return render(request, 'practice_result.html', {
        'session': session,
        'score': session.score,
        'total': session.total_marks,
        'percentage': percentage,
        'correct': session.score,
        'wrong': session.total_marks - session.score,
        'show_answers': True,
        'questions': [{'id': q.id, 'question_text': q.question_text, 'option1': q.option1, 
                      'option2': q.option2, 'option3': q.option3, 'option4': q.option4,
                      'correct_answer': q.correct_answer} for q in questions],
        'review_only': True,
    })


@login_required
@user_passes_test(is_admin)
def api_add_worksheet(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        difficulty = request.POST.get('difficulty', 'all')
        number_of_questions = int(request.POST.get('number_of_questions', 10))
        time_limit_minutes = int(request.POST.get('time_limit_minutes', 0))
        
        category = QuestionCategory.objects.get(id=category_id) if category_id else None
        
        worksheet = Worksheet.objects.create(
            title=title,
            description=description,
            category=category,
            difficulty=difficulty,
            number_of_questions=number_of_questions,
            time_limit_minutes=time_limit_minutes,
            is_published=True
        )
        
        return JsonResponse({'success': True, 'id': worksheet.id})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
@user_passes_test(is_admin)
def api_add_study_material(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        material_type = request.POST.get('material_type', 'notes')
        content = request.POST.get('content', '')
        
        category = QuestionCategory.objects.get(id=category_id) if category_id else None
        
        material = StudyMaterial.objects.create(
            title=title,
            description=description,
            category=category,
            material_type=material_type,
            content=content,
            is_published=True
        )
        
        return JsonResponse({'success': True, 'id': material.id})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
@user_passes_test(is_admin)
def api_add_practice_test(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        difficulty = request.POST.get('difficulty', 'all')
        number_of_questions = int(request.POST.get('number_of_questions', 10))
        is_timed = request.POST.get('is_timed') == 'true'
        time_limit_minutes = int(request.POST.get('time_limit_minutes', 0))
        show_answers_immediately = request.POST.get('show_answers_immediately') == 'true'
        
        category = QuestionCategory.objects.get(id=category_id) if category_id else None
        
        practice_test = PracticeTest.objects.create(
            title=title,
            description=description,
            category=category,
            difficulty=difficulty,
            number_of_questions=number_of_questions,
            is_timed=is_timed,
            time_limit_minutes=time_limit_minutes,
            show_answers_immediately=show_answers_immediately,
            is_published=True
        )
        
        return JsonResponse({'success': True, 'id': practice_test.id})
    return JsonResponse({'error': 'Invalid request'}, status=400)
