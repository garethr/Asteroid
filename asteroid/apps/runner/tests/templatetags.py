from test_extensions.django_common import DjangoCommon

class TemplateTagTests(DjangoCommon):
    "Tests for the templatetags"

    def test_converst_in_progress(self):
        "Example template tag test to check correct rendering"
        expected = 'in progress'
        self.assert_render(expected, """{% load correct_status %}{{"in_progress"|correct_status }}""")

    def test_doesnt_convert_succeeded(self):
        "Example template tag test to check correct rendering"
        expected = 'succeeded'
        self.assert_render(expected, """{% load correct_status %}{{"succeeded"|correct_status }}""")

    def test_doesnt_convert_failed(self):
        "Example template tag test to check correct rendering"
        expected = 'failed'
        self.assert_render(expected, """{% load correct_status %}{{"failed"|correct_status }}""")
