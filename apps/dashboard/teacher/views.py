from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from core.decorators import role_required
from core.models import Classroom, ClassroomSubject, TaskProgress, User, SubjectProgress
from .forms import ClassroomCreateForm, ClassroomStudentsAttachForm, ClassroomSubjectAssignForm, ClassroomUpdateForm


@login_required
@role_required('teacher')
def dashboard_view(request):
    classrooms = _teacher_classrooms(request.user)
    classroom_ids = classrooms.values_list('id', flat=True)
    student_ids = User.objects.filter(classrooms__teacher=request.user).values_list('id', flat=True).distinct()

    classroom_count = classrooms.count()
    student_count = student_ids.count()
    subject_count = ClassroomSubject.objects.filter(
        classroom_id__in=classroom_ids,
        is_active=True,
    ).values('subject_id').distinct().count()

    progress_summary = TaskProgress.objects.filter(
        learner_id__in=student_ids,
        task__level__module__subject__classroom_subjects__classroom_id__in=classroom_ids,
        task__level__module__subject__classroom_subjects__is_active=True,
    ).aggregate(
        total=Count('id', distinct=True),
        completed=Count('id', filter=Q(status=TaskProgress.Status.COMPLETED), distinct=True),
    )

    total_progress = progress_summary['total'] or 0
    completed_progress = progress_summary['completed'] or 0
    average_progress = round((completed_progress / total_progress) * 100) if total_progress else 0

    recent_classrooms = classrooms.annotate(
        students_count=Count('students', distinct=True),
        subjects_count=Count('classroom_subjects', filter=Q(classroom_subjects__is_active=True), distinct=True),
    ).order_by('-created_at')[:5]

    return render(request, 'app/dashboard/teacher/page.html', {
        'page_title': 'Панель учителя',
        'classroom_count': classroom_count,
        'student_count': student_count,
        'subject_count': subject_count,
        'average_progress': average_progress,
        'recent_classrooms': recent_classrooms,
    })


@login_required
@role_required('teacher')
def classrooms_view(request):
    classrooms = _teacher_classrooms(request.user).prefetch_related(
        'students',
        Prefetch(
            'classroom_subjects',
            queryset=ClassroomSubject.objects.select_related('subject').filter(is_active=True),
            to_attr='active_subjects',
        ),
    ).annotate(
        students_count=Count('students', distinct=True),
        subjects_count=Count('classroom_subjects', filter=Q(classroom_subjects__is_active=True), distinct=True),
    )

    return render(request, 'app/dashboard/teacher/classrooms/page.html', {
        'page_title': 'Классы',
        'classrooms': classrooms,
        'classroom_form': ClassroomCreateForm(),
        'subject_form': ClassroomSubjectAssignForm(teacher=request.user),
        'students_form': ClassroomStudentsAttachForm(teacher=request.user),
    })


@login_required
@role_required('teacher')
def students_view(request):
    classrooms = _teacher_classrooms(request.user)
    selected_classroom_id = request.GET.get('classroom')

    students = User.objects.filter(
        classrooms__teacher=request.user,
        role=User.Role.LEARNER,
    ).distinct().order_by('first_name', 'last_name', 'username')

    selected_classroom = None
    if selected_classroom_id:
        selected_classroom = get_object_or_404(classrooms, id=selected_classroom_id)
        students = students.filter(classrooms=selected_classroom)

    students = students.annotate(
        classrooms_count=Count('classrooms', filter=Q(classrooms__teacher=request.user), distinct=True),
    ).prefetch_related('classrooms')

    return render(request, 'app/dashboard/teacher/students/page.html', {
        'page_title': 'Ученики',
        'students': students,
        'classrooms': classrooms,
        'selected_classroom': selected_classroom,
    })


@login_required
@role_required('teacher')
def student_progress_view(request, student_id):
    student = get_object_or_404(
        User,
        id=student_id,
        role=User.Role.LEARNER,
        classrooms__teacher=request.user,
    )

    classrooms = Classroom.objects.filter(
        teacher=request.user,
        students=student,
    ).prefetch_related(
        'classroom_subjects__subject',
    )

    subject_progresses = SubjectProgress.objects.filter(
        learner=student,
        subject__classroom_subjects__classroom__in=classrooms,
    ).select_related(
        'subject',
    ).distinct()

    task_progresses = TaskProgress.objects.filter(
        learner=student,
        task__level__module__subject__classroom_subjects__classroom__in=classrooms,
    ).select_related(
        'task',
        'task__level',
        'task__level__module',
        'task__level__module__subject',
    ).distinct()

    context = {
        'student': student,
        'classrooms': classrooms,
        'subject_progresses': subject_progresses,
        'task_progresses': task_progresses,
    }

    return render(request, 'app/dashboard/teacher/students/student_progress.html', context)


