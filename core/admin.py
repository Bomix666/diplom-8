from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Classroom, Subject, Teacher, ScheduleEntry, Grade

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'role', 'email')
    list_filter = ('role',)
    search_fields = ('username', 'first_name', 'last_name', 'email')

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    filter_horizontal = ('subjects', 'classrooms')

@admin.register(ScheduleEntry)
class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ('classroom', 'subject', 'teacher', 'weekday', 'lesson_number', 'start_time', 'end_time')
    list_filter = ('classroom', 'subject', 'teacher', 'weekday')
    search_fields = ('classroom__name', 'subject__name', 'teacher__user__username')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'grade', 'teacher', 'comment')
    list_filter = ('subject', 'teacher', 'date')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'subject__name', 'teacher__user__username')
