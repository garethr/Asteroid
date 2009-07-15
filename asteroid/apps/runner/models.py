"Models for Asteroid"

import commands
from datetime import datetime

from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.conf import settings
from django.db import models

from amqplib import client_0_8 as amqp

# set of available statuses for runs
STATUSES=(
    ('in_progress','In progress'),
    ('succeeded','Succeeded'),
    ('failed','Failed'),
)

class Run(models.Model):
    """
    A run represents a single execution of a command. It stores both the 
    command to be executed, the date at which it's run and eventually the 
    output of the command. Runs have a status so we can see where they have 
    got to.
    """
    created_date = models.DateTimeField(default=datetime.today)
    updated_date = models.DateTimeField(default=datetime.today)
    command = models.ForeignKey("Command", related_name='command', help_text="The command which resulted in this run.")
    command_run = models.TextField(help_text="The actual command run. Stored in case the command is later changed.")
    output = models.TextField(null=True, blank=True, help_text="The output resulting from this run.")
    status = models.CharField("Status", max_length=10, choices=STATUSES, default="in_progress", help_text="Is the command currently running, or did is succeed or fail.")

    class Meta:
        "meta information about Runs"
        # Last in first out makes more sense
        ordering = ['-updated_date']

    def get_absolute_url(self):
        "runs exist in the url structure underneath their command"
        return "/commands/%s/%s" % (self.command.slug, self.id)

    def save(self, *args, **kwargs):
        "we want to update the updated date if we save the command"
        self.updated_date = str(datetime.today())
        super(Run, self).save()
        
    def __unicode__(self):
        "friendly output"
        if self.status == "in_progress":
            status = "in progress"
        else:
            status = self.status
        return "%s %s on %s" % (self.command, status, self.created_date.strftime("%a %B %Y at %H:%M"))

class Command(models.Model):
    "Commands represent shell scripts which can be run from the web front end"
    title = models.CharField(max_length=200, help_text="A descritive name for this command.")
    slug = models.SlugField(max_length=200, help_text="An automatically generated url slug.")
    created_date = models.DateTimeField(default=datetime.today)
    updated_date = models.DateTimeField(default=datetime.today)
    description = models.TextField(null=True, blank=True, help_text="Include a more detailed description of this command.")
    command_to_run = models.TextField(help_text="A valid shell command. Be carefull as this is going to be executed as the web server user when the command is run.")
    
    def __unicode__(self):
        "friendly output"
        return self.title

    def status(self):
        "the status of the command is the status of the last run"
        # wrapped in a try/except to catch the case before the command is run
        try:
            run = Run.objects.filter(command=self)[:1][0]
            return run.status
        except IndexError:
            return "not run yet"

    def run(self):
        """
        We can use the application without the message queue, which isn't
        as good for long running commands and means commands will only be
        executed on the same machine as the web application is running
        """
        # create an in progress run
        run = Run(
            command = self,
            command_run = self.command_to_run,
        )
        run.save()
        
        # execute the command and store the output and error code
        code, output = commands.getstatusoutput(self.command_to_run)

        # 0 is good, anything else is an error state
        if code == 0:
            run.status = "succeeded"
        else:
            run.status = "failed"
        run.output = output
        run.save()
        
        # return the saved run object
        return run
        
    def queue_run(self):
        """
        Create a run object, setting it's status to in progress then
        send a JSON document containing the command_to_run details and the
        run identifier to the queue
        """

        # again we create an in progress run
        run = Run(
            command = self,
            command_run = self.command_to_run,
        )
        run.save()
        
        # pre-json data structure
        obj = {
            'webhook': "%s%s%s/hook/" % (settings.DOMAIN, self.get_absolute_url(), run.id),
            'command': self.command_to_run,
        }
        
        json = simplejson.dumps(obj)
        # put json on message queue
        conn = amqp.Connection(settings.QUEUE_ADDRESS)
        # and get a channel
        chan = conn.channel()

        # define your exchange
        # if they already exist then we check they are of the correct type
        chan.exchange_declare(exchange='asteroid', type="direct", 
        durable=False, auto_delete=True)

        # and publish a message
        chan.basic_publish(amqp.Message(json), exchange="asteroid", routing_key="all")

        # close everything afterwards
        chan.close()
        conn.close()

        # return the run object
        return run

    def run_link(self):
        "we'll set up the link here so we can run it from the admin as well"
        return mark_safe('<a href="/commands/%s/run">Run command</a>' 
            % self.slug)
    run_link.allow_tags = True

    def get_absolute_url(self):
        "commands exist in the url structure"
        return "/commands/%s/" % self.slug

    def save(self, *args, **kwargs):
        "we want to update the updated date if we save the command"
        self.updated_date = str(datetime.today())
        super(Command, self).save()
