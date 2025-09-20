from django.shortcuts import render
from core.models import Semester, Department, Student, Course, Section, Enrollment, PastOrPlanned
from django.db.models import Count


def conflict_report_home(request):
    semesters = Semester.objects.all().order_by('-semester_id')
    selected_semester_id = request.POST.get('semester', None)

    # If no semester is selected from the form, default to the most recent one
    if not selected_semester_id and semesters.exists():
        selected_semester_id = semesters.first().semester_id

    selected_semester = Semester.objects.filter(semester_id=selected_semester_id).first()

    scheduling_issues = []

    if selected_semester:
        # 1. Sections with no enrolled students
        empty_sections = Section.objects.filter(
            semester=selected_semester
        ).annotate(
            num_students=Count('enrollment')
        ).filter(num_students=0).select_related('course')

        if empty_sections:
            issues = {
                'title': 'Empty Sections',
                'description': 'The following sections have no students enrolled.',
                'sections': empty_sections
            }
            scheduling_issues.append(issues)

        # 2. Sections with high enrollment
        over_capacity_sections = Section.objects.filter(
            semester=selected_semester
        ).annotate(
            num_students=Count('enrollment')
        ).filter(num_students__gt=20).select_related('course')  # Using 20 as an arbitrary high number

        if over_capacity_sections:
            issues = {
                'title': 'Over-Capacity Sections',
                'description': 'These sections have more students than recommended (over 20).',
                'sections': over_capacity_sections
            }
            scheduling_issues.append(issues)

        # 3. Courses with no sections
        courses_without_sections = Course.objects.filter(
            section__isnull=True
        )
        if courses_without_sections:
            issues = {
                'title': 'Courses Without Sections',
                'description': 'The following courses have not been assigned any sections.',
                'courses': courses_without_sections
            }
            scheduling_issues.append(issues)

    context = {
        'semesters': semesters,
        'selected_semester': selected_semester,
        'scheduling_issues': scheduling_issues
    }
    return render(request, 'conflictreport/home.html', context)