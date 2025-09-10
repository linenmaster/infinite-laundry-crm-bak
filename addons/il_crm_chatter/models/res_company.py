from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    crm_email = fields.Char(string="CRM Email")
