from django import forms
from .models import Course, Subject, Staff, Period, TimetableEntry

class CourseForm(forms.ModelForm):
    """
    Form for creating and updating Course instances.

    Fields:
        - 'name': The name of the course.
    
    Meta:
        model (Course): The Course model.
        fields (list): Specifies that only the 'name' field is displayed in the form.
    """
    class Meta:
        model = Course
        fields = ['name']


class SubjectForm(forms.ModelForm):
    """
    Form for creating and updating Subject instances.

    Fields:
        - 'name': The name of the subject.
        - 'course': The related course for the subject.
        - 'staff': The staff members eligible to teach this subject.
    
    Meta:
        model (Subject): The Subject model.
        fields (list): Specifies the 'name', 'course', and 'staff' fields.
    """
    class Meta:
        model = Subject
        fields = ['name', 'course', 'staff']


class StaffForm(forms.ModelForm):
    """
    Form for creating and updating Staff instances, including related subjects.

    Fields:
        - 'name': The name of the staff member.
        - 'subjects': Subjects that the staff member is qualified to teach.
    
    Attributes:
        subjects (ModelMultipleChoiceField): Allows selection of multiple subjects.
    
    Meta:
        model (Staff): The Staff model.
        fields (list): Specifies the 'name' and 'subjects' fields.
    """
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        required=False
    )
    class Meta:
        model = Staff
        fields = ['name', 'subjects'] 


class PeriodForm(forms.ModelForm):
    """
    Form for creating and updating Period instances.

    Fields:
        - 'day': The day of the week for this period.
        - 'period_number': The sequential number of the period within the day.
        - 'start_time': The start time of the period.
        - 'end_time': The end time of the period.
    
    Meta:
        model (Period): The Period model.
        fields (list): Specifies the 'day', 'period_number', 'start_time', and 'end_time' fields.
    """
    class Meta:
        model = Period
        fields = ['day', 'period_number', 'start_time', 'end_time']


        
