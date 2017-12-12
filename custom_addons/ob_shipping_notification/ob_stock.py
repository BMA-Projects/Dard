# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import osv,fields


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def notify_shipping(self, cr, uid, origin, context=None):
        if context is None: context = {}
        group_obj = self.pool.get('res.groups')
        user_obj = self.pool.get('res.users')
        tmpl_obj = self.pool.get('email.template')
        sale_obj = self.pool.get('sale.order')
        
        if context.get('active_id', False):
            delivery_id = context['active_id']
            delivery = self.browse(cr, uid, delivery_id, context=context)
            #Check payment is done
            if delivery.state == 'assigned':
                sale_id = sale_obj.search(cr, uid, [('name','=',origin)])
                if sale_id:# and delivery_id:
                    sale = sale_obj.browse(cr, uid, sale_id[0], context=context) or False
                    #Check 'Create Invoice' is 'Before Delivery' or 'On Demand'
                    if sale.order_policy == 'prepaid' or (sale.order_policy == 'manual' and sale.invoiced and not sale.shipped):
                        category_id = self.pool.get('ir.module.category').search(cr, uid, [('name','=','Warehouse')])
                        manager_ids = group_obj.search(cr, uid, [('name','=', 'Manager'),('category_id','in',category_id)])
                        user_ids = group_obj.browse(cr, uid, manager_ids, context=context)[0].users
                        email_to = ''
                        for user_id in user_ids:
                            if user_id.email:
                                email_to = email_to and email_to + ',' + user_id.email or email_to + user_id.email
                        template = delivery.state == 'assigned' and 'Ready to Deliver Shipping Notification Template'
                        tmpl_ids = tmpl_obj.search(cr, uid, [('name','=',template)])
                        if tmpl_ids:
                            tmpl_obj.write(cr, uid, tmpl_ids[0], {'email_to':email_to}, context=context)
                            #return self.pool.get('email.template').send_mail(cr, uid, tmpl_ids[0], delivery_id, True)
                            return False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: