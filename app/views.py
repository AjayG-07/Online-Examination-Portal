from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import Exam, Question, StudentResponse,ExamAssignment,StudentExamSession
from app.forms import ExamForm, QuestionForm, TeacherSignUpForm,ExamAssignmentForm,CustomUserCreationForm, CustomUserChangeForm,StudentProfileForm,TeacherProfileForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils import timezone
from datetime import timedelta
from .forms import CustomUserCreationForm, CustomAuthenticationForm,FeedbackForm
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Q
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.db.models import Max

# Role Check Helpers
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def is_teacher(user):
    return user.is_authenticated and user.role == 'teacher'

def is_admin_or_teacher(user):
    return is_admin(user) or is_teacher(user)


# Home View
def home_view(request):
    latest_exams = Exam.objects.order_by('-created_at')  # Adjust field if needed

    paginator = Paginator(latest_exams, 5)  # Show 5 exams per page
    page_number = request.GET.get('page')
    page_exams = paginator.get_page(page_number)
  
    return render(request, 'app/home.html', {'page_exams': page_exams})


# Authentication Views
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.role = 'student'  
            user.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'app/accounts/signup.html', {'form': form})


def admin_signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = True
            user.role = 'admin'
            user.save()
            messages.success(request, 'Admin Account created successfully!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'app/accounts/admin_signup.html', {'form': form})


def teacher_signup_view(request):
    if request.method == 'POST':
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'teacher'
            user.save()
            login(request, user)
            return redirect('teacher_dashboard')
    else:
        form = TeacherSignUpForm()
    return render(request, 'app/accounts/teacher_signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, f'Welcome {form.cleaned_data.get("username")}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = CustomAuthenticationForm(request)
    return render(request, 'app/accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')



# Admin Dashboard View
@user_passes_test(is_admin, login_url='home')
def admindashboard_view(request):
    return render(request, 'app/admindashboard.html')



@login_required
def student_list(request):
    students = CustomUser.objects.filter(role='student')
    template = 'app/teacher/student_list.html' if is_teacher(request.user) else 'app/admindashboard/student_list.html'
    return render(request, template, {'students': students})


def is_teacher(user):
    return user.is_authenticated and user.role == 'teacher'

@login_required
def student_add(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'student'
            user.save()
            # Redirect based on user role
            if is_teacher(request.user):
                return redirect('student_list')  
            else:
                return redirect('adminstudent_list') 
    else:
        form = CustomUserCreationForm(initial={'role': 'student'})

    # Select template based on user role
    if is_teacher(request.user):
        template = 'app/teacher/student_add.html'
    else:
        template = 'app/admindashboard/student_add.html'

    return render(request, template, {'form': form})


@login_required
def student_edit(request, pk):
    user = get_object_or_404(CustomUser, pk=pk, role='student')
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            if is_teacher(request.user):
                return redirect('student_list')  
            else:
                return redirect('adminstudent_list') 
    else:
        form = CustomUserChangeForm(instance=user)

    if is_teacher(request.user):
        template = 'app/teacher/student_edit.html'
    else:
        template = 'app/admindashboard/student_edit.html'

    return render(request, template, {'form': form})

@login_required
def student_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk, role='student')
    if request.method == 'POST':
        user.delete()
        return redirect('student_list' if is_teacher(request.user) else 'adminstudent_list')

    template = 'app/teacher/student_confirm_delete.html' if is_teacher(request.user) else 'app/admindashboard/student_confirm_delete.html'
    return render(request, template, {'user': user})


#teacher manage


@user_passes_test(is_admin, login_url='home')
def teacher_list(request):
    teachers = CustomUser.objects.filter(role='teacher')
    return render(request, 'app/admindashboard/teacher_list.html', {'teachers': teachers})

# Add a teacher
@user_passes_test(is_admin, login_url='home')
def teacher_add(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'teacher'
            user.save()
            return redirect('teacher_list')
    else:
        form = CustomUserCreationForm(initial={'role': 'teacher'})
    return render(request, 'app/admindashboard/teacher_add.html', {'form': form})

# Edit teacher
@user_passes_test(is_admin, login_url='home')
def teacher_edit(request, pk):
    user = get_object_or_404(CustomUser, pk=pk, role='teacher')
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('teacher_list')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'app/admindashboard/teacher_edit.html', {'form': form})

# Delete teacher
@user_passes_test(is_admin, login_url='home')
def teacher_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk, role='teacher')
    if request.method == 'POST':
        user.delete()
        return redirect('teacher_list')
    return render(request, 'app/admindashboard/teacher_confirm_delete.html', {'user': user})





@user_passes_test(is_admin_or_teacher)
def Exam_ListView(request):
    exams = Exam.objects.filter(created_by=request.user)
    return render(request, 'app/Exam/exam_list.html', {'exams': exams})


@user_passes_test(is_admin_or_teacher)
def Exam_CreateView(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            return redirect('exam_list')
    else:
        form = ExamForm()
    return render(request, 'app/Exam/exam_create.html', {'form': form})


@user_passes_test(is_admin_or_teacher)
def Edit_ExamView(request, pk):
    exam = get_object_or_404(Exam, pk=pk, created_by=request.user)
    if request.method == "POST":
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            return redirect('exam_list')
    else:
        form = ExamForm(instance=exam)
    return render(request, 'app/Exam/exam_edit.html', {'form': form})


@user_passes_test(is_admin_or_teacher)
def Exam_DeleteView(request, pk):
    exam = get_object_or_404(Exam, pk=pk, created_by=request.user)
    if request.method == 'POST':
        exam.delete()
        return redirect('exam_list')
    return render(request, 'app/Exam/exam_delete.html', {'exam': exam})




@user_passes_test(is_admin_or_teacher)
def question_listview(request, exam_id):
    exam_data = get_object_or_404(Exam, id=exam_id)
    questions = Question.objects.filter(exam=exam_data)
    return render(request, 'app/Question/question_list.html', {
        'exam_data': exam_data,
        'questions': questions
    })


@user_passes_test(is_admin_or_teacher)
def exam_question_dashboard_view(request):
    exams = Exam.objects.all()
    return render(request, 'app/Question/exam_question_dashboard.html', {'exams': exams})


@user_passes_test(is_admin_or_teacher)
def question_create(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            question.save()
            return redirect('question_list', exam_id=exam.id)
    else:
        form = QuestionForm()
    return render(request, 'app/Question/question_create.html', {'form': form, 'exam': exam})


@user_passes_test(is_admin_or_teacher)
def question_edit(request, exam_id, question_id):
    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id, exam=exam)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('question_list', exam_id=exam.id)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'app/Question/question_edit.html', {'form': form, 'exam': exam, 'question': question})


@user_passes_test(is_admin_or_teacher)
def question_delete(request, exam_id, question_id):
    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id, exam=exam)
    if request.method == 'POST':
        question.delete()
        return redirect('question_list', exam_id=exam.id)
    return render(request, 'app/Question/question_delete.html', {'exam': exam, 'question': question})





