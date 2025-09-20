from .models import *
from django.contrib import admin

# Register your models here.

admin.site.register(Semester)
admin.site.register(Department)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Section)
admin.site.register(Enrollment)