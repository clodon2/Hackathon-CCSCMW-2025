from django.shortcuts import render
from core.models import Semester, Department, Student, Course, Section, Enrollment, PastOrPlanned, Offering
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

    # Get all semesters, convert to int, and filter for future semesters
    all_semesters = Semester.objects.all().order_by('semester_id')
    future_semesters = [s for s in all_semesters if semester_to_number(s.semester_id) > current_semester_int]

    # Handle form submission and default semester selection
    selected_semester_id = request.POST.get('semester', None)

    if not selected_semester_id and future_semesters:
        selected_semester_id = future_semesters[0].semester_id

    selected_semester = Semester.objects.filter(semester_id=selected_semester_id).first()

    conflict_scores = []

    if selected_semester:
        # get all courses in that semester
        all_courses = Course.objects.filter(
            section__semester=selected_semester
        ).distinct()
        course_list = list(all_courses)

        for i in range(len(course_list)):
            for j in range(i + 1, len(course_list)):
                course1 = course_list[i]
                course2 = course_list[j]

                students1_ids = set(Enrollment.objects.filter(
                    section__course=course1,
                    section__semester=selected_semester
                ).values_list('student__student_id', flat=True))

                students2_ids = set(Enrollment.objects.filter(
                    section__course=course2,
                    section__semester=selected_semester
                ).values_list('student__student_id', flat=True))

                overlapping_students_ids = students1_ids.intersection(students2_ids)
                print(overlapping_students_ids)

                overlapping_students = Student.objects.filter(student_id__in=list(overlapping_students_ids))

                grad_weight = 0
                overlap_rarity = 0
                for student in overlapping_students:
                    print(student, "overlapping")
                    grad_day = student.expected_graduation
                    grad_distance = (semester_to_number(grad_day.semester_id) -
                                    semester_to_number(selected_semester.semester_id))
                    if grad_distance != 0:
                        grad_weight += 2 / grad_distance
                    else:
                        grad_weight = 2

                if len(overlapping_students) > 0:
                    grad_weight /= len(overlapping_students)

                    # course rarity
                    rarity_map = {'e': 1,
                    'ef': 1.4, 'es': 1.4,
                    'fo': 1.6, 'fe': 1.6,
                    'so': 1.6, 'se': 1.6}

                    offering1 = Offering.objects.filter(course=course1).first().offering_code
                    offering2 = Offering.objects.filter(course=course2).first().offering_code

                    overlap_rarity = ( rarity_map.get(offering1) + rarity_map.get(offering2) ) / 2

                #overlap_count = len(students1_ids.intersection(students2_ids))

                if grad_weight > 0:
                    conflict_scores.append({
                        'course1': course1,
                        'course2': course2,
                        'conflict_score': overlap_rarity * grad_weight
                    })


    print(selected_semester, conflict_scores)

    context = {
        'semesters': future_semesters,
        'selected_semester': selected_semester,
        'course_conflicts': conflict_scores
    }
    return render(request, 'conflictreport/home.html', context)