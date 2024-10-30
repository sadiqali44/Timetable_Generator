from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Subject, Staff, Period, TimetableEntry
from .forms import SubjectForm, StaffForm, PeriodForm, CourseForm
import random
from collections import defaultdict
from django.http import JsonResponse

def generate_timetable():
    """
    Generates a new timetable by assigning subjects and available staff to courses and periods, ensuring no scheduling conflicts.
    
    - Clears all existing TimetableEntry records.
    - Loops through each course to assign subjects and available staff members to periods.
    - Balances subject assignments across periods and avoids scheduling conflicts by checking staff availability.

    Returns:
        None
    """
    TimetableEntry.objects.all().delete()
    subject_assignment_count = defaultdict(lambda: defaultdict(int))
    for course in Course.objects.all():
        subjects = list(course.subjects.all())
        periods = Period.objects.all()
        
        for period in periods:
            random.shuffle(subjects)
            assigned = False  # Flag to indicate if a suitable entry is created
            subjects_sorted = sorted(subjects, key=lambda subj: subject_assignment_count[course][subj])
            for selected_subject in subjects_sorted:
                available_staff = list(selected_subject.staff.all())
                random.shuffle(available_staff)  # Shuffle staff list to pick a random available member
                
                for staff in available_staff:
                    conflict_exists = TimetableEntry.objects.filter(
                        staff=staff,
                        period__day=period.day,
                        period__period_number=period.period_number
                    ).exists()
                    
                    if not conflict_exists:
                        TimetableEntry.objects.create(
                            course=course,
                            subject=selected_subject,
                            staff=staff,
                            period=period
                        )
                        # Increment the assignment count for this subject
                        subject_assignment_count[course][selected_subject] += 1
                        assigned = True
                        break

                if assigned:
                    break


def generate_timetable_view(request):
    """
    View to trigger the timetable generation and redirect to the timetable listing page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to 'timetable_list'.
    """
    generate_timetable()
    return redirect('timetable_list')



def edit_timetable_row(request, course_id, day):
    """
    Allows manual editing of timetable entries for a specific course and day.

    - Retrieves the timetable entries for the specified course and day.
    - Filters staff availability for each period and subject, excluding those already assigned to other courses.
    - Updates timetable entries based on user-selected subjects and staff.

    Args:
        request (HttpRequest): The HTTP request object.
        course_id (int): The primary key of the course.
        day (str): The day of the week for editing timetable entries.

    Returns:
        HttpResponse: Redirects to 'timetable_list' after a POST request.
        HttpResponse: Renders 'edit_timetable_row.html' with initial and available staff data for the form.
    
    Template Context:
        - 'course': The Course instance being edited.
        - 'day': The day of the week.
        - 'timetable_entries': QuerySet of TimetableEntry objects for the specified course and day.
        - 'initial_staff_per_subject': Pre-filtered staff list for each subject.
        - 'available_staff_per_period': Staff available for each period without scheduling conflicts.
        - 'subjects': QuerySet of Subject objects related to the course.
    """
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
    return render(request, 'timetable/edit_timetable_row.html', {
        'course': course,
        'day': day,
        'timetable_entries': timetable_entries,
        'initial_staff_per_subject': initial_staff_per_subject,
        'available_staff_per_period': available_staff_per_period,
        'subjects': Subject.objects.filter(course=course)
    })
    
def get_staff_by_subject(request, subject_id):
    """
    Retrieves a list of staff members who can teach a specific subject.

    Args:
        request (HttpRequest): The HTTP request object.
        subject_id (int): The primary key of the subject.

    Returns:
        JsonResponse: A JSON response containing a list of staff members eligible to teach the subject.
    """
    staff = Staff.objects.filter(subjects=subject_id)
    staff_list = [{'id': staff_member.id, 'name': staff_member.name} for staff_member in staff]
    return JsonResponse({'staff': staff_list})

