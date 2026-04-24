from odoo import fields, models


class InstructorCourse(models.Model):
    _name = "instructor.course"
    _description = "Instructor professional development courses"
    _order = "start_date desc"

    name = fields.Char(required=True, string="Course name")
    category = fields.Selection(
        [
            ("activity_leadership", "Activity Leadership"),
            ("child_psychology", "Child Psychology"),
            ("group_dynamics", "Group Dynamics"),
            ("safety_first_aid", "Safety & First Aid"),
            ("conflict_resolution", "Conflict Resolution"),
        ],
        required=True,
    )

    description = fields.Html(string="Course description")
    duration_days = fields.Integer(string="Duration (days)")

    start_date = fields.Date(required=True, string="Start date")
    end_date = fields.Date(string="End date")

    max_participants = fields.Integer(string="Max participants")
    enrolled_count = fields.Integer(
        string="Enrolled", compute="_compute_enrolled_count"
    )

    instructor_ids = fields.Many2many(
        "res.users", string="Instructors", help="Who teaches this course"
    )

    location = fields.Char(string="Location")
    cost = fields.Float(string="Cost (USD)", help="Fee per participant")

    certificate_issued = fields.Boolean(string="Issues certificate?", default=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("open", "Open for enrollment"),
            ("completed", "Completed"),
        ],
        default="draft",
    )

    def _compute_enrolled_count(self):
        for record in self:
            record.enrolled_count = 0
