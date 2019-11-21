from django.contrib import admin
from .models import Project

@admin.register(Project)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'aws_resources')
    list_filter = ('hackathon',)