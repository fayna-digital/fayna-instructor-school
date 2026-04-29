from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class InstructorEnrollment(models.Model):
    _name = "instructor.enrollment"
    _description = "Instructor Enrollment"
    _inherit = ["mail.thread"]
    _order = "enrollment_date desc"

    course_id = fields.Many2one(
        "instructor.course",
        required=True,
        ondelete="restrict",
        index=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        index=True,
    )
    enrollment_date = fields.Date(default=fields.Date.today)
    state = fields.Selection(
        [
            ("enrolled", "Enrolled"),
            ("completed", "Completed"),
            ("dropped", "Dropped"),
        ],
        default="enrolled",
        required=True,
        tracking=True,
    )
    completion_date = fields.Date()
    certificate_number = fields.Char()
    notes = fields.Text()

    # ------------------------------------------------------------------ #
    # SQL constraints                                                      #
    # ------------------------------------------------------------------ #

    _sql_constraints = [
        (
            "unique_course_partner",
            "UNIQUE(course_id, partner_id)",
            "This person is already enrolled in this course.",
        ),
    ]

    # ------------------------------------------------------------------ #
    # Constraints                                                          #
    # ------------------------------------------------------------------ #

    @api.constrains("course_id", "state")
    def _check_course_not_archived(self):
        for enrollment in self:
            if enrollment.course_id.state == "archived" and enrollment.state == "enrolled":
                raise ValidationError(
                    _("Cannot enroll in an archived course: %s") % enrollment.course_id.name
                )

    # ------------------------------------------------------------------ #
    # State-machine actions                                                #
    # ------------------------------------------------------------------ #

    def action_complete(self):
        for enrollment in self:
            if enrollment.state != "enrolled":
                raise UserError(_("Only enrolled participants can be marked as completed."))
            enrollment.state = "completed"

    def action_drop(self):
        for enrollment in self:
            if enrollment.state == "dropped":
                raise UserError(_("Enrollment is already dropped."))
            enrollment.state = "dropped"

    # ------------------------------------------------------------------ #
    # Create guard — prevent enrollment in archived course                 #
    # ------------------------------------------------------------------ #

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.course_id.state == "archived":
                raise UserError(
                    _("Cannot enroll in an archived course: %s") % record.course_id.name
                )
        return records
