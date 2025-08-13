from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)


    def __str__(self):
        return self.username


class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField() 
    date = models.DateTimeField()
    duration = models.IntegerField(help_text='Duration in minutes')
    marks_per_question = models.IntegerField(default=5)
    passing_marks = models.IntegerField(default=22)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exams', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)

    OPTION_CHOICES = (
        ('option1', 'Option 1'),
        ('option2', 'Option 2'),
        ('option3', 'Option 3'),
        ('option4', 'Option 4'),
    )
    correct_option = models.CharField(max_length=20, choices=OPTION_CHOICES)
    marks = models.IntegerField(default=5)

    
    def clean(self):
        super().clean()
        options = [self.option1, self.option2, self.option3, self.option4]
        correct_option_value = getattr(self, self.correct_option)
        if correct_option_value not in options:
            raise ValidationError({'correct_option': 'Correct option must match one of the provided options.'})

    def __str__(self):
        return f"{self.exam.title} - {self.question_text[:50]}"


class StudentResponse(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    manually_graded = models.BooleanField(default=False)
    teacher_comment = models.TextField(blank=True, null=True)
    adjusted_marks = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'exam', 'question')

    def __str__(self):
        return f"{self.student.username} - {self.exam.title} - Q{self.question.id}"


class ExamAssignment(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('exam', 'student')

    def __str__(self):
        return f"{self.exam.title} assigned to {self.student.username}"




class StudentExamSession(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'exam')

    def time_elapsed(self):
        return timezone.now() - self.start_time

    def time_remaining(self):
        return max(0, self.exam.duration * 60 - int(self.time_elapsed().total_seconds()))


class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
