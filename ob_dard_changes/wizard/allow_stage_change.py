# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models,fields ,api
from datetime import datetime,time

class sale_order_allow_wizard(models.TransientModel):
	_inherit = 'sale.order.allow.wizard'


	@api.one
	def update_sale_stage_change_info(self):
		res = super(sale_order_allow_wizard, self).update_sale_stage_change_info()
		sale_obj = self.env['so.tracking']
		message_obj = self.env['mail.message']

		if self._context.get('stage_id'):
			stage_id = self._context.get('stage_id')
		else:
			stage_id = self._context.get('so_stage_id')
		if stage_id:
			if self._context.get('track_id'):
				sale_obj.browse(self._context.get('track_id')).write({'stage_id':stage_id})
				values = {}
				if self.message_allow:
					values.update({
					    'model': 'sale.order',
	                    'res_id': self._context.get('sale_order_id', False),
	                    'body' : self.message_allow,
	                    'parent_id': False,
		            })
					message_obj.create(values)
		return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
