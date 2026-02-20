from django.contrib import admin
from .models import Student, Question, QuestionCategory, Exam, ExamSession, Result

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'created_at')
    search_fields = ('user__username', 'student_id')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'category', 'marks', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('question_text',)

@admin.register(QuestionCategory)
class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'duration_minutes', 'number_of_questions', 'exam_date', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('title',)

@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'is_completed', 'started_at')
    list_filter = ('is_completed',)

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'passed', 'submitted_at')
    list_filter = ('passed',)
