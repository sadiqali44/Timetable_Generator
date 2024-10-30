"""
URL configuration for timetable project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from timetableApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('generate_timetable/', views.generate_timetable_view, name='generate_timetable'),
    path('', views.timetable_list, name='timetable_list'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/<int:pk>/update/', views.update_course, name='update_course'),
    path('courses/<int:pk>/delete/', views.delete_course, name='delete_course'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/update/', views.subject_update, name='subject_update'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    path('staffs/', views.staff_list, name='staff_list'),
    path('staffs/create/', views.staff_create, name='staff_create'),
    path('staffs/<int:pk>/update/', views.staff_update, name='staff_update'),
    path('staffs/<int:pk>/delete/', views.staff_delete, name='staff_delete'),
    path('periods/', views.period_list, name='period_list'),
    path('period/update/<int:pk>/', views.period_update, name='period_update'),
    path('timetable/edit/<int:course_id>/<str:day>/', views.edit_timetable_row, name='edit_timetable_row'),
    path('get_staff/<int:subject_id>/', views.get_staff_by_subject, name='get_staff_by_subject'),
    
    

    
]
