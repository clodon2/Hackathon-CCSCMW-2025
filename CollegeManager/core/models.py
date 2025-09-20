from tkinter.constants import CASCADE

from django.db import models


class Semester(models.Model):
    semester_id = models.CharField(max_length=6, unique=True)

    @property
    def name(self):
        if not self.semester_id or len(self.semester_id) < 4:
            return ""

        season_code = self.semester_id[:2].lower()
        year = self.semester_id[2:]

        season_names = {
            'fa': 'Fall',
            'sp': 'Spring',
            'su': 'Summer'
        }

        season = season_names.get(season_code, 'Unknown')

        return f"{season} {year}"

    def __str__(self):
        return f"{self.semester_id}"


class Department(models.Model):
    department_id = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return f"{self.department_id}"


class Student(models.Model):
    student_id = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    expected_graduation = models.ForeignKey(Semester, on_delete=models.CASCADE)
    class Meta: ordering=["student_id"]

    def __str__(self):
        return f"{self.name} ({self.student_id})"


class Course(models.Model):
    course_id = models.CharField(max_length=4, unique=True)  # e.g., CS 235
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    course_num = models.IntegerField()
    title = models.CharField(max_length=40)
    min_hours = models.FloatField()
    max_hours = models.FloatField()

    def __str__(self):
        return f"{self.course_id}: {self.title}"


class Section(models.Model):
    section_id = models.CharField(max_length=6, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    section_num = models.IntegerField()
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course} - {self.semester} (Section {self.section_id})"


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    class Meta: unique_together = ("student", "section")

    def __str__(self):
        return f"{self.student} enrolled in {self.section}"


class PastOrPlanned(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    class Meta: unique_together = ("student", "semester", "course")

    def __str__(self):
        return f"{self.student} past/future enrolled {self.course} in {self.semester}"