# Student Dashboard 


@login_required
def student_dashboard_view(request):
    exams = Exam.objects.all()
    query = request.GET.get('search')
    if query:
        exams = exams.filter(title__icontains=query)

    user = request.user

   
    latest_exam_ids = (
        StudentResponse.objects
        .filter(student=user)
        .values('exam_id')
        .annotate(latest_attempt=Max('id')) 
        .order_by('-latest_attempt')[:5]
    )
    latest_exams = Exam.objects.filter(id__in=[item['exam_id'] for item in latest_exam_ids])

    return render(request, 'app/student/student_dashboard.html', {
        'exams': exams,
        'user': user,
        'latest_exams': latest_exams,
    })


@login_required
def student_profile_view(request):
    user = request.user 

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('student_profile')  # this URL must be defined
    else:
        form = StudentProfileForm(instance=user)

    return render(request, 'app/student/student_profile.html', {'form': form})


# Show profile
@login_required
def profile_detail(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'app/student/profile_detail.html', {'user_profile': user})

# Edit profile
@login_required
def profile_edit(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # Permission Check
    if request.user != user and request.user.role != 'admin':
        return redirect('permission_denied')  # Optional

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile_detail', user_id=user.id)
    else:
        form = StudentProfileForm(instance=user)

    return render(request, 'app/student/profile_edit.html', {'form': form, 'user_profile': user})

# Delete profile
@login_required
def profile_delete(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.user != user and request.user.role != 'admin':
        return redirect('permission_denied')

    if request.method == 'POST':
        user.delete()
        return redirect('dashboard')  # or homepage
    return render(request, 'app/student/profile_delete_confirm.html', {'user_profile': user})


def exam_instructions_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    return render(request, 'app/student/exam_instructions.html', {'exam': exam})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Exam, StudentResponse

# ✅ Normalize helper
def normalize(value):
    return value.strip().lower() if value else ""

@login_required
def start_exam_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = list(exam.questions.all())

    for question in questions:
        question.options = [question.option1, question.option2, question.option3, question.option4]

    if request.method == 'POST':
        # ✅ Clear old responses if reattempt
        StudentResponse.objects.filter(student=request.user, exam=exam).delete()

        score = 0
        for question in questions:
            field_name = f"question_{question.id}"
            selected_option_raw = request.POST.get(field_name)

            if not selected_option_raw:
                selected_option = "Not Answered"
                is_correct = False
            else:
                selected_option = normalize(selected_option_raw)
                correct_option = normalize(getattr(question, question.correct_option, ""))  # Ensure lowercase + strip
                is_correct = selected_option == correct_option

            StudentResponse.objects.create(
                student=request.user,
                exam=exam,
                question=question,
                selected_option=selected_option_raw.strip() if selected_option_raw else "Not Answered",  # Store original text
                is_correct=is_correct,
                timestamp=timezone.now()
            )

            if is_correct:
                score += question.marks

        max_score = sum(q.marks for q in questions)
        percentage = (score / max_score) * 100 if max_score > 0 else 0
        passed = score >= exam.passing_marks

        if passed:
            messages.success(request, f"✅ Exam submitted! You passed with {score}/{max_score} marks ({percentage:.2f}%).")
        else:
            messages.warning(request, f"❌ Exam submitted! You failed with {score}/{max_score} marks ({percentage:.2f}%).")

        return redirect('student_result')

    end_time = timezone.now() + timedelta(minutes=exam.duration)

    return render(request, 'app/student/start_exam.html', {
        'exam': exam,
        'questions': questions,
        'end_time': end_time
    })


@login_required
def student_result_view(request):
    latest_response = StudentResponse.objects.filter(student=request.user).order_by('-id').first()

    if not latest_response:
        return render(request, 'app/student/student_result.html', {'exam_result': None})

    latest_exam = latest_response.exam
    responses = StudentResponse.objects.filter(student=request.user, exam=latest_exam).select_related('question')

    correct_score = 0
    max_score = 0
    response_list = []

    for res in responses:
        question = res.question
        res.options = [question.option1, question.option2, question.option3, question.option4]
        res.correct_option_value = getattr(question, question.correct_option)

        max_score += question.marks
        if res.is_correct:
            correct_score += question.marks

        response_list.append(res)

    percentage = round((correct_score / max_score) * 100, 2) if max_score > 0 else 0
    passed = correct_score >= latest_exam.passing_marks

    exam_result = {
        'exam': latest_exam,
        'responses': response_list,
        'correct_answers': correct_score,
        'total_questions': max_score,
        'percentage': percentage,
        'status': "Pass" if passed else "Fail",
        'grade': get_grade(percentage)
    }

    return render(request, 'app/student/student_result.html', {'exam_result': exam_result})


def get_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "F"


# Teacher Dashboard

@login_required
@user_passes_test(is_teacher, login_url='home')
def teacher_profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('teacher_profile')  # make sure this URL name exists
    else:
        form = TeacherProfileForm(instance=user)
    return render(request, 'app/teacher/teacher_profile.html', {'form': form})

@login_required
@user_passes_test(is_teacher, login_url='home')
def teacher_dashboard(request):
    teacher = request.user
    exams = Exam.objects.filter(created_by=teacher)
    total_exams = exams.count()

    responses = StudentResponse.objects.filter(exam__in=exams).select_related('student', 'exam')

    student_exam_map = {}
    for response in responses:
        student = response.student
        if student not in student_exam_map:
            student_exam_map[student] = []
        student_exam_map[student].append(response.exam)

    student_count = len(student_exam_map.keys())  # distinct students

    context = {
        'teacher': teacher,
        'exams': exams,
        'exam_count': total_exams,
        'student_count': student_count,
        'student_exam_map': student_exam_map,
    }
    return render(request, 'app/teacher/teacher_dashboard.html', context)


@user_passes_test(is_teacher)
def student_list_view(request):
    students = CustomUser.objects.filter(role='student')
    exam = Exam.objects.filter(created_by=request.user).last()

    return render(request, 'app/teacher/student_list.html', {
        'students': students,
        'exam': exam
    })

def teacher_student_edit(request, pk):
    student = get_object_or_404(CustomUser, pk=pk, role='student')

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('teacher_student_list')  # make sure this URL name exists
    else:
        form = CustomUserChangeForm(instance=student)

    return render(request, 'app/teacher/teacherstudent_edit.html', {'form': form})

def teacher_student_delete(request, pk):
    student = get_object_or_404(CustomUser, pk=pk, role='student')

    if request.method == 'POST':
        student.delete()
        return redirect('teacher_student_list')

    return render(request, 'app/teacher/teacherstudent_confirm_delete.html', {'user': student})

@user_passes_test(is_teacher)
def assign_exam_to_student(request, exam_id, student_id=None):
    exam = get_object_or_404(Exam, id=exam_id)
    student = get_object_or_404(CustomUser, id=student_id, role='student') if student_id else None

    if request.method == 'POST':
        form = ExamAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.exam = exam
            if student:
                assignment.student = student
            assignment.save()
            messages.success(request, 'Exam assigned successfully!')
            return redirect('student_list')  
    else:
        form = ExamAssignmentForm(initial={'exam': exam, 'student': student})

    return render(request, 'app/teacher/assign_exam.html', {
        'form': form,
        'exam': exam,
        'student': student
    })




@user_passes_test(is_teacher)
def exam_progress_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    total_questions = exam.questions.count()

    # Get all students assigned to this exam
    assigned_students = ExamAssignment.objects.filter(exam=exam).select_related('student')

    progress_data = []

    for assignment in assigned_students:
        student = assignment.student
        answered_count = StudentResponse.objects.filter(exam=exam, student=student).count()

        status = "Not Started"
        if answered_count > 0:
            status = "In Progress"
        if answered_count == total_questions:
            status = "Completed"

        progress_data.append({
            'student': student,
            'answered': answered_count,
            'total': total_questions,
            'status': status,
        })

    return render(request, 'app/teacher/exam_progress.html', {
        'exam': exam,
        'progress_data': progress_data
    })




@user_passes_test(is_teacher)
def exam_analytics(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    # Fetch all student responses for the given exam
    responses = StudentResponse.objects.filter(exam=exam)

    # Total unique students who attempted the exam
    total_students = responses.values('student').distinct().count()

    # Annotate each student’s score
    student_scores = (
        responses
        .values('student', 'student__username')
        .annotate(
            total_correct=Count('id', filter=Q(is_correct=True)),
            adjusted_total=Coalesce(Sum('adjusted_marks'), 0),
        )
    )

    max_marks = exam.questions.count() * exam.marks_per_question

    for score in student_scores:
        score['total_marks'] = score['total_correct'] * exam.marks_per_question
        score['percentage'] = round((score['total_marks'] / max_marks) * 100, 2) if max_marks > 0 else 0

    # Average score for the exam
    avg_score = (
        sum(score['total_marks'] for score in student_scores) / total_students
        if total_students > 0 else 0
    )

    # Per-question analytics
    question_stats = exam.questions.annotate(
        correct_count=Count('studentresponse', filter=Q(studentresponse__is_correct=True)),
        total_attempts=Count('studentresponse')
    )

    context = {
        'exam': exam,
        'total_students': total_students,
        'avg_score': round(avg_score, 2),
        'student_scores': student_scores,
        'question_stats': question_stats,
        'max_marks': max_marks,
    }

    return render(request, 'app/teacher/exam_analytics.html', context)





def contact_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('contact')  
    else:
        form = FeedbackForm()
    return render(request, 'app/contact.html', {'form': form})
