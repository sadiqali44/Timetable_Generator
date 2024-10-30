from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Subject, Staff, Period, TimetableEntry
from .forms import SubjectForm, StaffForm, PeriodForm, CourseForm, TimetableUpdateForm
import random
from collections import defaultdict
from django.http import JsonResponse

def generate_timetable():
    # Clear previous timetable entries
    TimetableEntry.objects.all().delete()

    # Initialize a counter to keep track of subject assignments per course
    subject_assignment_count = defaultdict(lambda: defaultdict(int))  # {course: {subject: count}}

    # Loop through each course to generate a timetable
    for course in Course.objects.all():
        subjects = list(course.subjects.all())

        # Get all periods for the week
        periods = Period.objects.all()
        
        for period in periods:
            # Shuffle subjects to avoid assigning them in the same order each time
            random.shuffle(subjects)
            assigned = False  # Flag to indicate if a suitable entry is created
            
            # Sort subjects by the number of times they’ve been assigned (ascending) to balance their distribution
            subjects_sorted = sorted(subjects, key=lambda subj: subject_assignment_count[course][subj])

            # Loop through sorted subjects until we find one with an available staff
            for selected_subject in subjects_sorted:
                available_staff = list(selected_subject.staff.all())
                random.shuffle(available_staff)  # Shuffle staff list to pick a random available member
                
                for staff in available_staff:
                    # Check if the staff is already assigned to the same period and day for a different course
                    conflict_exists = TimetableEntry.objects.filter(
                        staff=staff,
                        period__day=period.day,
                        period__period_number=period.period_number
                    ).exists()
                    
                    if not conflict_exists:
                        # If no conflict, create the timetable entry
                        TimetableEntry.objects.create(
                            course=course,
                            subject=selected_subject,
                            staff=staff,
                            period=period
                        )
                        # Increment the assignment count for this subject
                        subject_assignment_count[course][selected_subject] += 1
                        assigned = True  # Mark as assigned
                        break  # Exit the staff loop as we found a valid assignment

                if assigned:
                    break


def generate_timetable_view(request):
    generate_timetable()  # No parameters needed
    return redirect('timetable_list')  # Redirect to the timetable listing page



def edit_timetable_row(request, course_id, day):
    course = get_object_or_404(Course, id=course_id)
    periods = Period.objects.all()
    timetable_entries = TimetableEntry.objects.filter(course=course, period__day=day)

    # Pre-filter staff available for each period
    available_staff_per_period = {}
    for period in periods:
        unavailable_staff = TimetableEntry.objects.filter(
            period__day=day,
            period__period_number=period.period_number
        ).exclude(course=course).values_list('staff', flat=True)
        available_staff = Staff.objects.exclude(id__in=unavailable_staff)
        available_staff_per_period[period.period_number] = available_staff
        
    # Pre-filter staff for each timetable entry based on the subject
    initial_staff_per_subject = {}
    for entry in timetable_entries:
        initial_staff_per_subject[entry.subject.id] = Staff.objects.filter(subjects=entry.subject)
        
        # Get the staff members for the selected subject
        staff_for_subject = Staff.objects.filter(subjects=entry.subject)

        # Exclude staff already assigned to the same period on the same day for a different course
        already_assigned_staff = TimetableEntry.objects.filter(
            period__day=day,
            period__period_number=entry.period.period_number
        ).exclude(course=course).values_list('staff', flat=True)
        
        initial_staff_per_subject[entry.subject.id] = staff_for_subject.exclude(id__in=already_assigned_staff)

    if request.method == 'POST':
        for entry in timetable_entries:
            subject_id = request.POST.get(f'subject_{entry.period.period_number}')
            staff_id = request.POST.get(f'staff_{entry.period.period_number}')
            if subject_id and staff_id:
                entry.subject = Subject.objects.get(id=subject_id)
                entry.staff = Staff.objects.get(id=staff_id)
                entry.save()
        return redirect('timetable_list') 
    return render(request, 'edit_timetable_row.html', {
        'course': course,
        'day': day,
        'timetable_entries': timetable_entries,
        'initial_staff_per_subject': initial_staff_per_subject,
        'available_staff_per_period': available_staff_per_period,
        'subjects': Subject.objects.filter(course=course)
    })
    
