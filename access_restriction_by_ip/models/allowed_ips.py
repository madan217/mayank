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
from odoo import models, fields, api
import time


class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    allowed_ips = fields.One2many('allowed.ips', 'users_ip', string='IP')
    allow_time = fields.One2many('allowed.time', 'user_id', string='Access Time')

    @api.model
    def create(self, vals):
        res = super(ResUsersInherit, self).create(vals)
        alltimeObj = self.env['allowed.time']
        if res:
            for r in range(7):
                alltimeObj.create({
                    'user_id' : res.id,
                    'access_day' : str(r)
                    })
        return res


class AllowedIPs(models.Model):
    _name = 'allowed.ips'

    users_ip = fields.Many2one('res.users', string='IP')
    ip_address = fields.Char(string='Allowed IP')

class AllowedTime(models.Model):
    _name = 'allowed.time'

    user_id = fields.Many2one('res.users', string='User')
    access_day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')], string='Day',
        )
    access_start_time = fields.Char(string='Start Time')
    access_end_time = fields.Char('End Time')