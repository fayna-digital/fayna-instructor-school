from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class InstructorCourse(models.Model):
    _name = "instructor.course"
    _description = "Instructor Course"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_date desc, name"

    name = fields.Char(required=True, translate=True, index=True, tracking=True)
    description = fields.Html(translate=True)
    duration_hours = fields.Float(string="Duration (hours)")
    course_type = fields.Selection(
        [
            ("wychowawca", "Kurs wychowawcy (36h)"),
            ("kierownik", "Kurs kierownika (10h)"),
            ("first_aid", "First aid / BLS"),
            ("specialty", "Specialty course"),
        ],
        string="Course Type",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    start_date = fields.Date(string="Start Date", tracking=True)
    end_date = fields.Date(string="End Date", tracking=True)
    location = fields.Char(string="Location")
    max_participants = fields.Integer(string="Max Participants", default=20)
    website_published = fields.Boolean(default=False)

    price = fields.Monetary(string="Price", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    enrollment_ids = fields.One2many(
        "instructor.enrollment",
        "course_id",
        string="Enrollments",
    )
    enrollment_count = fields.Integer(
        string="Enrollments",
        compute="_compute_enrollment_count",
        store=True,
    )
    enrolled_count = fields.Integer(
        string="Enrolled (active)",
        compute="_compute_enrolled_count",
        store=True,
    )
    available_spots = fields.Integer(
        string="Available Spots",
        compute="_compute_available_spots",
        store=True,
    )

    # ------------------------------------------------------------------ #
    # Computed fields                                                      #
    # ------------------------------------------------------------------ #

    @api.depends("enrollment_ids")
    def _compute_enrollment_count(self):
        for course in self:
            course.enrollment_count = len(course.enrollment_ids)

    @api.depends("enrollment_ids", "enrollment_ids.state")
    def _compute_enrolled_count(self):
        for course in self:
            course.enrolled_count = len(
                course.enrollment_ids.filtered(lambda e: e.state not in ("cancelled",))
            )

    @api.depends("max_participants", "enrolled_count")
    def _compute_available_spots(self):
        for course in self:
            course.available_spots = max(0, (course.max_participants or 0) - course.enrolled_count)

    # ------------------------------------------------------------------ #
    # Constraints                                                          #
    # ------------------------------------------------------------------ #

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for course in self:
            if course.end_date and course.start_date and course.end_date < course.start_date:
                raise ValidationError(_("End date cannot be before start date."))

    # ------------------------------------------------------------------ #
    # State-machine actions                                                #
    # ------------------------------------------------------------------ #

    def action_open_enrollment(self):
        for course in self:
            if course.state != "draft":
                raise UserError(_("Only draft courses can be opened for enrollment."))
            course.state = "open"

    def action_start(self):
        for course in self:
            if course.state != "open":
                raise UserError(_("Only open courses can be started."))
            course.state = "in_progress"

    def action_complete(self):
        for course in self:
            if course.state != "in_progress":
                raise UserError(_("Only in-progress courses can be completed."))
            course.state = "completed"
            for enrollment in course.enrollment_ids.filtered(lambda e: e.state == "confirmed"):
                enrollment.state = "completed"

    def action_cancel(self):
        for course in self:
            if course.state == "cancelled":
                continue
            course.state = "cancelled"
            course.enrollment_ids.filtered(
                lambda e: e.state not in ("cancelled", "completed")
            ).write({"state": "cancelled"})

    # ------------------------------------------------------------------ #
    # Smart button action                                                  #
    # ------------------------------------------------------------------ #

    def action_view_enrollments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Enrollments"),
            "res_model": "instructor.enrollment",
            "view_mode": "tree,form",
            "domain": [("course_id", "=", self.id)],
            "context": {"default_course_id": self.id},
        }
