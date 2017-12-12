# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _
import re
from openerp import models, fields, api, _
from openerp import SUPERUSER_ID


class res_partner(models.Model):

    _inherit = "res.partner"

    cust_number = fields.Char('Number',size=32)

    def copy(self, cr, uid, ids, default=None, context=None):
        if not context:
            context={}
        if default is None:
            default = {}
        default.update({'cust_number':False})
        return super(res_partner,self).copy(cr, uid, ids, default=default,context=context)

    _sql_constraints = [
        ('customer_number_uniq', 'unique(cust_number)', 'The customer number must be unique.!')
    ]
    
# This method commented because in all default report (company,customer) address not print properly.
#     def name_get(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         if isinstance(ids, (int, long)):
#             ids = [ids]
#         if not len(ids):
#             return []
#         def _name_get(d):
#             name = d.get('name','')
#             cust_number = d.get('cust_number',False)
#             if cust_number:
#                 name = '[%s] %s' % (cust_number,name)
#             return (d['id'], name)
# 
#         result = []
#         for customer in self.browse(cr, uid, ids, context=context):
#             mydict = {
#                       'id': customer.id,
#                       'name': customer.name,
#                       'cust_number': customer.cust_number,
#                       }
#             result.append(_name_get(mydict))
#         return result
 

#     def name_get(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         if isinstance(ids, (int, long)):
#             ids = [ids]
#         if not len(ids):
#             return []
#  
#         def _name_get(d):
#             name = d.get('name','')
#             cust_number = d.get('cust_number',False)
#             if cust_number:
#                 name = '[%s] %s' % (cust_number,name)
#             return (d['id'], name)
#  
#         res = []
#         for record in self.browse(cr, uid, ids, context=context):
#             name = record.name
#             if record.parent_id and not record.is_company:
#                 name = "%s, %s" % (record.parent_name, name)
#             if context.get('show_address_only'):
#                 name = self._display_address(cr, uid, record, without_company=True, context=context)
#             if context.get('show_address'):
#                 name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
#             name = name.replace('\n\n','\n')
#             name = name.replace('\n\n','\n')
#             if context.get('show_email') and record.email:
#                 name = "%s <%s>" % (name, record.email)
#             res.append((record.id, name))
#             mydict = {
#                       'id': record.id,
#                       'name': record.name,
#                       'cust_number': record.cust_number,
#                       }
#             res.append(_name_get(mydict))
#         return res

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [('cust_number','=',name)]+ args, limit=limit, context=context)
            if not ids:
                ids = set()
                ids.update(self.search(cr, user, args + [('cust_number',operator,name)], limit=limit, context=context))
                if not limit or len(ids) < limit:
                    ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))
                ids = list(ids)
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('cust_number','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr,user, args, limit=limit, context=context)
        result = super(res_partner,self).name_get(cr, SUPERUSER_ID, ids, context=context)
        return result
