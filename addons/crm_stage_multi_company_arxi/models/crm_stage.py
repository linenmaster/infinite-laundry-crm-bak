

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
    def _stage_find(self, team_id=False, domain=None, order='sequence, id', limit=1):
        """ override the function """
        res = super(CrmLead, self)._stage_find(team_id=team_id, domain=domain, order=order, limit=limit)
        domain += [('company_ids','in',[self.env.user.company_id.id])]
        return self.env['crm.stage'].search(domain, order=order, limit=limit)