@login_required
@role_required('teacher')
@require_POST
def classroom_create_view(request):
    form = ClassroomCreateForm(request.POST)

    if form.is_valid():
        classroom = form.save(commit=False)
        classroom.teacher = request.user
        classroom.save()
        messages.success(request, 'Класс успешно создан.')
    else:
        messages.error(request, 'Проверьте название класса.')

    return redirect('teacher:classrooms')


@login_required
@role_required('teacher')
def classroom_update_view(request, classroom_id):
    classroom = get_object_or_404(_teacher_classrooms(request.user), id=classroom_id)

    if request.method == 'POST':
        form = ClassroomUpdateForm(request.POST, instance=classroom)

        if form.is_valid():
            form.save()
            messages.success(request, 'Класс успешно обновлён.')
            return redirect('teacher:classrooms')

        messages.error(request, 'Проверьте данные класса.')
    else:
        form = ClassroomUpdateForm(instance=classroom)

    return render(request, 'app/dashboard/teacher/classrooms/edit.html', {
        'page_title': 'Редактировать класс',
        'classroom': classroom,
        'form': form,
    })


@login_required
@role_required('teacher')
@require_POST
def classroom_delete_view(request, classroom_id):
    classroom = get_object_or_404(_teacher_classrooms(request.user), id=classroom_id)
    classroom.delete()

    messages.success(request, 'Класс удалён.')
    return redirect('teacher:classrooms')


@login_required
@role_required('teacher')
@require_POST
def classroom_subject_assign_view(request):
    form = ClassroomSubjectAssignForm(request.POST, teacher=request.user)

    if form.is_valid():
        classroom = form.cleaned_data['classroom']
        subject = form.cleaned_data['subject']
        classroom_subject, created = ClassroomSubject.objects.get_or_create(
            classroom=classroom,
            subject=subject,
            defaults={
                'assigned_by': request.user,
                'is_active': True,
            },
        )

        if not created and not classroom_subject.is_active:
            classroom_subject.is_active = True
            classroom_subject.assigned_by = request.user
            classroom_subject.save(update_fields=['is_active', 'assigned_by'])

        messages.success(request, 'Предмет закреплён за классом.')
    else:
        messages.error(request, 'Не удалось закрепить предмет.')

    return redirect('teacher:classrooms')


@login_required
@role_required('teacher')
def classroom_students_attach_view(request):
    search_query = request.GET.get('q', '').strip()

    if request.method == 'POST':
        form = ClassroomStudentsAttachForm(
            request.POST,
            teacher=request.user,
            search_query=search_query,
        )

        if form.is_valid():
            classroom = form.cleaned_data['classroom']
            students = form.cleaned_data['students']

            classroom.students.add(*students)

            messages.success(request, 'Ученики успешно добавлены в класс.')
            return redirect('teacher:classrooms')

        messages.error(request, 'Проверьте выбранные данные.')
    else:
        form = ClassroomStudentsAttachForm(
            teacher=request.user,
            search_query=search_query,
        )

    return render(request, 'app/dashboard/teacher/classrooms/attach_students.html', {
        'page_title': 'Добавить учеников',
        'form': form,
        'search_query': search_query,
        'students': form.fields['students'].queryset,
    })


@login_required
@role_required('teacher')
@require_POST
def classroom_student_remove_view(request, classroom_id, student_id):
    classroom = get_object_or_404(_teacher_classrooms(request.user), id=classroom_id)
    student = get_object_or_404(User, id=student_id, role=User.Role.LEARNER)
    classroom.students.remove(student)
    messages.success(request, 'Ученик удалён из класса.')

    return redirect(request.POST.get('next') or 'teacher:students')


def _teacher_classrooms(teacher):
    return Classroom.objects.filter(teacher=teacher)
