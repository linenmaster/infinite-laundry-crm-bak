from odoo import models, tools


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _message_create(self, values_list):
        """Override to set reply_to for CRM leads based on ir config paramater mail_reply_to."""
        mail_reply_to = self.env["ir.config_parameter"].sudo().get_param(
            "il_crm_chatter.mail_reply_to")
        if mail_reply_to:
            formatted_reply_to = tools.formataddr((self.env.user.name, mail_reply_to))
            for values in values_list:
                if values.get("model") == "crm.lead":
                    values["reply_to"] = formatted_reply_to

        return super()._message_create(values_list)