def create_course(request):
    """
    Handle the creation of a new course.

    If the request method is POST, validate the submitted course form data and save it.
    Redirect to the course list upon successful creation. If the request method is not POST,
    render an empty course form for user input.

    Args:
        request: The HTTP request object containing metadata about the request.

    Returns:
        HttpResponse: Renders the course creation form or redirects to the course list after creation.
    """
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')  # Redirect to course list after creation
    else:
        form = CourseForm()
    return render(request, 'timetable/course_form.html', {'form': form})

def course_list(request):
    """
    Retrieve and display a list of all courses.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Renders the list of courses.
    """
    courses = Course.objects.all()
    return render(request, 'timetable/course_list.html', {'courses': courses})

def update_course(request, pk):
    """
    Handle the update of an existing course.

    Retrieve the course by primary key (pk). If the request method is POST, validate the
    submitted form data and update the course. Redirect to the course list upon successful update.
    If the request method is not POST, render the form pre-filled with the course data.

    Args:
        request: The HTTP request object.
        pk: The primary key of the course to update.

    Returns:
        HttpResponse: Renders the course update form or redirects to the course list after update.
    """
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list') 
    else:
        form = CourseForm(instance=course)
    return render(request, 'timetable/course_form.html', {'form': form})

def delete_course(request, pk):
    """
    Handle the deletion of a course.

    Retrieve the course by primary key (pk). If the request method is POST, delete the course
    and redirect to the course list. If the request method is not POST, render the confirmation
    page for deletion.

    Args:
        request: The HTTP request object.
        pk: The primary key of the course to delete.

    Returns:
        HttpResponse: Renders the confirmation page or redirects to the course list after deletion.
    """
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        return redirect('course_list')
    return render(request, 'timetable/course_delete.html', {'course': course})

def subject_list(request):
    """
    Retrieve and display a list of all subjects.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Renders the list of subjects.
    """
    subjects = Subject.objects.all()
    return render(request, 'timetable/subject_list.html', {'subjects': subjects})

def subject_create(request):
    """
    Handle the creation of a new subject.

    If the request method is POST, validate the submitted subject form data and save it.
    Redirect to the subject list upon successful creation. If the request method is not POST,
    render an empty subject form for user input.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Renders the subject creation form or redirects to the subject list after creation.
    """
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subject_list')
    else:
        form = SubjectForm()
    return render(request, 'timetable/subject_form.html', {'form': form})

