# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################

from openerp.osv import osv, fields

class account_journal(osv.osv):
	_inherit = 'account.journal'
	_columns = {
		'cc_processing': fields.boolean('CC Processing', help="Allow credit card processing in this journal."),
		'cc_refunds': fields.boolean('CC Refunds', help="Allow credit card refunds in this journal."),
	}