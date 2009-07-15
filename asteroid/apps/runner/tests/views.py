from test_extensions.django_common import DjangoCommon

from django.conf import settings

from runner.models import Run, Command

class ViewTests(DjangoCommon):
    "Tests for the site frontend"

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

    def test_dashboard(self):
        response = self.client.get('/')
        self.assert_code(response, 200)

    def test_commands(self):
        response = self.client.get('/commands/')
        self.assert_code(response, 200)

    def test_runs(self):
        response = self.client.get('/runs/')
        self.assert_code(response, 200)

    def test_command(self):
        response = self.client.get('/commands/test/')
        self.assert_code(response, 200)

    def test_run(self):
        response = self.client.get('/commands/test/1/')
        self.assert_code(response, 200)

    def test_running_command(self):
        response = self.client.get('/commands/test/2/')
        self.assert_code(response, 404)
        response = self.client.get('/commands/test/run/')
        self.assert_code(response, 302)
        response = self.client.get('/commands/test/2/')
        self.assert_code(response, 200)
        self.assert_counts([2, 1], [Run, Command])

    def test_slashes_are_added(self):
        response = self.client.get('/commands/test/1/hook')
        self.assert_code(response, 301)
        response = self.client.get('/commands/test/1')
        self.assert_code(response, 301)
        response = self.client.get('/commands/test')
        self.assert_code(response, 301)
        response = self.client.get('/commands')
        self.assert_code(response, 301)

    def test_without_queue(self):
        settings.QUEUE_COMMANDS = False
        response = self.client.get('/commands/test/2/')
        self.assert_code(response, 404)
        response = self.client.get('/commands/test/run/')
        self.assert_code(response, 302)
        response = self.client.get('/commands/test/2/')
        self.assert_code(response, 200)
        self.assert_counts([2, 1], [Run, Command])
        
    def test_webhook_with_get(self):
        response = self.client.get('/commands/test/1/hook/')
        self.assert_code(response, 405)
        
    def test_non_existent_run_hook(self):
        response = self.client.post('/commands/test/3/hook/', {'test': 'test',})
        self.assert_code(response, 404)
        
    def test_run_hook_with_bad_request(self):
        response = self.client.post('/commands/test/1/hook/', {'test': 'test',})
        self.assert_code(response, 400)