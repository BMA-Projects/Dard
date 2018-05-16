# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, fields, api, _

class res_partner(models.Model):
    _inherit = "res.partner"

    _defaults = {
        'user_id': False,
    }

    attention = fields.Char('Attention')
    old_customer_number = fields.Char('Old Customer/Supplier #', copy=False)

    customer_state = fields.Selection([('draft', 'Draft')], default='draft')


#     @api.multi
#     def write(self, vals):
#         print '_____vals______1_____',vals
#         if vals.get('parent_id'):
#             parent_browse = self.browse(vals.get('parent_id'))
#             if parent_browse.customer == True:
#                 print '____self.type____',self.type
#                 if self.type == 'delivery':
#                     vals.update({'customer': False})
#                 else:
#                     vals.update({'customer': True})
#             if parent_browse.supplier == True:
#                 if self.type == 'delivery':
#                     vals.update({'supplier': False})
#                 else:
#                     vals.update({'supplier': True})
#         print '_____vals____',vals
#         return vals
    
    @api.model
    def create(self, vals):
        if vals.get('parent_id'):
            parent_browse = self.browse(vals.get('parent_id'))
            if parent_browse.customer == True:
                if vals.get('type') == 'delivery':
                    vals.update({'customer': False})
                else:
                    vals.update({'customer': True})
            if parent_browse.supplier == True:
                if vals.get('type') == 'delivery':
                    vals.update({'supplier': False})
                else:
                    vals.update({'supplier': True})
        if vals.has_key('is_company') and not vals.get('is_company'):
            vals.update({'old_customer_number': False})
        return super(res_partner, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.has_key('is_company') and not vals.get('is_company'):
            vals.update({'old_customer_number': False})
        res = super(res_partner, self).write(vals)
        return res
    
    
    def onchange_address_type(self, cr, uid, ids, parent_id, customer, supplier, type, context=None):
        dic = {}
        if parent_id:
            parent_browse = self.browse(cr, uid, parent_id)
            if parent_browse.customer == True:
                if type == 'delivery':
                    dic = {'customer': False}
                else:
                    dic = {'customer': True}
            if parent_browse.supplier == True:
                if type == 'delivery':
                    dic = {'supplier': False}
                else:
                    dic = {'supplier': True}
                
        return {'value': dic}

    @api.model
    def default_get(self,fields=None):
        res = super(res_partner,self).default_get(fields)
        if self._context.get('is_customer_shipped'):
            res.update({'customer': False})
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
