from django.shortcuts import render

# Create your views here.


def conflict_report_home(request):
    return render(request, 'conflictreport/home.html')