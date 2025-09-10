from odoo import models, tools


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _message_create(self, values_list):
        """Override to set reply_to for CRM leads based on company.crm_email."""
        crm_email = self.env.company.crm_email
        if crm_email:
            formatted_reply_to = tools.formataddr((self.env.user.name, crm_email))
            for values in values_list:
                if values.get("model") == "crm.lead":
                    values["reply_to"] = formatted_reply_to

        return super()._message_create(values_list)
