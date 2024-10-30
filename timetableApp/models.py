from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, related_name='subjects', on_delete=models.CASCADE)
    staff = models.ManyToManyField('Staff', related_name='subjects')

    def __str__(self):
        return f"{self.name} - {self.course.name}"


class Staff(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Period(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]
    
    day = models.CharField(max_length=10, choices=DAY_CHOICES)  # Choices for days of the week
    period_number = models.PositiveSmallIntegerField(default=1)  # Default period number set to 1
    start_time = models.TimeField(blank=True, null=True)  # Make start_time optional
    end_time = models.TimeField(blank=True, null=True)  # Make end_time optional
    class Meta:
        unique_together = ('day', 'period_number')  # Ensure unique period number per day

    def __str__(self):
        return f"{self.day} Period {self.period_number}"



class TimetableEntry(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    is_adjusted = models.BooleanField(default=False) 

    class Meta:
        unique_together = ('course', 'period', 'subject')

    def __str__(self):
        return f"{self.course.name} - {self.subject.name} - {self.period}"
