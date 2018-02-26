# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, fields, api, _
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import Warning
from datetime import date

class res_users(models.Model):
    _inherit = "res.users"


    is_salesperson = fields.Boolean(string="Is Salesperson")
#     check_list = fields.One2many('generate.ticket.check','user_id', 'Check List')
    
    
class mrp_production(models.Model):
    _inherit = "mrp.production"

    _defaults = {
        'user_id': False,
    }

class account_invoices(models.Model):
    _inherit = "account.invoice"

    _defaults = {
        'user_id': False,
    }

class sale_order(models.Model):
    _inherit = "sale.order"

    order_processor = fields.Many2one('res.users', string="Order Processor")

    _defaults = {
        'user_id': False,
        'in_hand_date_visible': True,
        'order_processor': lambda obj, cr, uid, context: uid,
    }

    @api.model
    def default_get(self, fields_list):
        values = super(sale_order, self).default_get(fields_list)
        values.update({'ship_dt': datetime.today().date().strftime('%Y-%m-%d')})
        return values

    @api.model
    def create(self, vals):
        if vals.get('ship_dt', False):
            # ship_dt = vals.get('ship_dt', False)
            # date_order = datetime.now()
            # date_order_new = date_order.date()

            # if isinstance(ship_dt, str):
            #     ship_dt = datetime.strptime(ship_dt, DEFAULT_SERVER_DATE_FORMAT)
            #     ship_dt_new = ship_dt.date()
            #     if ship_dt_new < date_order_new:
            #         raise Warning(_('Ship Date should not be before the Current Date'))
            return super(sale_order, self).create(vals)
        else:
            vals.update({
                'ship_dt': str(date.today() + timedelta(days=1)),
                'in_hand_date': str(date.today() + timedelta(days=1))
            })
            return super(sale_order, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('ship_dt', False):
            ship_dt = vals.get('ship_dt', False)
            date_order_new = datetime.strptime(self.create_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
            if isinstance(ship_dt, str):
                ship_dt = ship_dt.split(' ') and ship_dt.split(' ')[0]
                ship_dt = datetime.strptime(ship_dt, DEFAULT_SERVER_DATE_FORMAT)
                ship_dt_new = ship_dt.date()
                if ship_dt_new < date_order_new:
                    raise Warning(_('Ship Date cannot be empty, also should not be before the Order Creation Date'))
        result = super(sale_order, self.with_context(by_pass=True)).write(vals)
        return result

# class res_partner(models.Model):
#     _inherit = "res.partner"

#     _defaults = {
#         'user_id': False,
#     }
    
    
    
# #     @api.multi
# #     def write(self, vals):
# #         print '_____vals______1_____',vals
# #         if vals.get('parent_id'):
# #             parent_browse = self.browse(vals.get('parent_id'))
# #             if parent_browse.customer == True:
# #                 print '____self.type____',self.type
# #                 if self.type == 'delivery':
# #                     vals.update({'customer': False})
# #                 else:
# #                     vals.update({'customer': True})
# #             if parent_browse.supplier == True:
# #                 if self.type == 'delivery':
# #                     vals.update({'supplier': False})
# #                 else:
# #                     vals.update({'supplier': True})
# #         print '_____vals____',vals
# #         return vals
    
#     @api.model
#     def create(self, vals):
        
#         if vals.get('parent_id'):
#             parent_browse = self.browse(vals.get('parent_id'))
#             if parent_browse.customer == True:
#                 if vals.get('type') == 'delivery':
#                     vals.update({'customer': False})
#                 else:
#                     vals.update({'customer': True})
#             if parent_browse.supplier == True:
#                 if vals.get('type') == 'delivery':
#                     vals.update({'supplier': False})
#                 else:
#                     vals.update({'supplier': True})
        
#         return super(res_partner, self).create(vals)
    
    
#     def onchange_address_type(self, cr, uid, ids, parent_id, customer, supplier, type, context=None):
#         dic = {}
#         if parent_id:
#             parent_browse = self.browse(cr, uid, parent_id)
#             if parent_browse.customer == True:
#                 if type == 'delivery':
#                     dic = {'customer': False}
#                 else:
#                     dic = {'customer': True}
#             if parent_browse.supplier == True:
#                 if type == 'delivery':
#                     dic = {'supplier': False}
#                 else:
#                     dic = {'supplier': True}
                
#         return {'value': dic}
        

#NOTE: Commented because purchase requisition no more required in  Project:DARD
# class purchase_requisition(models.Model):
#     _inherit = "purchase.requisition"

#     _defaults = {
#         'user_id': False,
#     }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
