"Setup the Django administration"

from django.contrib import admin
from django import forms

from runner.models import Command, Run

class CommandAdmin(admin.ModelAdmin):
    "The command admin is used to populate the available commands"
    search_fields = ['title', 'description', 'command_to_run']
    list_display = ('title', 'description', 'run_link')
    prepopulated_fields = {'slug': ("title",)}
    ordering = ['title']
    date_hierarchy = 'created_date'
    fieldsets = (
        (None,
            {'fields':('title', 'description', 'command_to_run')}
        ),
        ('Meta',
            {
                'fields':('slug', ('created_date', 'updated_date')),
                'classes':('collapse',),                
            }
        ),
    )

class RunAdmin(admin.ModelAdmin):
    "The run admin is really only available for completeness"
    list_display = ('command', 'created_date', 'updated_date', 'status')
    ordering = ['-updated_date']
    date_hierarchy = 'updated_date'
    list_filter = ['command', 'status']
    fieldsets = (
        (None,
            {'fields':('command', 'status', 'output')}
        ),
        ('Meta',
            {
                'fields':('command_run', ('created_date', 'updated_date')),
                'classes':('collapse',),                
            }
        ),
    )

# register our admins
admin.site.register(Command, CommandAdmin)
admin.site.register(Run, RunAdmin)