from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ScheduleEntry, Grade, Subject, Classroom, Teacher, User, Homework
from django.utils import timezone
from datetime import date
from django.contrib.auth import authenticate, login
from django.contrib import messages

def get_user_role(user):
    if user.is_superuser or user.role == 'admin':
        return 'admin'
    return user.role

@login_required
def dashboard(request):
    role = get_user_role(request.user)
    today = timezone.localdate()
    weekdays = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
    ]
    context = {'role': role, 'today': today, 'weekdays': weekdays}
    if role == 'student':
        # Актуальное расписание и оценки на сегодня
        classroom = getattr(request.user, 'classroom', None)
        schedule_today = ScheduleEntry.objects.filter(classroom=classroom, weekday=today.weekday())
        grades_today = Grade.objects.filter(student=request.user, date=today)
        homeworks_today = Homework.objects.filter(classroom=classroom, date=today)
        context.update({
            'schedule_today': schedule_today,
            'grades_today': grades_today,
            'homeworks_today': homeworks_today,
        })
    elif role == 'teacher':
        teacher = Teacher.objects.filter(user=request.user).first()
        schedule_today = ScheduleEntry.objects.filter(teacher=teacher, weekday=today.weekday())
        context.update({'schedule_today': schedule_today})
    elif role == 'admin':
        # Для админа можно добавить статистику или быстрые ссылки
        pass
    return render(request, 'core/dashboard.html', context)

@login_required
def schedule(request):
    role = get_user_role(request.user)
    weekday = int(request.GET.get('weekday', timezone.now().weekday()))
    weekdays = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
    ]
    homeworks = None
    if role == 'student':
        classroom = getattr(request.user, 'classroom', None)
        entries = ScheduleEntry.objects.filter(classroom=classroom, weekday=weekday)
        homeworks = Homework.objects.filter(classroom=classroom, date=timezone.localdate())
    elif role == 'teacher':
        teacher = Teacher.objects.filter(user=request.user).first()
        entries = ScheduleEntry.objects.filter(teacher=teacher, weekday=weekday)
        homeworks = Homework.objects.filter(teacher=teacher, date=timezone.localdate())
    else:
        entries = ScheduleEntry.objects.filter(weekday=weekday)
    return render(request, 'core/schedule.html', {'entries': entries, 'weekday': weekday, 'weekdays': weekdays, 'homeworks': homeworks})

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
        avg = None
        grade_values = [int(g.grade) for g in grades if g.grade.isdigit()]
        if grade_values:
            avg = sum(grade_values) / len(grade_values)
        # Оценки за сегодня
        grades_today = grades.filter(date=timezone.localdate())
        return render(request, 'core/grades_student.html', {'grades': grades, 'avg': avg, 'grades_today': grades_today})
    else:
        grades = Grade.objects.all()
        return render(request, 'core/grades_admin.html', {'grades': grades})

@login_required
def profile(request):
    return render(request, 'core/profile.html', {'user': request.user})

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/accounts/login/')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and (user.is_superuser or user.role == 'admin'):
            login(request, user)
            return redirect('/admin/')
        else:
            messages.error(request, 'Неверный логин или пароль, или у вас нет прав администратора.')
    return render(request, 'core/admin_login.html')
