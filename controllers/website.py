from odoo import _, http
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
        """Public listing of published open/in-progress courses."""
        courses = (
            request.env["instructor.course"]
            .sudo()
            .search(
                [
                    ("website_published", "=", True),
                    ("state", "in", ("open", "in_progress")),
                ],
                order="start_date asc",
            )
        )
        return request.render(
            "fayna_instructor_school.page_instructor_school",
            {
                "courses": courses,
                "page_name": "instructor_school",
            },
        )

    @http.route(
        "/instructor-school/apply/<int:course_id>",
        auth="public",
        website=True,
        type="http",
        methods=["GET", "POST"],
        csrf=True,
    )
    def instructor_school_apply(self, course_id, **kw):
        """Public application form — no login required.

        GET  — render the form.
        POST — validate, find-or-create partner, create enrollment.
        """
        course = request.env["instructor.course"].sudo().browse(course_id)
        if not course.exists() or not course.website_published:
            return request.not_found()

        error = None
        success = False

        if request.httprequest.method == "POST":
            name = kw.get("applicant_name", "").strip()
            email = kw.get("applicant_email", "").strip()
            phone = kw.get("applicant_phone", "").strip()

            if not name or not email:
                error = _("Заповніть ім'я та email.")
            elif course.available_spots <= 0:
                error = _("На жаль, місця закінчились.")
            else:
                partner = (
                    request.env["res.partner"]
                    .sudo()
                    .search([("email", "=", email)], limit=1)
                )
                if not partner:
                    partner = request.env["res.partner"].sudo().create(
                        {"name": name, "email": email, "phone": phone}
                    )
                # Guard against duplicate application
                existing = (
                    request.env["instructor.enrollment"]
                    .sudo()
                    .search(
                        [
                            ("course_id", "=", course.id),
                            ("partner_id", "=", partner.id),
                        ],
                        limit=1,
                    )
                )
                if existing:
                    error = _("Ця електронна адреса вже зареєстрована на цей курс.")
                else:
                    request.env["instructor.enrollment"].sudo().create(
                        {
                            "course_id": course.id,
                            "partner_id": partner.id,
                            "state": "pending",
                        }
                    )
                    success = True

        return request.render(
            "fayna_instructor_school.page_instructor_apply",
            {
                "course": course,
                "error": error,
                "success": success,
                "page_name": "instructor_school",
            },
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
        course_model = request.env["instructor.course"].sudo()
        course = course_model.browse(course_id).exists()

        if not course or course.state != "open":
            return request.redirect("/instructor-school")

        # Resolve the partner for the current user
        partner = request.env.user.partner_id

        # Check for existing enrollment
        existing = (
            request.env["instructor.enrollment"]
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
        request.env["instructor.enrollment"].sudo().create(
            {
                "course_id": course.id,
                "partner_id": partner.id,
            }
        )

        return request.render(
            "fayna_instructor_school.instructor_school_enroll_confirm",
            {"course": course},
        )
