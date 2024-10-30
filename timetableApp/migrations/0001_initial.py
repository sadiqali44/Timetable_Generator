# Generated by Django 5.1.2 on 2024-10-30 11:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday')], max_length=10)),
                ('period_number', models.PositiveSmallIntegerField(default=1)),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
            ],
            options={
                'unique_together': {('day', 'period_number')},
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='timetableApp.course')),
                ('staff', models.ManyToManyField(related_name='subjects', to='timetableApp.staff')),
            ],
        ),
        migrations.CreateModel(
            name='TimetableEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_adjusted', models.BooleanField(default=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetableApp.course')),
                ('period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetableApp.period')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetableApp.staff')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetableApp.subject')),
            ],
            options={
                'unique_together': {('course', 'period', 'subject')},
            },
        ),
    ]