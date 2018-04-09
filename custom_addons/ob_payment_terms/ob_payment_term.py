# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time

import openerp
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp import models, fields, api, _
from openerp.tools.float_utils import float_round as round

class account_payment_term(osv.osv):
    _inherit = 'account.payment.term'

    prepay_payment = fields.Boolean(string="Prepay Payment Term")

class sale_order(osv.osv):
    _inherit = 'sale.order'

    payment_green = fields.Boolean(string="Prepay Payment Term")

    @api.model
    def create(self, values):
        if values.get('payment_term'):
        	final_vals = self.env['account.payment.term'].browse([values.get('payment_term')]).prepay_payment
        	if final_vals == True:
        		values.update({'payment_green':True})
        return super(sale_order, self).create(values)

    @api.multi
    def write(self,values):
        if values.get('payment_term'):
            final_vals = self.env['account.payment.term'].browse([values.get('payment_term')]).prepay_payment
            if final_vals == True:
                values.update({'payment_green':True})
            else:
                values.update({'payment_green':False})
        return super(sale_order, self).write(values)

class res_partner(osv.osv):
    _inherit = 'res.partner'

    payment_green = fields.Boolean(string="Prepay Payment Term")


    @api.model
    def create(self, values):
        if values.get('property_payment_term'):
        	final_vals = self.env['account.payment.term'].browse([values.get('property_payment_term')]).prepay_payment
        	if final_vals == True:
        		values.update({'payment_green':True})
        return super(res_partner, self).create(values)

    @api.multi
    def write(self,values):
    	if values.get('property_payment_term'):
    		final_vals = self.env['account.payment.term'].browse([values.get('property_payment_term')]).prepay_payment
    		if final_vals == True:
    			values.update({'payment_green':True})
    		else:
    			values.update({'payment_green':False})
    	return super(res_partner, self).write(values)