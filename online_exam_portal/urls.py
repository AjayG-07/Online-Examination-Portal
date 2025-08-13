"""
URL configuration for online_exam_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),

    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('admin_signup/', views.admin_signup_view, name='admin_signup'),
    path('teacher_signup/', views.teacher_signup_view, name='teacher_signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    #admin dashboard
    path('admindashboard/', views.admindashboard_view, name='admindashboard'),
    path('students/', views.student_list, name='adminstudent_list'),
    path('students/add/', views.student_add, name='student_add'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    # Teacher management
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/add/', views.teacher_add, name='teacher_add'),
    path('teachers/edit/<int:pk>/', views.teacher_edit, name='teacher_edit'),
    path('teachers/delete/<int:pk>/', views.teacher_delete, name='teacher_delete'),

    # Exam Form
    path('examlist/', views.Exam_ListView, name='exam_list'),
    path('examcreate/', views.Exam_CreateView, name='exam_create'),
    path('examedit/<int:pk>/', views.Edit_ExamView, name='exam_edit'),
    path('examdel/<int:pk>/', views.Exam_DeleteView, name='exam_delete'),

    # Question
    path('exams/<int:exam_id>/questions/', views.question_listview, name='question_list'),
    path('exam_list_dashboard/', views.exam_question_dashboard_view, name='exam_dashboard'),
    path('exams/<int:exam_id>/questions/create/', views.question_create, name='question_create'),
    path('exams/<int:exam_id>/questions/<int:question_id>/edit/', views.question_edit, name='question_edit'),
    path('exams/<int:exam_id>/questions/<int:question_id>/delete/', views.question_delete, name='question_delete'),

    # Student
    path('studashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('student/profile/', views.student_profile_view, name='student_profile'),
    path('profile/<int:user_id>/', views.profile_detail, name='profile_detail'),
    path('profile/<int:user_id>/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<int:user_id>/delete/', views.profile_delete, name='profile_delete'),

    path('exam/<int:exam_id>/instructions/', views.exam_instructions_view, name='exam_instructions'),
    path('exam/<int:exam_id>/start/', views.start_exam_view, name='start_exam'),
    path('myresults/', views.student_result_view, name='student_result'),
   


    # Teacher
    path('teacher/profile/', views.teacher_profile_view, name='teacher_profile'),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/teacherexams/', views.Exam_ListView, name='teacherexam_list'),
    path('teacher/teacherexams/create/', views.Exam_CreateView, name='teacherexam_create'),
    path('teacher/teacherexams/edit/<int:pk>/', views.Edit_ExamView, name='teacherexam_edit'),
    path('teacher/teacherexams/delete/<int:pk>/', views.Exam_DeleteView, name='teacherexam_delete'),
    path('teacher/students/', views.student_list_view, name='student_list'),
    path('teacher/students/<int:pk>/edit/', views.teacher_student_edit, name='teacher_student_edit'),
    path('teacher/students/<int:pk>/delete/', views.teacher_student_delete, name='teacher_student_delete'),

    path('teacher/assign_exam/<int:exam_id>/<int:student_id>/', views.assign_exam_to_student, name='assign_exam_to_student'),
    path('teacher/assign_exam/<int:exam_id>/', views.assign_exam_to_student, name='assign_exam_to_student'),
    path('teacher/exam-progress/<int:exam_id>/', views.exam_progress_view, name='exam_progress'),
    path('teacher/exam/<int:exam_id>/analytics/', views.exam_analytics, name='exam_analytics'),

    path('contact/', views.contact_view, name='contact'),






    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)