from django.contrib import admin
from .models import Course, Subject, Staff, Period, TimetableEntry

admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(Staff)
admin.site.register(Period)
admin.site.register(TimetableEntry)
