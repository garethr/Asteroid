from django.conf import settings
settings.QUEUE_COMMANDS = False

from admin import *
from models import *
from views import *
from templatetags import *