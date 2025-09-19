from django.shortcuts import render
# Create your views here.


def student_plan_home(request):
    return render(request, 'studentplan/home.html')