def subject_update(request, pk):
    """
    Handle the update of an existing subject.

    Retrieve the subject by primary key (pk). If the request method is POST, validate the
    submitted form data and update the subject. Redirect to the subject list upon successful update.
    If the request method is not POST, render the form pre-filled with the subject data.

    Args:
        request: The HTTP request object.
        pk: The primary key of the subject to update.

    Returns:
        HttpResponse: Renders the subject update form or redirects to the subject list after update.
    """
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('subject_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'timetable/subject_form.html', {'form': form})

def subject_delete(request, pk):
    """
    Handle the deletion of a subject.

    Retrieve the subject by primary key (pk). If the request method is POST, delete the subject
    and redirect to the subject list. If the request method is not POST, render the confirmation
    page for deletion.

    Args:
        request: The HTTP request object.
        pk: The primary key of the subject to delete.

    Returns:
        HttpResponse: Renders the confirmation page or redirects to the subject list after deletion.
    """
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        return redirect('subject_list')
    return render(request, 'timetable/subject_delete.html', {'subject': subject})

def staff_list(request):
    """
    Retrieve and display a list of all staff members.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Renders the list of staff members.
    """
    staffs = Staff.objects.prefetch_related('subjects').all()
    return render(request, 'staff/staff_list.html', {'staffs': staffs})

def staff_create(request):
    """
    Handle the creation of a new staff member.

    If the request method is POST, validate the submitted staff form data and save it.
    If subjects are provided, assign them to the newly created staff member.
    Redirect to the staff list upon successful creation. If the request method is not POST,
    render an empty staff form for user input.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Renders the staff creation form or redirects to the staff list after creation.
    """
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            staff = form.save()
            if 'subjects' in request.POST:
                subjects = request.POST.getlist('subjects') 
                staff.subjects.set(subjects) 
            return redirect('staff_list')
    else:
        form = StaffForm()

    subjects = Subject.objects.all() 
    return render(request, 'staff/staff_form.html', {'form': form, 'subjects': subjects})


def staff_update(request, pk):
    """
    Handle the update of an existing staff member.

    Retrieve the staff member by primary key (pk). If the request method is POST, validate the
    submitted form data and update the staff member. Update the assigned subjects accordingly.
    Redirect to the staff list upon successful update. If the request method is not POST,
    render the form pre-filled with the staff member's data.

    Args:
        request: The HTTP request object.
        pk: The primary key of the staff member to update.

    Returns:
        HttpResponse: Renders the staff update form or redirects to the staff list after update.
    """
    staff = get_object_or_404(Staff, pk=pk)
    
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            staff = form.save()  
            staff.subjects.set(request.POST.getlist('subjects'))  
            return redirect('staff_list')
    else:
        form = StaffForm(instance=staff)
    
    subjects = Subject.objects.all()
    return render(request, 'staff/staff_form.html', {'form': form, 'subjects': subjects, 'staff': staff})

def staff_delete(request, pk):
    """
    Deletes a specified staff member.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the staff member to delete.

    Returns:
        HttpResponse: Redirects to the 'staff_list' view after deletion on a POST request.
        HttpResponse: Renders the 'staff/staff_delete.html' template to confirm deletion.
    """
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        staff.delete()
        return redirect('staff_list')
    return render(request, 'staff/staff_delete.html', {'staff': staff})

def period_list(request):
    """
    Displays a list of periods with editable start and end times, and saves any modifications.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirects to 'period_list' after saving on a POST request.
        HttpResponse: Renders the 'timetable/period_list.html' template, listing all periods.
    
    Template Context:
        - 'periods': QuerySet of all Period objects.
        - 'days': List of weekdays ('Monday' to 'Friday').
        - 'period_numbers': Range object indicating period numbers (1 to 4).
    """
    periods = Period.objects.all() 
    if request.method == 'POST':
        for period in periods:
            start_time = request.POST.get(f'start_time_{period.pk}')
            end_time = request.POST.get(f'end_time_{period.pk}')
            period.start_time = start_time if start_time else None  
            period.end_time = end_time if end_time else None  
            period.save()
        return redirect('period_list') 

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    period_numbers = range(1, 5)
    return render(request, 'timetable/period_list.html', {'periods': periods, 'days': days, 'period_numbers': period_numbers})


def period_update(request, pk):
    """
    Updates the details of a specified period.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the period to update.

    Returns:
        HttpResponse: Redirects to 'period_list' after a successful update on a POST request.
        HttpResponse: Renders the 'timetable/period_form.html' template with a form for editing.
    
    Template Context:
        - 'form': Instance of PeriodForm pre-filled with the selected period's data.
    """
    period = get_object_or_404(Period, pk=pk)
    if request.method == 'POST':
        form = PeriodForm(request.POST, instance=period)
        if form.is_valid():
            form.save()
            return redirect('period_list')
    else:
        form = PeriodForm(instance=period)
    return render(request, 'timetable/period_form.html', {'form': form})

def timetable_list(request):
    """
    Displays a comprehensive timetable listing for all courses over a five-day week.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'timetable/timetable_list.html' template displaying the timetable.
    
    Template Context:
        - 'timetable_data': Dictionary where each course maps to its associated TimetableEntry instances.
        - 'days': List of weekdays ('Monday' to 'Friday').
        - 'period_numbers': Range object indicating period numbers (1 to 4).
    """
    courses = Course.objects.all()
    timetable_data = {}

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    period_numbers = range(1, 5)

    for course in courses:
        course_entries = TimetableEntry.objects.filter(course=course)
        timetable_data[course] = course_entries

    return render(request, 'timetable/timetable_list.html', {
        'timetable_data': timetable_data,
        'days': days,
        'period_numbers': period_numbers,
    })

