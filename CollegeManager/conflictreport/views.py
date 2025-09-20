from django.shortcuts import render
from core.models import Semester, Department, Student, Course, Section, Enrollment, PastOrPlanned
from django.db.models import Count
import datetime
from conflictreport.util_functions import semester_to_number


"""
For a target future semester (typically the next semester), generate a conflict report that:
Estimates how many students are planning to take each course.
Highlights course pairs that should not be scheduled at the same time.
Prioritizes conflicts to help in building the course schedule.

conflict level for each course pair based on:
🧵 Overlap: Number of students planning to take both courses that semester.
🔁 Course Rarity: Less common courses (e.g., CS 356) have higher conflict weight than high-frequency ones (e.g., ENG 101).
🎓 Student Seniority: A conflict is worse if many near-graduation students are affected.
🧠 The system should be able to explain the reasoning behind any conflict level (e.g., “6 students plan to take both; both are single-section upper-level courses; 4 are graduating seniors”).

"""


def conflict_report_home(request):
    today = datetime.date.today()
    current_year = today.year
    current_month = today.month

    if 1 <= current_month <= 4:
        current_semester_int = (current_year * 10) + 0
    elif 5 <= current_month <= 7:
        current_semester_int = (current_year * 10) + 1
    else:
        current_semester_int = (current_year * 10) + 2

    # Get all semesters, convert to integers, and filter for future semesters
    all_semesters = Semester.objects.all().order_by('semester_id')
    future_semesters = [s for s in all_semesters if semester_to_number(s.semester_id) > current_semester_int]

    # Handle form submission and default semester selection
    selected_semester_id = request.POST.get('semester', None)

    if not selected_semester_id and future_semesters:
        selected_semester_id = future_semesters[0].semester_id

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
        'semesters': future_semesters,
        'selected_semester': selected_semester,
        'scheduling_issues': scheduling_issues
    }
    return render(request, 'conflictreport/home.html', context)