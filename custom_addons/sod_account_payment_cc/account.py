# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################

from openerp.osv import osv, fields


class account_payment_term(osv.osv):
	_inherit = 'account.payment.term'
	_columns = {
		'is_cc_term': fields.boolean('CC Term?'),
	}