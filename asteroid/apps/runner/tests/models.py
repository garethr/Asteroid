from test_extensions.django_common import DjangoCommon

from datetime import datetime

from runner.models import Run, Command

class RunTests(DjangoCommon):
    "Tests for the Run model"
    
    def setUp(self):
        self.assert_counts([0, 0], [Run, Command])
        command = Command.objects.create(
            title = "test",
            slug = "test",
            command_to_run = "ls",
        )
        self.assert_counts([0, 1], [Run, Command])
        run = Run.objects.create(
            command = command,
            command_run = command.command_to_run,
        )
        self.assert_counts([1, 1], [Run, Command])
        
        self.run = run
        self.command = command

    def test_get_absolute_url(self):
        self.assert_equal("/commands/test/1", self.run.get_absolute_url())

    def test_string_method_for_run(self):
        self.assert_equal("test in progress on %s" % datetime.now().strftime("%a %B %Y at %H:%M"), str(self.run))

    def test_string_method_when_not_in_progress(self):
        self.run.status = "succeeded"
        self.assert_equal("test succeeded on %s" % datetime.now().strftime("%a %B %Y at %H:%M"), str(self.run))
        

class CommandTests(DjangoCommon):
    "Tests for the Command model"

    def setUp(self):
        self.assert_counts([0, 0], [Run, Command])
        command = Command.objects.create(
            title = "test",
            slug = "test",
            command_to_run = "ls",
        )
        self.assert_counts([0, 1], [Run, Command])
        run = Run.objects.create(
            command = command,
            command_run = command.command_to_run,
        )
        self.assert_counts([1, 1], [Run, Command])

        self.run = run
        self.command = command
        
    def test_status_from_runs(self):
        self.assert_equal("in_progress", self.command.status())
        
    def test_status_without_runs(self):
        self.run.delete()
        self.assert_equal("not run yet", self.command.status())

    def test_run_creates_run(self):
        self.command.run()
        self.assert_counts([2, 1], [Run, Command])

    def test_run_changes_command_status(self):
        self.assert_equal("in_progress", self.command.status())
        self.command.run()
        self.assert_equal("succeeded", self.command.status())

    def test_run_that_fails(self):
        self.command.command_to_run = "return 2"
        self.command.run()
        self.assert_equal("failed", self.command.status())

    def test_get_absolute_url(self):
        self.assert_equal("/commands/test/", self.command.get_absolute_url())

    def test_run_link(self):
        self.assert_equal('<a href="/commands/test/run">Run command</a>', self.command.run_link())
