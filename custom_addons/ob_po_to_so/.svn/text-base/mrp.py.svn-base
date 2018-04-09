# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import osv
from openerp.tools.translate import _
from openerp import tools
from openerp import models, fields, api, _

class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    sale_id = fields.Many2one('sale.order', 'Sale Order',readonly=1, invisible=1, copy=False)
    so_name = fields.Char('Sale Order',size=64, help="Sale Order reference number",readonly=1,copy=False)

    @api.model
    def create(self, values):
        res =  super(mrp_production, self).create(values)
        sale_obj = self.env['sale.order']
        sale_line_obj = self.env['sale.order.line']
        name = self.browse(res.id).name
        partner_name = None
        origin = values.get('origin','')
        origin = origin.split(':')
        if origin:
            sale_id = sale_obj.search([('name','ilike', origin[0])])
#             sol_data = sale_line_obj.search([('order_id','=',sale_id.id),('product_id','=',values.get('product_id'))])
#             sol_data.write({'mo_ref':res.name})
            if sale_id:
                so_name = sale_id.name
                res.write({'so_name' : so_name,})
        return res