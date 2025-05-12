# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cal_client_id = fields.Char("Client_id", config_parameter='google_calendar_client_id', default='')
    cal_client_secret = fields.Char("Client_key", config_parameter='google_calendar_client_secret', default='')
    cal_sync_paused = fields.Boolean("Google Synchronization Paused", config_parameter='google_calendar_sync_paused',
        help="Indicates if synchronization with Google Calendar is paused or not.")
    custom_module_google_calendar = fields.Boolean(
        string='Allow the users to synchronize their calendar  with Google Calendar', config_parameter='custom_module_google_calendar')
    start_date = fields.Datetime(string='Start Date', config_parameter='google_start_date',)

    @api.onchange('start_date')
    def _check_google_start_date(self):
        if self.start_date:
            # Get the original stored value of the start_date
            stored_start_date = self.env['ir.config_parameter'].sudo().get_param('google_start_date')

            if stored_start_date:
                stored_start_date = fields.Datetime.from_string(stored_start_date)

                # Check if the new date is later than the stored date
                if self.start_date > stored_start_date:
                    raise UserError(
                        "You can only set the date to an earlier or the same date. You cannot set it to a future date.")

