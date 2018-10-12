# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Niyas Raphy(<http://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo.addons.web.controllers import main
from odoo.http import request
from odoo.exceptions import Warning
import odoo
import odoo.modules.registry
from odoo.tools.translate import _
from odoo import http, fields
from datetime import datetime, timedelta
import time
from pytz import timezone
import pytz

class Home(main.Home):

    @http.route('/web/login', type='http', auth="public")
    def web_login(self, redirect=None, **kw):
        main.ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID
        indiatm = pytz.timezone('Asia/Kolkata')
        values = request.params.copy()
        # system date is behind 1 day, handle it by adding 1 day
        current_datetime = (datetime.now() + timedelta(days=1)).replace(tzinfo=pytz.timezone('UTC')).astimezone(indiatm)
        current_time = datetime.strptime(current_datetime.strftime('%H:%M'), '%H:%M').time()
        print "cuurent date time=========",current_datetime
        current_day = current_datetime.weekday()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            ip_address = request.httprequest.environ['REMOTE_ADDR']
            print "ip address=============",ip_address
            if request.params['login']:
                user_rec = request.env['res.users'].sudo().search([('login', '=', request.params['login'])])
                if user_rec.allowed_ips:
                    ip_list = []
                    for rec in user_rec.allowed_ips:
                        ip_list.append(rec.ip_address)
                    if ip_address in ip_list:
                        if user_rec.allow_time:
                            for rec_time in user_rec.allow_time:

                                if rec_time.access_day and rec_time.access_start_time and rec_time.access_end_time:
                                    print "current_datetime=======",current_time
                                    print "==========",datetime.strptime(rec_time.access_start_time.strip(), '%H:%M').time()
                                    print "end=============",datetime.strptime(rec_time.access_end_time.strip(), '%H:%M').time()
                                    if (int(rec_time.access_day) == int(current_day) and
                                        datetime.strptime(rec_time.access_start_time.strip(), '%H:%M').time() <= current_time and
                                        datetime.strptime(rec_time.access_end_time.strip(), '%H:%M').time() >= current_time):
                                        uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                                        print "if============="
                                        if uid is not False:
                                            request.params['login_success'] = True
                                            if not redirect:
                                                redirect = '/web'
                                            return http.redirect_with_hash(redirect)
                                        request.uid = old_uid
                                        values['error'] = _("Wrong login/password")
                                    values['error'] = _("at this Time")
                    request.uid = old_uid
                    values['error'] = _("Not allowed to login from this IP") + ' ' + values.get('error','')
                elif user_rec.allow_time:
                    for rec_time in user_rec.allow_time:
                        if rec_time.access_day and rec_time.access_start_time and rec_time.access_end_time:
                            print "current_datetime=======",current_time
                            print "==========",datetime.strptime(rec_time.access_start_time.strip(), '%H:%M').time()
                            print "end=============",datetime.strptime(rec_time.access_end_time.strip(), '%H:%M').time()
                            if (int(rec_time.access_day) == int(current_day) and
                                        datetime.strptime(rec_time.access_start_time.strip(), '%H:%M').time() <= current_time and
                                        datetime.strptime(rec_time.access_end_time.strip(), '%H:%M').time() >= current_time):
                                uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                                print "if============="
                                if uid is not False:
                                    request.params['login_success'] = True
                                    if not redirect:
                                        redirect = '/web'
                                    return http.redirect_with_hash(redirect)
                                request.uid = old_uid
                                values['error'] = _("Wrong login/password")
                            values['error'] = _("Your are not allowed to login at this Time")
                else:
                    uid = request.session.authenticate(request.session.db, request.params['login'],
                                                       request.params['password'])
                    if uid is not False:
                        request.params['login_success'] = True
                        if not redirect:
                            redirect = '/web'
                        return http.redirect_with_hash(redirect)
                    request.uid = old_uid
                    values['error'] = _("Wrong login/password")

        return request.render('web.login', values)
