from django.shortcuts import render, redirect, get_object_or_404
from core.models import Student, Enrollment, PastOrPlanned

def student_select(request):
    students = Student.objects.all().order_by("name")
    return render(request, "studentplan/selectstudent.html", {"students": students})


def set_student_session(request, pk):
    student = get_object_or_404(Student, pk=pk)
    request.session['student_id'] = student.id
    return redirect("schedule")


def student_scheduler(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect("select_student") # force them to pick one first
    student = get_object_or_404(Student, pk=student_id)
    return render(request, 'studentplan/scheduler.html', {'student': student})


def student_progress(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect("select_student")

    student = get_object_or_404(Student, pk=student_id)

    # Completed work: count enrollments and sum course hours
    enrollments = (Enrollment.objects
                   .filter(student=student)
                   .select_related("section__course", "section__semester"))

    completed = []
    total_credits = 0.0
    for e in enrollments:
        c = e.section.course
        sem = e.section.semester.semester_id
        hours = c.min_hours or 0.0
        total_credits += hours
        completed.append({
            'course_id': f"{c.department.department_id} {c.course_num}",
            'title': c.title,
            'hours': hours,
            'semester': sem
        })

    # Planned items (optional: across all semesters)
    planned = (
        PastOrPlanned.objects
        .filter(student=student)
        .select_related("course", "semester")
        .order_by("semester__semester_id", "course__department__department_id", "course__course_num")
    )

    context = {
        'student': student,
        'completed': completed,
        'total_credits': total_credits,
        'planned': planned,
        'planned_count': planned.count(),
        'credits_completed': len(completed),
    }

    return render(request, 'studentplan/progress.html', context)
