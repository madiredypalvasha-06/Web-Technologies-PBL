from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

class QuestionCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='#6366f1')
    
    def __str__(self):
        return self.name

class Question(models.Model):
    question_text = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)
    category = models.ForeignKey(QuestionCategory, on_delete=models.SET_NULL, null=True, blank=True)
    marks = models.IntegerField(default=1)
    difficulty = models.CharField(max_length=20, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.question_text[:50]

class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(QuestionCategory, on_delete=models.SET_NULL, null=True, blank=True)
    duration_minutes = models.IntegerField(default=30)
    number_of_questions = models.IntegerField(default=10)
    passing_percentage = models.IntegerField(default=50)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    randomize_questions = models.BooleanField(default=True)
    show_results = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class ExamSession(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    questions = models.JSONField(default=list)
    answers = models.JSONField(default=dict)
    score = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    ip_address = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.student.user.username} - {self.exam.title}"

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    passing_percentage = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)
    time_taken = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Malpractice tracking
    violations_tab_switch = models.IntegerField(default=0)
    violations_copy_paste = models.IntegerField(default=0)
    violations_right_click = models.IntegerField(default=0)
    violations_focus_lost = models.IntegerField(default=0)
    violations_screenshot = models.IntegerField(default=0)
    total_violations = models.IntegerField(default=0)
    violations_json = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.student.user.username} - {self.exam.title}: {self.score}%"

class Analytics(models.Model):
    total_students = models.IntegerField(default=0)
    total_exams = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    total_results = models.IntegerField(default=0)
    avg_pass_rate = models.FloatField(default=0)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Analytics - {self.date}"


class Worksheet(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(QuestionCategory, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.CharField(max_length=20, choices=[('all', 'All Levels'), ('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='all')
    number_of_questions = models.IntegerField(default=10)
    time_limit_minutes = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class StudyMaterial(models.Model):
    MATERIAL_TYPES = [
        ('notes', 'Notes'),
        ('video', 'Video'),
        ('article', 'Article'),
        ('cheatsheet', 'Cheat Sheet'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(QuestionCategory, on_delete=models.SET_NULL, null=True, blank=True)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, default='notes')
    content = models.TextField(blank=True)
    file_url = models.FileField(upload_to='study_materials/', blank=True, null=True)
    external_link = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class PracticeTest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(QuestionCategory, on_delete=models.SET_NULL, null=True, blank=True)
    worksheet = models.ForeignKey(Worksheet, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.CharField(max_length=20, choices=[('all', 'All Levels'), ('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='all')
    is_timed = models.BooleanField(default=False)
    time_limit_minutes = models.IntegerField(default=0)
    show_answers_immediately = models.BooleanField(default=True)
    allow_review = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class PracticeSession(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    practice_test = models.ForeignKey(PracticeTest, on_delete=models.CASCADE, null=True, blank=True)
    worksheet = models.ForeignKey(Worksheet, on_delete=models.CASCADE, null=True, blank=True)
    questions = models.JSONField(default=list)
    answers = models.JSONField(default=dict)
    score = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.user.username} - {self.practice_test or self.worksheet}"


class Bookmark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'question')
    
    def __str__(self):
        return f"{self.student.user.username} - {self.question.question_text[:30]}"


class QuestionAttempt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    practice_test = models.ForeignKey(PracticeTest, on_delete=models.CASCADE, null=True, blank=True)
    worksheet = models.ForeignKey(Worksheet, on_delete=models.CASCADE, null=True, blank=True)
    selected_answer = models.CharField(max_length=255, blank=True)
    is_correct = models.BooleanField(default=False)
    is_bookmarked = models.BooleanField(default=False)
    attempt_number = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.user.username} - Q{self.question.id}"


class StudentProgress(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    category = models.ForeignKey(QuestionCategory, on_delete=models.SET_NULL, null=True, blank=True)
    total_questions_attempted = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    average_time_per_question = models.FloatField(default=0)
    streak_days = models.IntegerField(default=0)
    last_practice_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'category')
    
    def __str__(self):
        return f"{self.student.user.username} - {self.category or 'Overall'} Progress"


class Achievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('first_test', 'First Test'),
        ('streak_7', '7 Day Streak'),
        ('streak_30', '30 Day Streak'),
        ('perfect_score', 'Perfect Score'),
        ('speed_demon', 'Speed Demon'),
        ('consistent', 'Consistent Learner'),
        ('category_master', 'Category Master'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    achievement_type = models.CharField(max_length=50, choices=ACHIEVEMENT_TYPES)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='trophy')
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'achievement_type')
    
    def __str__(self):
        return f"{self.student.user.username} - {self.title}"
