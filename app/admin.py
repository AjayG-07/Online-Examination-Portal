from django.contrib import admin
from app.models import Exam, Question, StudentResponse, CustomUser
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),  # show role in edit form
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),  # show role in create form
    )

admin.site.register(CustomUser, CustomUserAdmin)


class ExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'date', 'duration')

admin.site.register(Exam, ExamAdmin)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam', 'question_text', 'option1', 'option2', 'option3', 'option4', 'correct_option')

admin.site.register(Question, QuestionAdmin)


admin.site.register(StudentResponse)
