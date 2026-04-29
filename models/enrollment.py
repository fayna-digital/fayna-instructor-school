from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class InstructorEnrollment(models.Model):
    _name = "instructor.enrollment"
    _description = "Instructor Enrollment"
    _inherit = ["mail.thread"]
    _order = "enrollment_date desc"

    course_id = fields.Many2one(
        "instructor.course",
        string="Course",
        required=True,
        ondelete="restrict",
        index=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Participant",
        required=True,
        index=True,
        ondelete="restrict",
    )
    enrollment_date = fields.Date(
        string="Enrollment Date",
        default=fields.Date.today,
        required=True,
    )
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
        required=True,
        tracking=True,
    )
    completion_date = fields.Date()
    certificate_number = fields.Char()
    notes = fields.Text(string="Notes")
    payment_status = fields.Selection(
        [
            ("unpaid", "Unpaid"),
            ("paid", "Paid"),
        ],
        string="Payment",
        default="unpaid",
        required=True,
        tracking=True,
    )

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
    def _check_course_not_cancelled(self):
        for enrollment in self:
            if enrollment.course_id.state == "cancelled" and enrollment.state == "pending":
                raise ValidationError(
                    _("Cannot enroll in a cancelled course: %s") % enrollment.course_id.name
                )

    # ------------------------------------------------------------------ #
    # State-machine actions                                                #
    # ------------------------------------------------------------------ #

    def action_confirm(self):
        for enrollment in self:
            if enrollment.state != "pending":
                raise UserError(_("Only pending enrollments can be confirmed."))
            enrollment.state = "confirmed"

    def action_complete(self):
        for enrollment in self:
            if enrollment.state != "confirmed":
                raise UserError(_("Only confirmed enrollments can be completed."))
            enrollment.state = "completed"

    def action_cancel(self):
        for enrollment in self:
            if enrollment.state in ("completed", "cancelled"):
                raise UserError(_("Cannot cancel a completed or already cancelled enrollment."))
            enrollment.state = "cancelled"

    # ------------------------------------------------------------------ #
    # Create guard — capacity check                                        #
    # ------------------------------------------------------------------ #

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            course = record.course_id
            if course.max_participants and course.available_spots < 0:
                raise UserError(_("Course '%s' is fully booked.") % course.name)
        return records
