# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as dt
from lxml import etree
from openerp.http import request

class purchase_order(models.Model):

    _inherit = 'purchase.order'
    
    def do_merge(self, cr, uid, ids, context=None):
        if not context: context={}
        sale_obj = self.pool.get('sale.order')
        sol_object = self.pool.get('sale.order.line')
        purchase_line_obj = self.pool.get('purchase.order.line')
        res = super(purchase_order,self).do_merge(cr, uid, ids, context=context)
        if res:
            pol_ids = purchase_line_obj.search(cr, uid, [('order_id','=',res.keys()[0])])
            for po_data in self.browse(cr, uid, res.keys()[0], context=context):
                for po_line in po_data.order_line:
                    if po_line.so_ref:
                        so_ids = sale_obj.search(cr, uid, [('name','=',po_line.so_ref)],context=context)
                        for sale_data in sale_obj.browse(cr, uid, so_ids, context=context):
                            for sol in sale_data.order_line:
                                if sol.po_ref == po_data.name:
                                    sol_object.write(cr, uid, sol.id, {'po_ref':po_data.name},context=context)
                        sol_ids = sol_object.search(cr, uid, [('po_line_ref','=',po_line.name),('name','=',po_line.so_line_ref)])
        return res