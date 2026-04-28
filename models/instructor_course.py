from odoo import _, api, fields, models
from odoo.exceptions import UserError


class InstructorCourse(models.Model):
    _name = "fayna.instructor.course"
    _description = "Instructor School Course"
    _order = "start_date desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Course Name",
        required=True,
        tracking=True,
        index=True,
    )
    description = fields.Html(string="Description")
    start_date = fields.Date(string="Start Date", required=True, tracking=True)
    end_date = fields.Date(string="End Date", tracking=True)
    max_participants = fields.Integer(string="Max Participants", default=20)
    location = fields.Char(string="Location")

    price = fields.Monetary(string="Price", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    enrollment_ids = fields.One2many(
        "fayna.instructor.enrollment",
        "course_id",
        string="Enrollments",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )

    enrolled_count = fields.Integer(
        string="Enrolled",
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
                raise UserError(_("End date cannot be before start date."))

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
