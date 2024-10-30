from django.db import models

class Course(models.Model):
    """
    Represents an academic course.

    Attributes:
        name (CharField): The name of the course.
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Subject(models.Model):
    """
    Represents a subject that is part of a course.

    Attributes:
        name (CharField): The name of the subject.
        course (ForeignKey): Reference to the related course.
        staff (ManyToManyField): Staff members qualified to teach this subject.
    """
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, related_name='subjects', on_delete=models.CASCADE)
    staff = models.ManyToManyField('Staff', related_name='subjects')

    def __str__(self):
        return f"{self.name} - {self.course.name}"


class Staff(models.Model):
    """
    Represents a staff member eligible to teach subjects.

    Attributes:
        name (CharField): The name of the staff member.
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Period(models.Model):
    """
    Represents a specific period in the school timetable for each weekday.

    Attributes:
        day (CharField): The day of the week for this period.
        period_number (PositiveSmallIntegerField): The period number within the day.
        start_time (TimeField): The start time of the period.
        end_time (TimeField): The end time of the period.
    
    Meta:
        unique_together (tuple): Ensures unique period numbers for each day.
    """
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]
    
    day = models.CharField(max_length=10, choices=DAY_CHOICES)  
    period_number = models.PositiveSmallIntegerField(default=1)  
    start_time = models.TimeField(blank=True, null=True)  
    end_time = models.TimeField(blank=True, null=True)  
    class Meta:
        unique_together = ('day', 'period_number')

    def __str__(self):
        return f"{self.day} Period {self.period_number}"



class TimetableEntry(models.Model):
    """
    Represents a specific entry in the timetable, assigning a subject and staff member to a period for a course.

    Attributes:
        course (ForeignKey): Reference to the course.
        subject (ForeignKey): Reference to the assigned subject.
        staff (ForeignKey): Reference to the staff member assigned for this subject and period.
        period (ForeignKey): Reference to the assigned period.
        is_adjusted (BooleanField): Flag indicating if this entry has been manually adjusted.

    Meta:
        unique_together (tuple): Ensures unique combination of course, period, and subject.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    is_adjusted = models.BooleanField(default=False) 

    class Meta:
        unique_together = ('course', 'period', 'subject')

    def __str__(self):
        return f"{self.course.name} - {self.subject.name} - {self.period}"
