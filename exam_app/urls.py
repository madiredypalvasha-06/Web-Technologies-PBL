from django.urls import path
from . import views, api_views

urlpatterns = [
    # API endpoints
    path('api/login/', api_views.api_login, name='api_login'),
    path('api/logout/', api_views.api_logout, name='api_logout'),
    path('api/register/', api_views.api_register, name='api_register'),
    path('api/user/', api_views.api_user, name='api_user'),
    path('api/exams/', api_views.api_exams, name='api_exams'),
    path('api/results/', api_views.api_results, name='api_results'),
    path('api/practice/tests/', api_views.api_practice_tests, name='api_practice_tests'),
    path('api/worksheets/', api_views.api_worksheets, name='api_worksheets'),
    path('api/materials/', api_views.api_materials, name='api_materials'),
    path('api/categories/', api_views.api_categories, name='api_categories'),
    path('api/progress/', api_views.api_progress, name='api_progress'),
    path('api/bookmarks/', api_views.api_bookmarks, name='api_bookmarks'),
    path('api/bookmarks/toggle/', api_views.api_toggle_bookmark, name='api_toggle_bookmark'),
    
    # Admin API endpoints
    path('api/admin/dashboard/', api_views.api_admin_dashboard, name='api_admin_dashboard'),
    path('api/admin/students/', api_views.api_admin_students, name='api_admin_students'),
    path('api/admin/students/<int:student_id>/', api_views.api_admin_student_update, name='api_admin_student_update'),
    path('api/admin/exams/', api_views.api_admin_exams, name='api_admin_exams'),
    path('api/admin/exams/create/', api_views.api_admin_exam_create, name='api_admin_exam_create'),
    path('api/admin/exams/<int:exam_id>/', api_views.api_admin_exam_update, name='api_admin_exam_update'),
    path('api/admin/questions/', api_views.api_admin_questions, name='api_admin_questions'),
    path('api/admin/questions/create/', api_views.api_admin_question_create, name='api_admin_question_create'),
    path('api/admin/questions/<int:question_id>/', api_views.api_admin_question_update, name='api_admin_question_update'),
    
    # Exam API endpoints
    path('api/exam/<int:exam_id>/', api_views.api_exam_detail, name='api_exam_detail'),
    path('api/exam/<int:exam_id>/start/', api_views.api_exam_start, name='api_exam_start'),
    path('api/exam/<int:exam_id>/take/', api_views.api_exam_take, name='api_exam_take'),
    path('api/exam/<int:exam_id>/submit/', api_views.api_exam_submit, name='api_exam_submit'),
    path('api/exam/<int:exam_id>/violation/', api_views.api_exam_violation, name='api_exam_violation'),
    
    # Template views
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/exam/<int:exam_id>/', views.start_exam, name='start_exam'),
    path('student/results/', views.view_my_results, name='my_results'),
    
    path('practice/', views.practice_hub, name='practice_hub'),
    path('practice/tests/', views.practice_tests, name='practice_tests'),
    path('practice/test/<int:test_id>/', views.start_practice_test, name='start_practice_test'),
    path('practice/test/submit/', views.submit_practice_test, name='submit_practice_test'),
    path('practice/test/result/<int:session_id>/', views.practice_result, name='practice_result'),
    path('practice/worksheets/', views.worksheets, name='worksheets'),
    path('practice/materials/', views.study_materials, name='study_materials'),
    path('practice/bookmarks/', views.my_bookmarks, name='my_bookmarks'),
    path('practice/bookmarks/toggle/', views.toggle_bookmark, name='toggle_bookmark'),
    path('practice/progress/', views.my_progress, name='my_progress'),
    
    path('control/', views.admin_dashboard, name='admin_dashboard'),
    path('control/category/add/', views.api_add_category, name='api_add_category'),
    path('control/questions/add/', views.api_add_question, name='api_add_question'),
    path('control/questions/delete/<int:question_id>/', views.api_delete_question, name='delete_question'),
    path('control/exams/add/', views.api_add_exam, name='api_add_exam'),
    path('control/exams/delete/<int:exam_id>/', views.api_delete_exam, name='delete_exam'),
    path('control/exams/toggle/<int:exam_id>/', views.api_toggle_exam, name='toggle_exam'),
    path('control/analytics/', views.api_get_analytics, name='api_analytics'),
    path('control/worksheet/add/', views.api_add_worksheet, name='api_add_worksheet'),
    path('control/material/add/', views.api_add_study_material, name='api_add_material'),
    path('control/practice-test/add/', views.api_add_practice_test, name='api_add_practice_test'),
]
