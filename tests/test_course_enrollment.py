"""Tests for instructor.course and instructor.enrollment models.

Covers the 5 required test cases:
  - test_create_course
  - test_enroll_partner
  - test_complete_enrollment
  - test_course_enrollment_count
  - test_archived_course_cannot_enroll
"""

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestCourseEnrollment(TransactionCase):
    """Integration tests for instructor.course + instructor.enrollment."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_a = cls.env["res.partner"].create({"name": "Anna Nowak"})
        cls.partner_b = cls.env["res.partner"].create({"name": "Bohdan Koval"})

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _make_course(self, name="Test Course", state="draft", **kw):
        vals = {
            "name": name,
            "course_type": "wychowawca",
            "duration_hours": 36.0,
            "max_participants": 20,
            "state": state,
        }
        vals.update(kw)
        return self.env["instructor.course"].create(vals)

    def _enroll(self, course, partner):
        return self.env["instructor.enrollment"].create(
            {
                "course_id": course.id,
                "partner_id": partner.id,
            }
        )

    # ------------------------------------------------------------------ #
    # test_create_course                                                   #
    # ------------------------------------------------------------------ #

    def test_create_course(self):
        """Course is created with correct defaults."""
        course = self._make_course(name="Kurs wychowawcy 2026")
        self.assertEqual(course.name, "Kurs wychowawcy 2026")
        self.assertEqual(course.state, "draft")
        self.assertEqual(course.course_type, "wychowawca")
        self.assertEqual(course.duration_hours, 36.0)
        self.assertEqual(course.max_participants, 20)
        self.assertEqual(course.enrollment_count, 0)
        self.assertFalse(course.website_published)

    # ------------------------------------------------------------------ #
    # test_enroll_partner                                                  #
    # ------------------------------------------------------------------ #

    def test_enroll_partner(self):
        """Partner can be enrolled in an active course."""
        course = self._make_course(state="active")
        enrollment = self._enroll(course, self.partner_a)

        self.assertEqual(enrollment.state, "enrolled")
        self.assertEqual(enrollment.course_id, course)
        self.assertEqual(enrollment.partner_id, self.partner_a)
        self.assertTrue(enrollment.enrollment_date)

    # ------------------------------------------------------------------ #
    # test_complete_enrollment                                             #
    # ------------------------------------------------------------------ #

    def test_complete_enrollment(self):
        """Enrollment transitions from enrolled to completed."""
        course = self._make_course(state="active")
        enrollment = self._enroll(course, self.partner_a)
        self.assertEqual(enrollment.state, "enrolled")

        enrollment.action_complete()
        self.assertEqual(enrollment.state, "completed")

    def test_complete_enrollment_wrong_state_raises(self):
        """Cannot complete an already dropped enrollment."""
        course = self._make_course(state="active")
        enrollment = self._enroll(course, self.partner_a)
        enrollment.action_drop()
        with self.assertRaises(UserError):
            enrollment.action_complete()

    # ------------------------------------------------------------------ #
    # test_course_enrollment_count                                         #
    # ------------------------------------------------------------------ #

    def test_course_enrollment_count(self):
        """enrollment_count computed field tracks enrolled records."""
        course = self._make_course(state="active")
        self.assertEqual(course.enrollment_count, 0)

        self._enroll(course, self.partner_a)
        self.assertEqual(course.enrollment_count, 1)

        self._enroll(course, self.partner_b)
        self.assertEqual(course.enrollment_count, 2)

    # ------------------------------------------------------------------ #
    # test_archived_course_cannot_enroll                                   #
    # ------------------------------------------------------------------ #

    def test_archived_course_cannot_enroll(self):
        """Enrolling in an archived course raises UserError."""
        course = self._make_course(state="active")
        course.action_archive_course()
        self.assertEqual(course.state, "archived")

        with self.assertRaises((UserError, ValidationError)):
            self._enroll(course, self.partner_a)

    # ------------------------------------------------------------------ #
    # Additional coverage                                                  #
    # ------------------------------------------------------------------ #

    def test_state_machine_draft_to_active(self):
        """Draft course activates correctly."""
        course = self._make_course()
        self.assertEqual(course.state, "draft")
        course.action_activate()
        self.assertEqual(course.state, "active")

    def test_state_machine_active_to_archived(self):
        """Active course can be archived."""
        course = self._make_course(state="active")
        course.action_archive_course()
        self.assertEqual(course.state, "archived")

    def test_smart_button_action(self):
        """action_view_enrollments returns a valid window action dict."""
        course = self._make_course(state="active")
        self._enroll(course, self.partner_a)

        action = course.action_view_enrollments()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "instructor.enrollment")
        self.assertIn(("course_id", "=", course.id), action["domain"])

    def test_course_type_selection(self):
        """All valid course_type values are accepted."""
        for ctype in ("wychowawca", "kierownik", "first_aid", "specialty"):
            course = self._make_course(name=f"Course {ctype}", course_type=ctype)
            self.assertEqual(course.course_type, ctype)

    def test_drop_already_dropped_raises(self):
        """Dropping an already-dropped enrollment raises UserError."""
        course = self._make_course(state="active")
        enrollment = self._enroll(course, self.partner_a)
        enrollment.action_drop()
        with self.assertRaises(UserError):
            enrollment.action_drop()
