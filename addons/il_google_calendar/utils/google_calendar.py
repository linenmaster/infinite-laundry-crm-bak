# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from uuid import uuid4
import requests
import json
import logging

from odoo import fields
from odoo.addons.il_google_calendar.utils.google_event import GoogleEvent
from odoo.addons.google_account.models.google_service import TIMEOUT


_logger = logging.getLogger(__name__)

def requires_auth_token(func):
    def wrapped(self, *args, **kwargs):
        if not kwargs.get('token'):
            raise AttributeError("An authentication token is required")
        return func(self, *args, **kwargs)
    return wrapped

class InvalidSyncToken(Exception):
    pass

class GoogleCalendarService():

    def __init__(self, google_service):
        self.google_service = google_service

    @requires_auth_token
    def get_events(self, token=None, event_id=None, start_date=None, timeout=TIMEOUT):
        ICP = self.google_service.env['ir.config_parameter'].sudo()
        calendar_id = ICP.get_param('google_calendar_account_id', default='primary')

        base_url = f"/calendar/v3/calendars/{calendar_id}/events"
        headers = {'Content-type': 'application/json'}
        params = {'access_token': token}

        if event_id:
            url = f"{base_url}/{event_id}"
        else:
            url = base_url
            if start_date:
                params['timeMin'] = start_date
                _logger.info(f"Syncing events by date: {start_date} ")
            else:
                # fallback to default date range of ±365 days
                day_range = int(ICP.get_param('google_calendar.sync.range_days', default=365))
                now = fields.Datetime.now()
                params['timeMin'] = now.isoformat() + 'Z'
                params['timeMax'] = fields.Datetime.add(now, days=day_range).isoformat() + 'Z'
                _logger.info("No date range provided, defaulting to %s days forward", day_range)

        try:
            status, data, time = self.google_service._do_request(url, params, headers, method='GET', timeout=timeout)
        except requests.HTTPError as e:
            raise e  # let upper logic handle it cleanly

        if event_id:
            return GoogleEvent([data]), None, ()

        # Paginated results
        events = data.get('items', [])
        next_page_token = data.get('nextPageToken')
        while next_page_token:
            params.update({'pageToken': next_page_token})
            status, data, time = self.google_service._do_request(url, params, headers, method='GET', timeout=timeout)
            events += data.get('items', [])
            next_page_token = data.get('nextPageToken')

        default_reminders = data.get('defaultReminders')
        return GoogleEvent(events), None, default_reminders

    @requires_auth_token
    def insert(self, values, token=None, timeout=TIMEOUT, callback_method=None):
        send_updates = self.google_service._context.get('send_updates', True)
        url = "/calendar/v3/calendars/primary/events?conferenceDataVersion=1&sendUpdates=%s" % ("all" if send_updates else "none")
        headers = {'Content-type': 'application/json', 'Authorization': 'Bearer %s' % token}
        if not values.get('id'):
            values['id'] = uuid4().hex
        request_values = self.google_service._do_request(url, json.dumps(values), headers, method='POST', timeout=timeout)
        # Execute optional callback function using the returned values from insertion. TODO (gdpf) refactor in master.
        if callable(callback_method):
            callback_method(request_values, values)
        return values['id']

    @requires_auth_token
    def patch(self, event_id, values, token=None, timeout=TIMEOUT):
        url = "/calendar/v3/calendars/primary/events/%s?sendUpdates=all" % event_id
        headers = {'Content-type': 'application/json', 'Authorization': 'Bearer %s' % token}
        self.google_service._do_request(url, json.dumps(values), headers, method='PATCH', timeout=timeout)

    @requires_auth_token
    def delete(self, event_id, token=None, timeout=TIMEOUT):
        url = "/calendar/v3/calendars/primary/events/%s?sendUpdates=all" % event_id
        headers = {'Content-type': 'application/json'}
        params = {'access_token': token}
        # Delete all events from recurrence in a single request to Google and triggering a single mail.
        # The 'singleEvents' parameter is a trick that tells Google API to delete all recurrent events individually,
        # making the deletion be handled entirely on their side, and then we archive the events in Odoo.
        is_recurrence = self.google_service._context.get('is_recurrence', True)
        if is_recurrence:
            params['singleEvents'] = 'true'
        try:
            self.google_service._do_request(url, params, headers=headers, method='DELETE', timeout=timeout)
        except requests.HTTPError as e:
            # For some unknown reason Google can also return a 403 response when the event is already cancelled.
            if e.response.status_code not in (410, 403):
                raise e
            _logger.info("Google event %s was already deleted" % event_id)


    #################################
    ##  MANAGE CONNEXION TO GMAIL  ##
    #################################


    def is_authorized(self, user):
        return bool(user.sudo().google_calendar_rtoken)

    def _get_calendar_scope(self, RO=False):
        readonly = '.readonly' if RO else ''
        return 'https://www.googleapis.com/auth/calendar%s' % (readonly)

    def _google_authentication_url(self, from_url='http://www.odoo.com'):
        state = {
            'd': self.google_service.env.cr.dbname,
            's': 'calendar',
            'f': from_url
        }
        base_url = self.google_service._context.get('base_url') or self.google_service.get_base_url()
        return self.google_service._get_authorize_uri(
            'calendar',
            self._get_calendar_scope(),
            base_url + '/google_account/authentication',
            state=json.dumps(state),
            approval_prompt='force',
            access_type='offline'
        )

    def _can_authorize_google(self, user):
        return user.has_group('base.group_erp_manager')
