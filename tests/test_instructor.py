from odoo.tests.common import TransactionCase


class TestInstructor(TransactionCase):
    def test_course_create(self):
        course = self.env["instructor.course"].create(
            {
                "name": "Leadership",
                "course_type": "wychowawca",
                "duration_hours": 36.0,
            }
        )
        self.assertEqual(course.name, "Leadership")
        self.assertEqual(course.state, "draft")
