

from odoo import fields, models


class CrmStage(models.Model):

    _inherit = "crm.stage"

    company_ids = fields.Many2many(
        "res.company",
        string="Company",
        index=True,
        help="Specific company that uses this stage. "
        "Other companies will not be able to see or use this stage.",
        default=lambda self:
            self.env["res.company"]._company_default_get("crm.stage"),
    )

class CrmLead(models.Model):
    _inherit = "crm.lead"
    def _stage_find(self, team_id=False, domain=[], order='sequence, id', limit=1):
        """ override the function """
        domain += [('company_ids','in',[self.env.user.company_id.id])]
        return super(CrmLead, self)._stage_find(team_id=team_id, domain=domain, order=order, limit=limit)

    def action_send_email_to_customer(self):
        """
        Sends an email to the customer using a specific email template.
        """
        self.ensure_one()
        template = self.env.ref('crm_stage_multi_company_arxi.email_template_pipeline_customer')
        outgoing_mail_server_id = self.env['ir.mail_server'].search([], order='sequence asc', limit=1)
        
        ctx = {
                'default_model': 'crm.lead',
                'default_res_ids': [self.id],
                'default_use_template': bool(template),
                'default_template_id': template.id,
                'default_composition_mode': 'comment', # or 'comment' to add it to the chatter
                
                'default_mail_server_id': outgoing_mail_server_id.id or False,
                'default_force_send': True,
                'default_use_default_to': False,
                'default_email_to': self.partner_id and self.partner_id.email_formatted or False,
        }
        
        self.with_context(ctx).message_post_with_source(
            template,
            subtype_xmlid='mail.mt_comment',
        )
        return True
