from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ScheduleEntry, Grade, Subject, Classroom, Teacher, User
from django.utils import timezone
from datetime import date

def get_user_role(user):
    if user.is_superuser or user.role == 'admin':
        return 'admin'
    return user.role

@login_required
def dashboard(request):
    role = get_user_role(request.user)
    return render(request, 'core/dashboard.html', {'role': role})

@login_required
def schedule(request):
    role = get_user_role(request.user)
    weekday = int(request.GET.get('weekday', timezone.now().weekday()))
    weekdays = [
        (0, 'Пн'),
        (1, 'Вт'),
        (2, 'Ср'),
        (3, 'Чт'),
        (4, 'Пт'),
        (5, 'Сб'),
    ]
    if role == 'student':
        # student's classroom
        classroom = getattr(request.user, 'classroom', None)
        entries = ScheduleEntry.objects.filter(classroom=classroom, weekday=weekday)
    elif role == 'teacher':
        teacher = Teacher.objects.filter(user=request.user).first()
        entries = ScheduleEntry.objects.filter(teacher=teacher, weekday=weekday)
    else:
        entries = ScheduleEntry.objects.filter(weekday=weekday)
    return render(request, 'core/schedule.html', {'entries': entries, 'weekday': weekday, 'weekdays': weekdays})

@login_required
def grades(request):
    role = get_user_role(request.user)
    if role == 'teacher':
        teacher = Teacher.objects.filter(user=request.user).first()
        classroom_id = request.GET.get('classroom')
        subject_id = request.GET.get('subject')
        classrooms = teacher.classrooms.all()
        subjects = teacher.subjects.all()
        grades = None
        students = None
        if classroom_id and subject_id:
            students = User.objects.filter(classroom__id=classroom_id, role='student')
            grades = Grade.objects.filter(teacher=teacher, subject_id=subject_id, student__in=students)
        return render(request, 'core/grades_teacher.html', {'classrooms': classrooms, 'subjects': subjects, 'grades': grades, 'students': students})
    elif role == 'student':
        subject_id = request.GET.get('subject')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        grades = Grade.objects.filter(student=request.user)
        if subject_id:
            grades = grades.filter(subject_id=subject_id)
        if start_date:
            grades = grades.filter(date__gte=start_date)
        if end_date:
            grades = grades.filter(date__lte=end_date)
        # Средний балл
        avg = None
        grade_values = [int(g.grade) for g in grades if g.grade.isdigit()]
        if grade_values:
            avg = sum(grade_values) / len(grade_values)
        return render(request, 'core/grades_student.html', {'grades': grades, 'avg': avg})
    else:
        # Админ видит всё
        grades = Grade.objects.all()
        return render(request, 'core/grades_admin.html', {'grades': grades})

@login_required
def profile(request):
    return render(request, 'core/profile.html', {'user': request.user})
