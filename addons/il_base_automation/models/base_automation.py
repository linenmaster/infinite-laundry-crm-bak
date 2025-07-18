# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
import logging
import traceback
from collections import defaultdict
from uuid import uuid4

from dateutil.relativedelta import relativedelta

from odoo import _, api, exceptions, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import safe_eval
from odoo.http import request

_logger = logging.getLogger(__name__)

class BaseAutomation(models.Model):
    _inherit = 'base.automation'

    @api.model
    def _default_users(self):
        # Example: Set default to current user and another specific user
        current_user = self.env.user
        # other_user = self.sudo().env.ref('base.group_system')  # Replace with actual user XML ID or logic
        return [(6, 0, [current_user.id])]#, other_user.id

    user_ids = fields.Many2many("res.users", relation="base_automation_users_rel",
        string="Allowed Users", default=lambda self: self._default_users())
    
    # user_ids = fields.Many2many("res.users", relation="base_automation_users_rel",
    #     string="Allowed Users")

DEFAULT_PYTHON_CODE = """# Available variables:
#  - env: environment on which the action is triggered
#  - model: model of the record on which the action is triggered; is a void recordset
#  - record: record on which the action is triggered; may be void
#  - records: recordset of all records on which the action is triggered in multi-mode; may be void
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - float_compare: utility function to compare floats based on specific precision
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - _logger: _logger.info(message): logger to emit messages in server logs
#  - UserError: exception class for raising user-facing warning messages
#  - Command: x2many commands namespace
# To return an action, assign: action = {...}\n\n\n\n"""
class IrActionsServer(models.Model):
    _inherit = 'ir.actions.server'

    #overridding python_code field for sale_manager
    code = fields.Text(string='Python Code', groups='base.group_system,sales_team.group_sale_manager',
                       default=DEFAULT_PYTHON_CODE,
                       help="Write Python code that the action will execute. Some variables are "
                            "available for use; help about python expression is given in the help tab.")
