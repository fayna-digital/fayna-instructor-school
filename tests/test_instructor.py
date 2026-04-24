from datetime import date

from odoo.tests.common import TransactionCase


class TestInstructor(TransactionCase):
    def test_course_create(self):
        course = self.env["instructor.course"].create(
            {
                "name": "Leadership",
                "category": "child_psychology",
                "start_date": date.today(),
            }
        )
        self.assertTrue(course.certificate_issued)
