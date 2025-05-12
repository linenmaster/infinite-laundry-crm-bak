# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cal_microsoft_client_id = fields.Char("Microsoft Client_id", config_parameter='microsoft_calendar_client_id', default='')
    cal_microsoft_client_secret = fields.Char("Microsoft Client_key", config_parameter='microsoft_calendar_client_secret', default='')
    cal_microsoft_sync_paused = fields.Boolean("Microsoft Synchronization Paused", config_parameter='microsoft_calendar_sync_paused',
        help="Indicates if synchronization with Outlook Calendar is paused or not.")
    custom_module_outlook_calendar = fields.Boolean(
        string='Allow the users to synchronize their calendar  with Google Calendar', config_parameter='custom_module_outlook_calendar')
    outlook_start_date = fields.Datetime(string='Start Date', config_parameter='outlook_start_date',)

    @api.onchange('outlook_start_date')
    def _check_start_date_change(self):
        if self.outlook_start_date:
            stored_start_date = self.env['ir.config_parameter'].sudo().get_param('outlook_start_date')
            if stored_start_date:
                stored_start_date = fields.Datetime.from_string(stored_start_date)
                if self.outlook_start_date > stored_start_date:
                    raise UserError(
                        "You can only set the date to an earlier or the same date. You cannot set it to a future date.")

