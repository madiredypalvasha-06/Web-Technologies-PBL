import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_exam.settings')
django.setup()

from exam_app.models import QuestionCategory, Question, Exam, Student, User
from django.contrib.auth import get_user_model

print("Creating categories...")
categories_data = [
    ('Programming', 'Programming related questions'),
    ('Database', 'Database and SQL questions'),
    ('Web Development', 'Web development questions'),
    ('Networking', 'Computer networking questions'),
    ('Operating Systems', 'OS related questions'),
    ('Python', 'Python programming questions'),
    ('JavaScript', 'JavaScript questions'),
    ('General', 'General IT knowledge'),
]

for name, desc in categories_data:
    QuestionCategory.objects.get_or_create(name=name, defaults={'description': desc})

print(f"Created {QuestionCategory.objects.count()} categories")

print("Creating sample exam...")
from datetime import date, time

exam, created = Exam.objects.get_or_create(
    title="Python Fundamentals",
    defaults={
        'description': 'Test your Python knowledge',
        'duration_minutes': 30,
        'number_of_questions': 25,
        'passing_percentage': 50,
        'exam_date': date.today(),
        'start_time': time(9, 0),
        'end_time': time(17, 0),
        'is_active': True
    }
)
if created:
    print("Created sample exam")
else:
    print("Exam already exists")

print("\n=== Setup Complete ===")
print("Now create a superuser with: python manage.py createsuperuser")
