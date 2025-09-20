from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import Student, Enrollment, PastOrPlanned, Semester, Course
# Create your views here.


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
        return redirect("select_student")
    student = get_object_or_404(Student, pk=student_id)

    selected_sem = request.GET.get("sem") or request.POST.get("sem") or ""

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add":
            sem_id = request.POST.get("sem")
            crs_id = request.POST.get("course_id")
            if not (sem_id and crs_id):
                messages.error(request, "Pick a semester and a course to add.")
            else:
                try:
                    sem, _ = Semester.objects.get_or_create(semester_id=sem_id)
                    course = Course.objects.get(course_id=crs_id)
                    obj, created = PastOrPlanned.objects.get_or_create(
                        student=student, course=course, semester=sem
                    )
                    if created:
                        messages.success(request, f"Added {course.title} to {sem.semester_id}.")
                    else:
                        messages.info(request, f"{course.title} was already planned for {sem.semester_id}.")
                    selected_sem = sem.semester_id
                except Course.DoesNotExist:
                    messages.error(request, "Course not found.")
        elif action == "remove":
            pp_id = request.POST.get("pp_id")
            removed = PastOrPlanned.objects.filter(id=pp_id, student=student).delete()[0]
            if removed:
                messages.success(request, "Removed planned course.")
            else:
                messages.info(request, "Nothing to remove.")

    semesters = Semester.objects.order_by("semester_id")  # for the dropdown

    planned_qs = (PastOrPlanned.objects
                  .filter(student=student)
                  .select_related("course", "course__department", "semester"))
    if selected_sem:
        planned_qs = planned_qs.filter(semester__semester_id=selected_sem)

    planned = planned_qs.order_by("semester__semester_id",
                                  "course__department__department_id",
                                  "course__course_num")

    available_courses = []
    if selected_sem:
        already = set(planned_qs.values_list("course__course_id", flat=True))
        available_courses = (Course.objects
                             .exclude(course_id__in=already)
                             .select_related("department")
                             .order_by("department__department_id", "course_num")[:300])

    context = {
        "student": student,
        "semesters": semesters,
        "selected_sem": selected_sem,
        "planned": planned,
        "available_courses": available_courses,
    }
    return render(request, "studentplan/scheduler.html", context)

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
        sem = e.section.semester.name
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
