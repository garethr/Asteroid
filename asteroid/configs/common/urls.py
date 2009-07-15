from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.conf import settings

from runner.views import run_command, show_command, list_commands, show_run, \
    dashboard, list_runs, run_web_hook

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^$', dashboard),
    (r'^commands/$', list_commands),
    (r'^runs/$', list_runs),
    (r'^commands/(?P<command>[-\w]+)/(?P<run>\d+)/$', show_run),
    (r'^commands/(?P<command>[-\w]+)/run/$', run_command),
    (r'^commands/(?P<command>[-\w]+)/(?P<run>\d+)/hook/$', run_web_hook),
    (r'^commands/(?P<command>[-\w]+)/$', show_command),
    (r'^assets/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT
    }),
)