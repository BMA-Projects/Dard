# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp.osv import fields, osv, orm

class mail_thread(osv.AbstractModel):
	_inherit = 'mail.thread'

	def create(self, cr, uid, values, context=None):
		ctx = context.copy()
		ctx.update({'mail_create_nosubscribe':True})
		thread_id = super(mail_thread, self).create(cr, uid, values, context=ctx)
		return thread_id

	def message_auto_subscribe(self, cr, uid, ids, updated_fields, context=None, values=None):
		return True
	
	