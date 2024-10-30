from django import forms
from .models import Course, Subject, Staff, Period, TimetableEntry

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name']  # Only include fields you want users to fill out


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'course', 'staff']  # `course` and `staff` are foreign keys


class StaffForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        required=False
    )
    class Meta:
        model = Staff
        fields = ['name', 'subjects'] 


class PeriodForm(forms.ModelForm):
    class Meta:
        model = Period
        fields = ['day', 'period_number', 'start_time', 'end_time']


class TimetableUpdateForm(forms.ModelForm):
    class Meta:
        model = TimetableEntry
        fields = ['subject', 'staff']
        
