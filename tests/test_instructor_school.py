"""Integration tests for fayna_instructor_school.

Coverage target: ≥ 70 % (models + state machine + ACL + website route).
"""

from datetime import date, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import HttpCase, TransactionCase


@tagged("post_install", "-at_install")
class TestInstructorCourse(TransactionCase):
    """Tests for fayna.instructor.course model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = date.today()
        cls.tomorrow = cls.today + timedelta(days=1)
        cls.next_week = cls.today + timedelta(days=7)

    def _make_course(self, **kw):
        vals = {
            "name": "Test Course",
            "start_date": self.tomorrow,
            "max_participants": 10,
        }
        vals.update(kw)
        return self.env["fayna.instructor.course"].create(vals)

    # ---------------------------------------------------------------- #
    # test_create_course                                                #
    # ---------------------------------------------------------------- #
    def test_create_course(self):
        course = self._make_course(name="Leadership 101", location="Warsaw")
        self.assertEqual(course.state, "draft")
        self.assertEqual(course.location, "Warsaw")
        self.assertEqual(course.max_participants, 10)
        self.assertEqual(course.enrolled_count, 0)
        self.assertEqual(course.available_spots, 10)

    # ---------------------------------------------------------------- #
    # test_enrollment_creates                                           #
    # ---------------------------------------------------------------- #
    def test_enrollment_creates(self):
        course = self._make_course()
        course.action_open_enrollment()
        partner = self.env["res.partner"].create({"name": "Anna Kowalska"})
        enrollment = self.env["fayna.instructor.enrollment"].create(
            {
                "course_id": course.id,
                "partner_id": partner.id,
            }
        )
        self.assertEqual(enrollment.state, "pending")
        self.assertEqual(enrollment.payment_status, "unpaid")
        self.assertEqual(course.enrolled_count, 1)

    # ---------------------------------------------------------------- #
    # test_double_enrollment_prevented                                  #
    # ---------------------------------------------------------------- #
    def test_double_enrollment_prevented(self):
        course = self._make_course()
        course.action_open_enrollment()
        partner = self.env["res.partner"].create({"name": "Duplicate User"})
        self.env["fayna.instructor.enrollment"].create(
            {"course_id": course.id, "partner_id": partner.id}
        )
        from odoo.tools import mute_logger
        from psycopg2 import IntegrityError

        with mute_logger("odoo.sql_db"), self.assertRaises((IntegrityError, Exception)):
            self.env["fayna.instructor.enrollment"].create(
                {"course_id": course.id, "partner_id": partner.id}
            )

    # ---------------------------------------------------------------- #
    # test_available_spots_compute                                      #
    # ---------------------------------------------------------------- #
    def test_available_spots_compute(self):
        course = self._make_course(max_participants=3)
        course.action_open_enrollment()
        for i in range(3):
            p = self.env["res.partner"].create({"name": f"Participant {i}"})
            self.env["fayna.instructor.enrollment"].create(
                {"course_id": course.id, "partner_id": p.id}
            )
        self.assertEqual(course.enrolled_count, 3)
        self.assertEqual(course.available_spots, 0)

    # ---------------------------------------------------------------- #
    # test_state_machine_open_to_complete                               #
    # ---------------------------------------------------------------- #
    def test_state_machine_open_to_complete(self):
        course = self._make_course()
        self.assertEqual(course.state, "draft")

        course.action_open_enrollment()
        self.assertEqual(course.state, "open")

        course.action_start()
        self.assertEqual(course.state, "in_progress")

        course.action_complete()
        self.assertEqual(course.state, "completed")

    def test_state_machine_wrong_transition_raises(self):
        course = self._make_course()
        with self.assertRaises(UserError):
            course.action_start()  # draft → in_progress not allowed

    # ---------------------------------------------------------------- #
    # test_cancel_course_cancels_enrollments                            #
    # ---------------------------------------------------------------- #
    def test_cancel_course_cancels_enrollments(self):
        course = self._make_course()
        course.action_open_enrollment()
        partner = self.env["res.partner"].create({"name": "Bob"})
        enrollment = self.env["fayna.instructor.enrollment"].create(
            {"course_id": course.id, "partner_id": partner.id}
        )
        enrollment.action_confirm()
        self.assertEqual(enrollment.state, "confirmed")

        course.action_cancel()
        self.assertEqual(course.state, "cancelled")
        self.assertEqual(enrollment.state, "cancelled")

    # ---------------------------------------------------------------- #
    # test_date_constraint                                              #
    # ---------------------------------------------------------------- #
    def test_date_constraint_end_before_start(self):
        with self.assertRaises((UserError, ValidationError)):
            self.env["fayna.instructor.course"].create(
                {
                    "name": "Bad Dates",
                    "start_date": self.next_week,
                    "end_date": self.tomorrow,  # end < start
                }
            )


@tagged("post_install", "-at_install")
class TestInstructorEnrollment(TransactionCase):
    """Tests for fayna.instructor.enrollment model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = date.today()
        cls.course = cls.env["fayna.instructor.course"].create(
            {
                "name": "Enrollment Test Course",
                "start_date": cls.today + timedelta(days=5),
                "max_participants": 20,
                "state": "open",
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Student"})

    def _enroll(self, partner=None, course=None):
        return self.env["fayna.instructor.enrollment"].create(
            {
                "course_id": (course or self.course).id,
                "partner_id": (partner or self.partner).id,
            }
        )

    # ---------------------------------------------------------------- #
    # test_acl_portal_user_can_enroll                                   #
    # ---------------------------------------------------------------- #
    def test_acl_portal_user_can_enroll(self):
        """Portal user can create their own enrollment via sudo (as controller does)."""
        portal_group = self.env.ref("base.group_portal")
        portal_user = self.env["res.users"].create(
            {
                "name": "Portal Student",
                "login": "portal_student_test@example.com",
                "groups_id": [(6, 0, [portal_group.id])],
            }
        )
        # Simulate controller behavior: sudo() create on behalf of partner
        enrollment = (
            self.env["fayna.instructor.enrollment"]
            .sudo()
            .create(
                {
                    "course_id": self.course.id,
                    "partner_id": portal_user.partner_id.id,
                }
            )
        )
        self.assertEqual(enrollment.state, "pending")
        self.assertEqual(enrollment.partner_id, portal_user.partner_id)

    def test_enrollment_confirm_complete_flow(self):
        enrollment = self._enroll()
        enrollment.action_confirm()
        self.assertEqual(enrollment.state, "confirmed")
        enrollment.action_complete()
        self.assertEqual(enrollment.state, "completed")

    def test_enrollment_cancel_flow(self):
        enrollment = self._enroll()
        enrollment.action_cancel()
        self.assertEqual(enrollment.state, "cancelled")
        with self.assertRaises(UserError):
            enrollment.action_cancel()  # already cancelled


@tagged("post_install", "-at_install")
class TestInstructorSchoolWebsite(HttpCase):
    """Website route smoke tests."""

    # ---------------------------------------------------------------- #
    # test_website_page_accessible                                      #
    # ---------------------------------------------------------------- #
    def test_website_page_accessible(self):
        """Public /instructor-school returns 200."""
        response = self.url_open("/instructor-school")
        self.assertEqual(response.status_code, 200)

    def test_website_page_lists_open_courses(self):
        """Open courses appear on the public page."""
        self.env["fayna.instructor.course"].create(
            {
                "name": "Visible Open Course",
                "start_date": date.today() + timedelta(days=3),
                "state": "open",
            }
        )
        response = self.url_open("/instructor-school")
        self.assertIn(b"Visible Open Course", response.content)

    def test_enroll_redirect_unauthenticated(self):
        """Unauthenticated enroll redirects to login (302)."""
        course = self.env["fayna.instructor.course"].create(
            {
                "name": "Auth Required Course",
                "start_date": date.today() + timedelta(days=3),
                "state": "open",
            }
        )
        response = self.url_open(
            f"/instructor-school/enroll/{course.id}",
            allow_redirects=False,
        )
        self.assertIn(response.status_code, (302, 303))
