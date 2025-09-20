from core.models import PastOrPlanned, Course
from conflictreport.util_functions import semester_to_number
import datetime


def calculate_conflict_score():
    today = datetime.date.today()
    current_year = today.year
    current_month = today.month

    if 1 <= current_month <= 4:
        current_semester_int = (current_year * 10) + 0
    elif 5 <= current_month <= 7:
        current_semester_int = (current_year * 10) + 1
    else:
        current_semester_int = (current_year * 10) + 2

    all_not_now = PastOrPlanned.objects.all().order_by('semester_id')
    planned = [s for s in all_not_now if semester_to_number(s.semester_id) > current_semester_int]

    all_courses = Cou


