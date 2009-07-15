from test_extensions.django_common import DjangoCommon
 
class AdminTests(DjangoCommon):
    "Tests for the site admin"

    def test_login_for_home_page(self):
        self.login_as_admin()
        response = self.client.get('/admin/')
        self.assert_code(response, 200)
        self.assert_response_contains('Log out', response)
        
    def test_not_logged_in_homepage(self):
        response = self.client.get('/admin/')
        self.assert_code(response, 200)
        self.assert_response_contains('Log in', response)
    
    def test_runner_admin_registered(self):
        self.login_as_admin()
        response = self.client.get('/admin/runner/')
        self.assert_code(response, 200)
        response = self.client.get('/admin/runner/command/')
        self.assert_code(response, 200)
        response = self.client.get('/admin/runner/run/')
        self.assert_code(response, 200)
        response = self.client.get('/admin/runner/run/add/')
        self.assert_code(response, 200)
        response = self.client.get('/admin/runner/command/add/')
        self.assert_code(response, 200)