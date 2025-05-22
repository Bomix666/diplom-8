from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Админ'),
        ('teacher', 'Учитель'),
        ('student', 'Ученик'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    classroom = models.ForeignKey('Classroom', on_delete=models.SET_NULL, null=True, blank=True)
    # Optionally: phone, parent_email, etc.

class Classroom(models.Model):
    name = models.CharField(max_length=10, unique=True)  # e.g. "10Б"

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#888888")  # For frontend color coding

    def __str__(self):
        return self.name

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    subjects = models.ManyToManyField(Subject)
    classrooms = models.ManyToManyField(Classroom, blank=True)  # Which classes the teacher teaches

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class ScheduleEntry(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, verbose_name='Класс')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='Учитель')
    weekday = models.IntegerField(choices=[(i, d) for i, d in enumerate(['Пн','Вт','Ср','Чт','Пт','Сб'])], verbose_name='День недели')
    lesson_number = models.PositiveIntegerField(verbose_name='Номер урока')  # 1, 2, 3...
    start_time = models.TimeField(verbose_name='Начало')
    end_time = models.TimeField(verbose_name='Конец')

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'
        unique_together = ("classroom", "weekday", "lesson_number")
        ordering = ["weekday", "lesson_number"]

    def __str__(self):
        return f"{self.classroom} {self.subject} {self.get_weekday_display()} {self.lesson_number}"

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, verbose_name='Ученик')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    date = models.DateField(verbose_name='Дата')
    grade = models.CharField(max_length=5, verbose_name='Оценка')  # e.g. "5", "4+", "н"
    comment = models.CharField(max_length=100, blank=True, verbose_name='Комментарий')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='Учитель')

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'

    def __str__(self):
        return f"{self.student}: {self.subject} {self.grade} ({self.date})"

class Homework(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, verbose_name='Класс')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    date = models.DateField(verbose_name='Дата')
    text = models.TextField(verbose_name='Домашнее задание')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='Учитель')

    class Meta:
        verbose_name = 'Домашнее задание'
        verbose_name_plural = 'Домашние задания'
        ordering = ['-date']

    def __str__(self):
        return f"{self.classroom} {self.subject} {self.date}"
