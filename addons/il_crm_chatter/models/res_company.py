from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """ Inherit the base settings to add a counter of failed email + configure
    the alias domain. """
    _inherit = 'res.config.settings'

    mail_reply_to = fields.Char(
        config_parameter='il_crm_chatter.mail_reply_to',
        help="Set default reply-to.",
    )