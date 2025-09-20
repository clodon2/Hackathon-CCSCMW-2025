# your_app/views.py
import csv
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from core.models import Semester, Department, Student, Course, Section, Enrollment, PastOrPlanned, Offering


def upload_csv(request):
    success_message = None
    if request.method == 'POST':
        import_type = request.POST.get('import_type')
        csv_file = request.FILES.get('csv_file')

        if not csv_file or not csv_file.name.endswith('.csv'):
            return HttpResponseBadRequest("Invalid file. Please upload a CSV file.")

        decoded_file = csv_file.read().decode('utf-8').splitlines()
        cleaned_lines = [line.replace("'", "") for line in decoded_file]
        reader = csv.DictReader(cleaned_lines)

        try:
            if import_type == 'course':
                for row in reader:
                    department_obj, created = Department.objects.get_or_create(
                        department_id=row['dept code']
                    )

                    # Create the Course entry using the row data
                    Course.objects.create(
                        course_id=row['crs id'],
                        department=department_obj,
                        course_num=row['crs num'],
                        title=row['title'],
                        min_hours=row['min hours'],
                        max_hours=row['max hours']
                    )

            elif import_type == 'student':
                for row in reader:
                    semester_obj, created = Semester.objects.get_or_create(semester_id=row['exp grad date'])

                    student_obj, created = Student.objects.get_or_create(
                        student_id=row['std id'],
                        defaults={
                            'name': row['name'],
                            'email': row['email'],
                            'expected_graduation': semester_obj
                        }
                    )

            elif import_type == 'section':
                for row in reader:
                    print(row)
                    # Retrieve related objects. These must exist in the database.
                    department_obj, created = Department.objects.get_or_create(department_id=row['dept code'])

                    # Note: You need to get the Course by both department and course number
                    course_obj = Course.objects.get(
                        department=department_obj,
                        course_num=int(row['crs num'])
                    )

                    semester_obj, created_sem = Semester.objects.get_or_create(semester_id=row['sem'])

                    # Create the Section entry using get_or_create to prevent duplicates
                    Section.objects.get_or_create(
                        section_id=row['sec id'],
                        defaults={
                            'department': department_obj,
                            'course': course_obj,
                            'section_num': int(row['sec num']),
                            'semester': semester_obj
                        }
                    )

            elif import_type == 'enrollment':
                for row in reader:
                    # Get the related Student and Section objects. They must exist in the database.
                    student_obj = Student.objects.get(student_id=row['std id'])
                    section_obj = Section.objects.get(section_id=row['sec id'])

                    # Create the Enrollment record, using get_or_create to prevent duplicates
                    Enrollment.objects.get_or_create(
                        student=student_obj,
                        section=section_obj
                    )

            elif import_type == "planned":
                for row in reader:
                    # Get the related Student and Section objects. They must exist in the database.
                    student_obj = Student.objects.get(student_id=row['std id'])
                    course_obj = Course.objects.get(course_id=row['crs id'])
                    semester_obj, created = Semester.objects.get_or_create(semester_id=row['sem'])

                    # Create the Enrollment record, using get_or_create to prevent duplicates
                    PastOrPlanned.objects.get_or_create(
                        student=student_obj,
                        course=course_obj,
                        semester=semester_obj
                    )

            elif import_type == "offering":
                for row in reader:
                    course_obj = Course.objects.get(course_id=row['crs id'])

                    # Create the Enrollment record, using get_or_create to prevent duplicates
                    Offering.objects.get_or_create(
                        course=course_obj,
                        offering_code=row['code'].replace("'", "")
                    )

            success_message = f"Successfully imported data for {import_type}!"

        except (Department.DoesNotExist, Course.DoesNotExist, Semester.DoesNotExist) as e:
            return HttpResponseBadRequest(
                f"A related record was not found for one of the sections. Error: {e}"
            )

        except (Student.DoesNotExist, Section.DoesNotExist) as e:
            # Handle cases where a related object is missing
            return HttpResponseBadRequest(
                f"A related record was not found. Please ensure all students and sections are imported first. Error: {e}"
            )

        except ValueError:
            # Handle cases where 'crs num' or 'sec num' is not a number
            return HttpResponseBadRequest(f"A numeric field had an invalid value.")

        except Exception as e:
            return HttpResponseBadRequest(f"An error occurred during import: {e}")

        """
        try:
            if import_type == 'offering':
                for row in reader:
                    Semester.objects.get_or_create(semester_id=row['semester_id'])

            elif import_type == 'department':
                for row in reader:
                    Department.objects.get_or_create(department_id=row['department_id'])

            elif import_type == 'course':
                for row in reader:
                    department_obj, _ = Department.objects.get_or_create(department_id=row['dept code'])
                    Course.objects.create(
                        course_id=row['crs id'],
                        department=department_obj,
                        course_num=row['crs num'],  # Corrected key
                        title=row['title'],
                        min_hours=row['min hours'],
                        max_hours=row['max hours']
                    )

            elif import_type == 'student':
                for row in reader:
                    semester_obj = Semester.objects.get(semester_id=row['expected_graduation_id'])
                    Student.objects.create(
                        student_id=row['student_id'],
                        name=row['name'],
                        email=row['email'],
                        expected_graduation=semester_obj
                    )

            elif import_type == 'section':
                for row in reader:
                    department_obj = Department.objects.get(department_id=row['department_id'])
                    course_obj = Course.objects.get(course_id=row['course_id'])
                    semester_obj = Semester.objects.get(semester_id=row['semester_id'])
                    Section.objects.create(
                        section_id=row['section_id'],
                        department=department_obj,
                        course=course_obj,
                        section_num=row['section_num'],
                        semester=semester_obj
                    )

            elif import_type == 'enrollment':
                for row in reader:
                    student_obj = Student.objects.get(student_id=row['student_id'])
                    section_obj = Section.objects.get(section_id=row['section_id'])
                    Enrollment.objects.get_or_create(
                        student=student_obj,
                        section=section_obj
                    )

        except Exception as e:
            return HttpResponseBadRequest(f"An error occurred during import: {e}")
        """

    return render(request, 'uploaddata/uploadpage.html', {'success_message': success_message})