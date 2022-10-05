from odoo import models, fields, api, _
from odoo.exceptions import  ValidationError , UserError



class RejectInheritTimesheetWizzard(models.TransientModel):
    _name = "reject.timesheet.wizard"


    reject_reason = fields.Text(string="Reject Reason")


    def reject_reset_draft(self):
        pm_group = self.env['res.users'].has_group('custom_bbi_timesheet.timesheet_project_manager_id')
        active_ids = self.env["account.analytic.line"].browse(self._context['ids'])
        for rec in active_ids:
            if self.env.user != rec.employee_id.user_id:
                if rec.validated_statu == 'draft':
                    raise ValidationError("You can't Reject and rest the draft timesheets")
                elif (rec.validated_statu == 'submit' or rec.validated_statu == 'approved' ):
                    rec.validated_statu = "draft"
                    rec.reject_reason = self.reject_reason

                elif rec.validated_statu == 'validated':
                    if pm_group:
                        rec.validated_statu = "draft"
                        rec.reject_reason = self.reject_reason
                    else:
                        raise ValidationError("only Project Manager reject and rest draft the validate timesheet")
            else:
                raise ValidationError(_("You can't Reject and rest draft your Timesheet.please go to your manager  "))



    def reject_timesheets(self):
        pm_group = self.env['res.users'].has_group('custom_bbi_timesheet.timesheet_project_manager_id')
        active_ids = self.env["account.analytic.line"].browse(self._context['ids'])
        for rec in active_ids:
            if self.env.user != rec.employee_id.user_id:
                if rec.validated_statu == 'draft':
                    raise ValidationError("You can't Reject the draft timesheets")
                elif (rec.validated_statu == 'submit' or rec.validated_statu == 'approved'):
                    rec.validated_statu = "rejected"
                    rec.reject_reason = self.reject_reason

                elif rec.validated_statu == 'validated':
                    if pm_group:
                        rec.validated_statu = "rejected"
                        rec.reject_reason = self.reject_reason
                    else:
                        raise ValidationError("only Project Manager reject the validate timesheet")

                elif rec.validated_statu == 'rejected':
                    raise ValidationError("You Can't Reject The Rejected timesheet line/s")

            else:
                raise ValidationError(_("You can't Reject your Timesheet.please go to your manager  "))