def get_staff_by_subject(request, subject_id):
    staff = Staff.objects.filter(subjects=subject_id)
    staff_list = [{'id': staff_member.id, 'name': staff_member.name} for staff_member in staff]
    return JsonResponse({'staff': staff_list})

# Create Course
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')  # Redirect to course list after creation
    else:
        form = CourseForm()
    return render(request, 'timetable/course_form.html', {'form': form})

# Read Courses (List)
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'timetable/course_list.html', {'courses': courses})

# Update Course
def update_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')  # Redirect to course list after update
    else:
        form = CourseForm(instance=course)
    return render(request, 'timetable/course_form.html', {'form': form})

# Delete Course
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        return redirect('course_list')  # Redirect to course list after deletion
    return render(request, 'timetable/course_delete.html', {'course': course})

# List all subjects
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'timetable/subject_list.html', {'subjects': subjects})

# Create a new subject
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subject_list')
    else:
        form = SubjectForm()
    return render(request, 'timetable/subject_form.html', {'form': form})

# Update an existing subject
def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('subject_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'timetable/subject_form.html', {'form': form})

# Delete a subject
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        return redirect('subject_list')
    return render(request, 'timetable/subject_delete.html', {'subject': subject})

# List all staffs
def staff_list(request):
    staffs = Staff.objects.prefetch_related('subjects').all()
    return render(request, 'staff/staff_list.html', {'staffs': staffs})

# Create a new staff
def staff_create(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            staff = form.save()  # Save the staff instance
            # Assign subjects if provided
            if 'subjects' in request.POST:
                subjects = request.POST.getlist('subjects')  # Get list of selected subject IDs
                staff.subjects.set(subjects)  # Assign selected subjects to the staff
            return redirect('staff_list')
    else:
        form = StaffForm()

    subjects = Subject.objects.all()  # Get all subjects to display in the form
    return render(request, 'staff/staff_form.html', {'form': form, 'subjects': subjects})


# Update an existing staff
def staff_update(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            staff = form.save()  # Save the staff instance
            staff.subjects.set(request.POST.getlist('subjects'))  # Update the assigned subjects
            return redirect('staff_list')
    else:
        form = StaffForm(instance=staff)
    
    subjects = Subject.objects.all()  # Get all subjects to display in the form
    return render(request, 'staff/staff_form.html', {'form': form, 'subjects': subjects, 'staff': staff})

# Delete a staff
def staff_delete(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        staff.delete()
        return redirect('staff_list')
    return render(request, 'staff/staff_delete.html', {'staff': staff})

def period_list(request):
    periods = Period.objects.all()  # Retrieve all periods
    if request.method == 'POST':
        for period in periods:
            start_time = request.POST.get(f'start_time_{period.pk}')
            end_time = request.POST.get(f'end_time_{period.pk}')
            period.start_time = start_time if start_time else None  # Set to None if empty
            period.end_time = end_time if end_time else None  # Set to None if empty
            period.save()
        return redirect('period_list')  # Redirect after saving

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    period_numbers = range(1, 5)  # Assuming 4 periods in a day
    return render(request, 'timetable/period_list.html', {'periods': periods, 'days': days, 'period_numbers': period_numbers})


def period_update(request, pk):
    period = get_object_or_404(Period, pk=pk)
    if request.method == 'POST':
        form = PeriodForm(request.POST, instance=period)
        if form.is_valid():
            form.save()
            return redirect('period_list')  # Redirect back to the list after saving
    else:
        form = PeriodForm(instance=period)
    return render(request, 'timetable/period_form.html', {'form': form})

#Timetable
def timetable_list(request):
    courses = Course.objects.all()
    timetable_data = {}

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    period_numbers = range(1, 5)  # Assuming 4 periods in a day

    for course in courses:
        course_entries = TimetableEntry.objects.filter(course=course)
        timetable_data[course] = course_entries

    return render(request, 'timetable/timetable_list.html', {
        'timetable_data': timetable_data,
        'days': days,
        'period_numbers': period_numbers,
    })

