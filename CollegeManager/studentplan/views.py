from django.shortcuts import render, redirect, get_object_or_404
from core.models import Student
# Create your views here.


def student_select(request):
    students = Student.objects.all().order_by("name")
    return render(request, "studentplan/selectstudent.html", {"students": students})


def set_student_session(request, pk):
    student = get_object_or_404(Student, pk=pk)
    request.session['student_id'] = student.id
    return redirect('schedule')


def student_scheduler(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('select_student')  # force them to pick one first
    student = get_object_or_404(Student, pk=student_id)
    return render(request, 'studentplan/scheduler.html', {'student': student})


def student_progress(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('select_student')  # force them to pick one first
    student = get_object_or_404(Student, pk=student_id)
    return render(request, 'studentplan/progress.html', {'student':student})