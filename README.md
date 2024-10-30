# Timetable Generation Application

This is a Django-based web application designed to facilitate timetable management for courses, subjects, and staff. It supports the automated generation of timetables and provides an intuitive interface for manual adjustments by administrators. Key features include CRUD operations for `Courses`, `Subjects`, `Staff`, and flexible validation rules to avoid scheduling conflicts.

## Features

- **CRUD Operations**: Manage courses, subjects, and staff data with intuitive interfaces.
- **Timetable Generation**: Automatically generate timetables based on course requirements and available staff.
- **Manual Adjustment**: Administrators can manually edit the generated timetable and assign subjects and staff for each period.
- **Validation**: Prevents scheduling conflicts by filtering available staff for a specific subject who are not already assigned to a different course during the same period on the same day.
- **Dynamic Filtering**: Staff dropdown filters dynamically based on the selected subject, period, and day, ensuring only eligible staff are shown.

## Technologies

- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript (jQuery for AJAX calls)
- **Database**: SQLite (default, configurable to other databases)
- **APIs**: JSON-based API for AJAX-driven staff filtering

## Setup

### Prerequisites

- **Python** (version 3.8+)
- **Django** (version 3.2+)

### Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/yourusername/timetable-app.git
    cd timetable-app
    ```

2. **Create a virtual environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install the required packages**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Apply migrations**:

    ```bash
    python manage.py migrate
    ```

5. **Create a superuser** (for admin access):

    ```bash
    python manage.py createsuperuser
    ```

6. **Start the development server**:

    ```bash
    python manage.py runserver
    ```

7. **Access the application** at `http://127.0.0.1:8000`.

## Usage

### 1. CRUD Operations
   - Navigate to the sections for `Courses`, `Subjects`, and `Staff` to add, edit, or delete records.
   - Each record type is accessible through the navigation bar at the top.

### 2. Generating and Editing Timetables
   - Navigate to the `Timetable` section to view or generate timetables.
   - Use the edit functionality to manually adjust assignments, ensuring no conflicts.

### 3. AJAX-Based Staff Filtering
   - When editing timetable entries, the staff dropdown dynamically updates based on selected subject, day, and period to show only available staff.

## API Endpoints

- **`/get_staff_by_subject/<subject_id>/<day>/<period_number>/`**: Returns a JSON list of available staff for a specific subject, day, and period. Used for AJAX requests when dynamically updating the staff dropdown.

## Project Structure

- **templates/**: Contains all HTML templates, including consistent designs for list and edit pages.
- **views.py**: Main business logic for handling timetable generation, CRUD operations, and staff filtering.
- **models.py**: Django models for `Course`, `Subject`, `Staff`, `TimetableEntry`, and `Period`.
- **urls.py**: URL configuration for the application.
