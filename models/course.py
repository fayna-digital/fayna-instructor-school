from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class InstructorCourse(models.Model):
    _name = "instructor.course"
    _description = "Instructor Course"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

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
            ("active", "Active"),
            ("archived", "Archived"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    max_participants = fields.Integer(string="Max Participants", default=20)
    website_published = fields.Boolean(default=False)

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

    # ------------------------------------------------------------------ #
    # Computed fields                                                      #
    # ------------------------------------------------------------------ #

    @api.depends("enrollment_ids")
    def _compute_enrollment_count(self):
        for course in self:
            course.enrollment_count = len(course.enrollment_ids)

    # ------------------------------------------------------------------ #
    # Constraints                                                          #
    # ------------------------------------------------------------------ #

    @api.constrains("state", "enrollment_ids")
    def _check_archived_no_enroll(self):
        for course in self:
            if course.state == "archived" and course.enrollment_ids:
                # Validate that no new enrollments can be created (enforced on enrollment)
                pass

    # ------------------------------------------------------------------ #
    # State-machine actions                                                #
    # ------------------------------------------------------------------ #

    def action_activate(self):
        for course in self:
            if course.state != "draft":
                raise UserError(_("Only draft courses can be activated."))
            course.state = "active"

    def action_archive_course(self):
        for course in self:
            if course.state == "archived":
                continue
            course.state = "archived"

    def action_reset_draft(self):
        for course in self:
            if course.state != "archived":
                raise UserError(_("Only archived courses can be reset to draft."))
            course.state = "draft"

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
