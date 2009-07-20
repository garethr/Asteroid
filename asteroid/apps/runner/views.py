"Views for Asteroid"

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import Http404, HttpResponseNotFound, HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.conf import settings
from django.utils import simplejson
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from runner.models import Command, Run

def run_command(request, command):
    """
    to run a command we simply GET a specific url. We're using GET mainly
    for convenience. We'll see how it goes.
    """
    
    # check we have a valid command, if not throw a 404
    existing_command = get_object_or_404(Command, slug__iexact=command)

    # check whether we're using the message queue or not
    if settings.QUEUE_COMMANDS:
        run = existing_command.queue_run()
    else:
        run = existing_command.run()
    
    # redirect to the run that's been created
    return HttpResponseRedirect(run.get_absolute_url())
        
def run_web_hook(request, command, run):
    """
    The web hook lets the message queue tell us how the command got on. It 
    accepts a JSON document with the status and the output from the command.
    When we recieve it we also change the status.
    """

    # we're dealing with a post request
    if request.POST:
        try:
            # we try and get the run based on the url parameters
            existing_run = Run.objects.get(id=run, command__slug=command)

            # the web hook will only run against in progress tasks
            # so in theory should only be run once.
            if existing_run.status == "in_progress":

                # sample json input
                # json = """{
                #     "status": 0,
                #     "output": "bob2"
                # }"""
                
                # get json document from post body in request.POST
                json = request.raw_post_data

                # not try parse the JSON
                try:
                    obj = simplejson.loads(json)
                except ValueError, e:
                    # invalid input
                    return HttpResponseBadRequest()

                # get the status code and convert it to our values
                if obj['status'] == 0:
                    code = "succeeded"
                else:
                    code = "failed"

                # set the attributes on our run and save it
                existing_run.status = code # succeeded failed in_progress
                existing_run.output = obj['output']
                existing_run.save()

                # return a 200 code as everything went OK
                return HttpResponse(
                    content_type = 'application/javascript; charset=utf8'
                )

            else:
                # this run is not in progress, only the first response is recorded
                # should be client error
                return HttpResponseBadRequest()

        except Run.DoesNotExist:
            # we didn't find a run, so throw a 404
            return HttpResponseNotFound()

    else:
        # should be method not allowed as we only respond to post
        return HttpResponseNotAllowed(['POST'])

def list_commands(request):
    "list all the available commands in the system"
    # if none exist throw a 404
    commands = get_list_or_404(Command)
    context = {
        'commands': commands,
    }
    return render_to_response('list_commands.html', context,
        context_instance=RequestContext(request))

def list_runs(request):
    "list all the runs that have been made so far"
    runs = get_list_or_404(Run)
    
    paginator = Paginator(runs, 10) # Show 10 runs per page

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        run_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        run_list = paginator.page(paginator.num_pages)
    
    context = {
        'runs': run_list,
    }
    return render_to_response('list_runs.html', context,
        context_instance=RequestContext(request))
        
def show_run(request, command, run):
    "show an individual run. This will show the output once it's been recieved"

    try:
        # we're checking the id and the command at the same time
        existing_run = Run.objects.get(id=run, command__slug=command)
        context = {
            'run': existing_run,
        }
        return render_to_response('show_run.html', context,
            context_instance=RequestContext(request))

    except Run.DoesNotExist:
        # the run doesn't exist so throw a 404
        raise Http404

def show_command(request, command):
    "show an individual command, along with the last few runs"

    # throw a 404 if we don't find anything
    existing_command = get_object_or_404(Command, slug__iexact=command)
    
    # get all runs
    runs = Run.objects.filter(command=existing_command)
    
    paginator = Paginator(runs, 10) # Show 10 runs per page

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        run_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        run_list = paginator.page(paginator.num_pages)
    
    context = {
        'command': existing_command,
        'runs': run_list,
    }
    return render_to_response('show_command.html', context,
        context_instance=RequestContext(request))
        
def dashboard(request):
    "make a nice homepage dashboard with the commands and latest runs"

    commands = Command.objects.filter()
    runs = Run.objects.filter()[:20]

    context = {
        'commands': commands,
        'runs': runs,
    }
    return render_to_response('dashboard.html', context,
        context_instance=RequestContext(request))
