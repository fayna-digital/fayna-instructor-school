from odoo import http
from odoo.http import request


class InstructorSchoolController(http.Controller):
    """Public website routes for Instructor School."""

    @http.route(
        "/instructor-school",
        auth="public",
        website=True,
        type="http",
        methods=["GET"],
    )
    def instructor_school_page(self, **kwargs):
        """Public listing of open courses."""
        courses = (
            request.env["fayna.instructor.course"]
            .sudo()
            .search([("state", "=", "open")], order="start_date asc")
        )
        return request.render(
            "fayna_instructor_school.instructor_school_page",
            {"courses": courses},
        )

    @http.route(
        "/instructor-school/enroll/<int:course_id>",
        auth="user",
        website=True,
        type="http",
        methods=["GET"],
    )
    def enroll(self, course_id, **kwargs):
        """Enroll the currently logged-in user into a course.

        Requires authentication (auth='user').  If the user is not logged in
        Odoo's website module redirects them to the login page automatically.
        """
        course_model = request.env["fayna.instructor.course"].sudo()
        course = course_model.browse(course_id).exists()

        if not course or course.state != "open":
            return request.redirect("/instructor-school")

        # Resolve the partner for the current user
        partner = request.env.user.partner_id

        # Check for existing enrollment
        existing = (
            request.env["fayna.instructor.enrollment"]
            .sudo()
            .search(
                [("course_id", "=", course.id), ("partner_id", "=", partner.id)],
                limit=1,
            )
        )
        if existing:
            return request.render(
                "fayna_instructor_school.instructor_school_already_enrolled",
                {"course": course},
            )

        # Check capacity
        if course.max_participants and course.available_spots <= 0:
            return request.redirect("/instructor-school")

        # Create the enrollment as the portal user via sudo (portal can create own)
        request.env["fayna.instructor.enrollment"].sudo().create(
            {
                "course_id": course.id,
                "partner_id": partner.id,
            }
        )

        return request.render(
            "fayna_instructor_school.instructor_school_enroll_confirm",
            {"course": course},
        )
