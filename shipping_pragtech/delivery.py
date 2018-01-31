# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields,osv

class delivery_carrier(osv.osv):
    _inherit = "delivery.carrier"
    _columns = {
        'service_code': fields.char('Service Code', size=100, help="Code used as input to API"),
        'service_output': fields.char('Service Output', size=100, help="Code returned as output by API"),
        'container_usps' : fields.char('Container', size=100),
        'size_usps' : fields.char('Size', size=100),
        'first_class_mail_type_usps' : fields.char('First Class Mail Type', size=100),
        'is_ups' : fields.boolean('Is UPS', help="If the field is set to True, it will consider it as UPS service type."),
        'is_usps' : fields.boolean('Is USPS', help="If the field is set to True, it will consider it as USPS service type."),
        'is_fedex' : fields.boolean('Is FedEx', help="If the field is set to True, it will consider it as FedEx service type.")
    }
delivery_carrier()