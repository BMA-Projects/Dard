# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import osv, fields
from openerp import _
from openerp.exceptions import Warning

class res_partner(osv.osv):

    _inherit = "res.partner"
 	
    def parnter_create_notification(self, cr, uid, obj,  context=None):
        if context.get('from_create',False):
            group_obj = self.pool.get('res.groups')
            user_obj = self.pool.get('res.users')
            if obj.customer or obj.supplier:
                manager_ids = group_obj.search(cr, uid, [('name','=', 'Financial Manager')])
                user_ids = group_obj.browse(cr, uid, manager_ids, context=context)[0].users
                email = []
                for id in user_ids:
                    email.append(id.email)
                email_to = ','.join(str(e) for e in email)
                tmpl_obj = self.pool.get('email.template')
                tmpl_ids = tmpl_obj.search(cr, uid, [('name','=','Partner E-mail Template')])
                if tmpl_ids:
                    tmpl_obj.write(cr, uid, tmpl_ids[0], {'email_to':email_to}, context=context)
                    self.pool.get('email.template').send_mail(cr, uid, tmpl_ids[0], obj.id)
        return {}
    
    def create(self, cr, uid, vals, context=None):
        if not context:context={}
        context = context.copy()
        context.update({'from_create':True})
        partner_id = super(res_partner, self).create(cr, uid, vals, context=context)
        return partner_id
    
