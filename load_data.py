import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_exam.settings')
django.setup()

from exam_app.models import QuestionCategory, Question, Exam, PracticeTest, Worksheet, StudyMaterial
from datetime import date, time

print("=" * 50)
print("Loading Sample Data to Shared Database")
print("=" * 50)

# Create Categories
print("\n[1] Creating categories...")
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
print(f"  Created {QuestionCategory.objects.count()} categories")

# Create Questions
print("\n[2] Creating questions...")
python_cat = QuestionCategory.objects.get(name='Python')
db_cat = QuestionCategory.objects.get(name='Database')
web_cat = QuestionCategory.objects.get(name='Web Development')
net_cat = QuestionCategory.objects.get(name='Networking')
os_cat = QuestionCategory.objects.get(name='Operating Systems')
gen_cat = QuestionCategory.objects.get(name='General')
prog_cat = QuestionCategory.objects.get(name='Programming')
js_cat = QuestionCategory.objects.get(name='JavaScript')

questions_data = [
    # Python Questions
    (python_cat, 'What is the output of print(type([]))?', 'list', 'tuple', 'dict', 'set', 1),
    (python_cat, 'Which method is used to add an element at the end of a list?', 'append()', 'add()', 'insert()', 'extend()', 1),
    (python_cat, 'What is the correct way to create a dictionary?', '[a:b]', 'dict()', '{a:b}', 'both B and C', 4),
    (python_cat, 'What does len() return for an empty list?', '0', '1', 'None', 'False', 1),
    (python_cat, 'Which keyword is used to define a function?', 'function', 'def', 'func', 'define', 2),
    (python_cat, 'What is the output of 2**3?', '6', '8', '9', '5', 2),
    (python_cat, 'Which is not a Python data type?', 'int', 'str', 'char', 'bool', 3),
    (python_cat, 'How do you start a comment in Python?', '//', '#', '/*', '--', 2),
    (python_cat, 'What is the output of bool([])?', 'True', 'False', 'None', 'Error', 2),
    
    # Database Questions
    (db_cat, 'What does SQL stand for?', 'Structured Query Language', 'Simple Query Language', 'System Query Language', 'Standard Query Language', 1),
    (db_cat, 'Which command is used to create a table?', 'CREATE TABLE', 'ADD TABLE', 'NEW TABLE', 'MAKE TABLE', 1),
    (db_cat, 'What is a primary key?', 'Unique identifier', 'First column', 'Index', 'Foreign key', 1),
    (db_cat, 'Which JOIN returns only matching rows?', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN', 'FULL JOIN', 3),
    (db_cat, 'What does INSERT do?', 'Adds data', 'Deletes data', 'Updates data', 'Reads data', 1),
    (db_cat, 'Which is a DDL command?', 'SELECT', 'INSERT', 'DROP', 'UPDATE', 3),
    (db_cat, 'What is normalization?', 'Data sorting', 'Reducing redundancy', 'Data encryption', 'Data compression', 2),
    (db_cat, 'What is a foreign key?', 'Primary key of another table', 'Unique key', 'Index key', 'Composite key', 1),
    
    # Web Development Questions
    (web_cat, 'What does HTML stand for?', 'Hyper Text Markup Language', 'High Tech Modern Language', 'Home Tool Markup Language', 'Hyperlinks Text Mark Language', 1),
    (web_cat, 'Which tag is used for largest heading?', '<h6>', '<h1>', '<head>', '<header>', 2),
    (web_cat, 'What does CSS stand for?', 'Creative Style Sheets', 'Cascading Style Sheets', 'Computer Style Sheets', 'Colorful Style Sheets', 2),
    (web_cat, 'Which is not a JavaScript framework?', 'React', 'Angular', 'Django', 'Vue', 3),
    (web_cat, 'What does API stand for?', 'Application Programming Interface', 'Advanced Program Interface', 'Application Program Integration', 'Automated Protocol Interface', 1),
    (web_cat, 'Which protocol is used for web?', 'FTP', 'HTTP', 'SMTP', 'TCP', 2),
    (web_cat, 'What is JSON?', 'Java Script Object Notation', 'Java Standard Object Notation', 'JavaScript Object Notation', 'Java Source Object Notation', 3),
    (web_cat, 'Which is server-side language?', 'HTML', 'CSS', 'Python', 'JavaScript', 3),
    
    # Networking Questions
    (net_cat, 'What does HTTP stand for?', 'HyperText Transfer Protocol', 'High Transfer Text Protocol', 'HyperText Transmission Process', 'High Text Transfer Protocol', 1),
    (net_cat, 'What is IP address?', 'Internet Protocol', 'Internet Provider', 'Internal Protocol', 'Interconnected Protocol', 1),
    (net_cat, 'Which port is for HTTP?', '80', '443', '21', '25', 1),
    (net_cat, 'What does DNS do?', 'Converts IP to domain', 'Encrypts data', 'Transfers files', 'Manages email', 1),
    (net_cat, 'What is LAN?', 'Local Area Network', 'Large Area Network', 'Long Area Network', 'Link Area Network', 1),
    (net_cat, 'Which layer is HTTP?', 'Transport', 'Network', 'Application', 'Data Link', 3),
    (net_cat, 'What does TCP stand for?', 'Transfer Control Protocol', 'Transmission Control Protocol', 'Text Control Protocol', 'Transmission Communication Protocol', 2),
    (net_cat, 'What is a firewall?', 'Security system', 'Network switch', 'Router', 'Modem', 1),
    
    # Operating Systems Questions
    (os_cat, 'What does CPU stand for?', 'Central Processing Unit', 'Computer Processing Unit', 'Central Program Unit', 'Core Processing Unit', 1),
    (os_cat, 'What is RAM?', 'Random Access Memory', 'Read Access Memory', 'Run Access Memory', 'Ready Access Memory', 1),
    (os_cat, 'What does OS stand for?', 'Open System', 'Operating System', 'Online System', 'Output System', 2),
    (os_cat, 'Which is not an OS?', 'Windows', 'Linux', 'MacOS', 'Python', 4),
    (os_cat, 'What is virtual memory?', 'Extra RAM', 'Hard disk space used as RAM', 'Cache memory', 'ROM', 2),
    (os_cat, 'What does BIOS do?', 'Runs applications', 'Boot process', 'Manages files', 'Network connection', 2),
    (os_cat, 'What is a process?', 'Running program', 'File', 'Folder', 'Application', 1),
    (os_cat, 'What is deadlock?', 'System hang', 'Two processes waiting for each other', 'Memory full', 'CPU overload', 2),
    
    # General Questions
    (gen_cat, 'What does WWW stand for?', 'World Wide Web', 'Western World Web', 'Wide World Web', 'World Web Wide', 1),
    (gen_cat, 'What is AI?', 'Artificial Intelligence', 'Automated Information', 'Advanced Internet', 'Artificial Information', 1),
    (gen_cat, 'What does URL stand for?', 'Uniform Resource Locator', 'Universal Resource Link', 'Unique Resource Locator', 'Unified Resource Link', 1),
    (gen_cat, 'What is cloud computing?', 'Weather computing', 'Internet-based computing', 'Offline computing', 'Quantum computing', 2),
    (gen_cat, 'What does IoT stand for?', 'Internet of Things', 'Internet of Technology', 'Internal of Things', 'Integrated of Technology', 1),
    
    # Programming Questions
    (prog_cat, 'What is a variable?', 'Storage location', 'Data type', 'Function', 'Loop', 1),
    (prog_cat, 'What is a loop?', 'Conditional statement', 'Repeats code', 'Function call', 'Variable', 2),
    (prog_cat, 'What is OOP?', 'Object Oriented Programming', 'Online Programming', 'Output Oriented Programming', 'Object Oriented Process', 1),
    (prog_cat, 'What is inheritance?', 'Child class from parent', 'New variable', 'Loop type', 'Function type', 1),
    (prog_cat, 'What is a function?', 'Reusable code block', 'Variable', 'Loop', 'Class', 1),
    (prog_cat, 'What is an array?', 'List of elements', 'Single value', 'Condition', 'Loop', 1),
    (prog_cat, 'What is a class?', 'Blueprint for objects', 'Function', 'Variable', 'Loop', 1),
    (prog_cat, 'What is an algorithm?', 'Step-by-step solution', 'Programming language', 'Data type', 'Operating system', 1),
    
    # JavaScript Questions
    (js_cat, 'How do you declare a variable in JS?', 'var x', 'variable x', 'int x', 'let x = 5', 4),
    (js_cat, 'What is console.log()?', 'Print to console', 'Input function', 'Alert', 'Loop', 1),
    (js_cat, 'Which is JS framework?', 'Django', 'Laravel', 'React', 'Flask', 3),
    (js_cat, 'What does DOM stand for?', 'Document Object Model', 'Data Object Model', 'Digital Object Model', 'Document Order Model', 1),
    (js_cat, 'How do you write comment in JS?', '// comment', '<!-- comment -->', '# comment', '** comment **', 1),
    (js_cat, 'What is JSON?', 'Data format', 'Function', 'Variable', 'Loop', 1),
    (js_cat, 'Which method adds to array end?', 'push()', 'pop()', 'shift()', 'unshift()', 1),
    (js_cat, 'What is === in JS?', 'Strict equality', 'Assignment', 'Comparison', 'Not equal', 1),
]

for cat, q, a1, a2, a3, a4, correct in questions_data:
    Question.objects.get_or_create(
        question_text=q,
        defaults={
            'category': cat,
            'option1': a1,
            'option2': a2,
            'option3': a3,
            'option4': a4,
            'correct_answer': correct,
            'marks': 1,
            'difficulty': 'Medium'
        }
    )
print(f"  Created {Question.objects.count()} questions")

# Create Exams
print("\n[3] Creating exams...")
exams_data = [
    ('Python Fundamentals', 'Test your Python knowledge', 30, 25, 50),
    ('Database Essentials', 'SQL and database concepts', 15, 20, 50),
    ('Web Development Basics', 'HTML, CSS, JS fundamentals', 15, 20, 50),
    ('Networking Concepts', 'Computer networking basics', 15, 20, 50),
    ('Operating Systems Basics', 'OS concepts and processes', 15, 20, 50),
    ('General IT Knowledge', 'General IT awareness', 30, 25, 50),
    ('JavaScript Basics', 'JavaScript programming', 30, 25, 50),
    ('Database Management', 'Advanced database concepts', 30, 25, 50),
]

for title, desc, duration, questions, passing in exams_data:
    Exam.objects.get_or_create(
        title=title,
        defaults={
            'description': desc,
            'duration_minutes': duration,
            'number_of_questions': questions,
            'passing_percentage': passing,
            'exam_date': date.today(),
            'start_time': time(9, 0),
            'end_time': time(17, 0),
            'is_active': True
        }
    )
print(f"  Created {Exam.objects.count()} exams")

# Create Practice Tests
print("\n[4] Creating practice tests...")
practice_tests = [
    ('Python Practice Test', 'Test your Python skills', 'Python', 'Medium', 10, 15),
    ('Database Quiz', 'SQL fundamentals quiz', 'Database', 'Easy', 10, 10),
    ('Web Dev Quiz', 'Web development basics', 'Web Development', 'Easy', 10, 10),
    ('Networking Quiz', 'Networking concepts', 'Networking', 'Medium', 10, 15),
    ('OS Quiz', 'Operating systems basics', 'Operating Systems', 'Easy', 10, 10),
    ('JavaScript Practice', 'JS programming practice', 'JavaScript', 'Medium', 10, 15),
    ('General Knowledge', 'IT general awareness', 'General', 'Easy', 10, 10),
]

for title, desc, category, difficulty, questions, time_limit in practice_tests:
    PracticeTest.objects.get_or_create(
        title=title,
        defaults={
            'description': desc,
            'category': category,
            'difficulty': difficulty,
            'number_of_questions': questions,
            'time_limit': time_limit,
            'is_active': True
        }
    )
print(f"  Created {PracticeTest.objects.count()} practice tests")

# Create Worksheets
print("\n[5] Creating worksheets...")
worksheets = [
    ('Python Worksheet 1', 'Python basics exercises', 'Python', 'Easy', 15),
    ('Database Worksheet', 'SQL practice problems', 'Database', 'Medium', 20),
    ('Web Dev Worksheet', 'HTML/CSS exercises', 'Web Development', 'Easy', 15),
    ('Networking Worksheet', 'Network topology problems', 'Networking', 'Medium', 15),
    ('OS Worksheet', 'Process management exercises', 'Operating Systems', 'Medium', 15),
    ('JavaScript Worksheet', 'JS coding practice', 'JavaScript', 'Medium', 20),
    ('General Worksheet', 'IT awareness questions', 'General', 'Easy', 10),
]

for title, desc, category, difficulty, questions in worksheets:
    Worksheet.objects.get_or_create(
        title=title,
        defaults={
            'description': desc,
            'category': category,
            'difficulty': difficulty,
            'number_of_questions': questions,
            'is_active': True
        }
    )
print(f"  Created {Worksheet.objects.count()} worksheets")

# Create Study Materials
print("\n[6] Creating study materials...")
materials = [
    ('Python Notes', 'Complete Python programming notes', 'Python', 'Notes'),
    ('SQL Cheat Sheet', 'Quick SQL reference guide', 'Database', 'Cheat Sheet'),
    ('Web Dev Tutorial', 'HTML CSS JS tutorial', 'Web Development', 'Article'),
    ('Networking Guide', 'Network fundamentals guide', 'Networking', 'Article'),
    ('OS Concepts', 'Operating systems notes', 'Operating Systems', 'Notes'),
    ('JavaScript Tutorial', 'JS for beginners', 'JavaScript', 'Video'),
    ('IT General Knowledge', 'General IT awareness', 'General', 'Notes'),
]

for title, desc, category, material_type in materials:
    StudyMaterial.objects.get_or_create(
        title=title,
        defaults={
            'description': desc,
            'category': category,
            'material_type': material_type,
            'is_active': True
        }
    )
print(f"  Created {StudyMaterial.objects.count()} study materials")

print("\n" + "=" * 50)
print("SUCCESS! All sample data loaded!")
print("=" * 50)
print(f"\nTotal: {Question.objects.count()} questions, {Exam.objects.count()} exams")
print("\nNow create admin with: python manage.py createsuperuser")
