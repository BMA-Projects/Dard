# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

#from openerp.osv import osv, fields
#from openerp import tools
#from datetime import datetime
#from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv
# from openerp import models, fields, api, _
from datetime import datetime,date
from openerp.tools.translate import _
from openerp.exceptions import Warning
from openerp.osv.orm import setup_modifiers
from dateutil.relativedelta import relativedelta
from openerp import tools

class product_turn(osv.osv):
    _inherit = 'product.product'

    def get_qty_date(self, cr, uid, ids, last_year_date=None, location=False, context=None):
        if not context:context={}
        stock_his_obj = self.pool.get('stock.history')
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            if location:
                domain = [['date', '<=', last_year_date],['product_id','=',product.id],['location_id','=',location]]
            else:
                domain = [['date', '<=', last_year_date],['product_id','=',product.id]]
            lines = stock_his_obj.search(cr, uid, domain, context=context)
            lines_rec = stock_his_obj.browse(cr, uid, lines, context=context)
            prod_id =0
            my_qty = 0
            for line_rec in lines_rec:
                if prod_id != product.id:
                    my_qty = 0
                    prod_id = product.id
                my_qty += line_rec.quantity
            res.update({product.id:my_qty})
        return res
           
    def _product_turn_calc(self, cr, uid, ids,name, arg, context=None):
        result = dict.fromkeys(ids, 0.0)
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        if context.get('date_from'):
            to_date = datetime.strptime(context.get('date_from',False,),tools.DEFAULT_SERVER_DATETIME_FORMAT)
            to_date_inv = datetime.strftime(to_date,tools.DEFAULT_SERVER_DATETIME_FORMAT)
            last_year_date = datetime.strftime(to_date - relativedelta(years=1), tools.DEFAULT_SERVER_DATETIME_FORMAT)
            last_year_date_before = datetime.strftime(datetime.strptime(last_year_date,tools.DEFAULT_SERVER_DATETIME_FORMAT).replace(minute=59, hour=23, second=59, microsecond=0), tools.DEFAULT_SERVER_DATETIME_FORMAT)
            location = context.get('location_id',False)
            start_qty = self.get_qty_date(cr, uid, ids, last_year_date=last_year_date_before,location=location)
            end_qty = self.get_qty_date(cr, uid, ids, last_year_date=to_date_inv,location=location)
            
            for obj in self.browse(cr, uid, ids, context=context):
                sum = 0.0
                avg_inv = 0.0
                if location:
                    move_ids = move_obj.search(cr,uid,[('state','=','done'),('create_date','>',last_year_date_before),('create_date','<',to_date_inv),('picking_type_id.code', '=', 'outgoing'),('location_id','=', location),('product_id', '=', obj.id)],context=context)
                else:
                    move_ids = move_obj.search(cr, uid,[('state','=','done'),('create_date','>',last_year_date_before),('create_date','<',to_date_inv),('picking_type_id.code', '=', 'outgoing'),('product_id', '=', obj.id)],context=context)
                for move in move_obj.browse(cr, uid,move_ids, context=context):
                    
                    avg_inv =((start_qty.get(move.product_id.id)*(move.product_id.standard_price)) + ( end_qty.get(move.product_id.id)*(move.product_id.standard_price)))/2
                    if avg_inv >0 :
                        sum += (move.product_qty * move.product_id.standard_price)
                if sum > 0.0 and avg_inv > 0.0:
                    result[obj.id]=sum/avg_inv
                else:
                    result[obj.id]=0.0
        return result

    _columns = {
                'product_turn': fields.function(_product_turn_calc, type='float', string='Turns', help="Yearly product turn ",),
                'qty_available_turn' : fields.float('Quantity On Hand')
    }
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
