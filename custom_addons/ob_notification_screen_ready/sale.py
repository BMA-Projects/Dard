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

class sale_order(osv.osv):
    
    _inherit = "sale.order"

    def copy(self, cr, uid, id, default=None, context=None):
        if not context:context = {}
        sale_line_obj = self.pool.get('sale.order.line')
        line_default = {
            'is_screen_ready': False,
            'is_notification_sent': False,
        }
        new_id = super(sale_order, self).copy(cr, uid, id, default, context=context)
        need_update_id = sale_line_obj.search( cr, uid, [('order_id','=',new_id)], context = context)
        sale_line_obj.write(cr, uid, need_update_id, line_default, context=context)
        return new_id


class sale_order_line(osv.osv):

    _inherit = "sale.order.line"
    
    def set_screens_are_ready(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'is_screen_ready':True},context=context)
        return {}
    
    
    def get_mrp_manager_emails(self, cr, uid, ids, field, arg, context=None):
        emails = []
        manager_group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mrp', 'group_mrp_manager')[1]
        user_group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mrp', 'group_mrp_user')[1]
        group_obj = self.pool.get('res.groups')
        for group_rec in group_obj.browse(cr, uid, [manager_group_id,user_group_id], context=context):
            for user in group_rec.users:
                if user.email:
                    emails.append(user.email)
        res = {}
        emails = ','.join(i for i in emails)
        for id in ids:
            res[id] = emails
        return res
        
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        value = {}
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        if product:
            product_type_2 = self.pool.get("product.product").browse(cr, uid, product, context=context).type
            if res.get('value',False):
                res.get('value').update({'product_type_2':product_type_2})
            else:
                res = {'value': {'product_type_2':product_type_2}}
        return res
        
    _columns = {
        'product_type_2' : fields.char("Product Type"),
        'is_screen_ready' : fields.boolean('Screens are ready',help='This will send an E-mail to the Current login User and Manufacturing Manager(s) that screens are ready.'),
        'is_notification_sent' : fields.boolean('Is notification Sent'),
        'mrp_manager_mails' : fields.function(get_mrp_manager_emails,type="char",string='MRP Manager Emails'),
    }
    
    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        id = super(sale_order_line, self).create(cr, uid, vals, context=context)
        if vals.get('is_screen_ready',False):
            if self.send_mail(cr, uid, [id], context=context):
                self.write(cr, uid, id, {'is_notification_sent': True}, context=context)
            else:
                raise osv.except_osv(_('Sending Mail for Notify Screens are ready !'), _('Unable to send mail. Please contact your Administrator.'))
        return id
    
    def send_mail(self, cr, uid, ids, context=None):
        email_temp_obj = self.pool.get('email.template')
        mail_mail_obj = self.pool.get('mail.mail')
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ob_notification_screen_ready', 'email_template_edi_notification_screen_ready')[1]
        msg_id = email_temp_obj.send_mail(cr, uid, template_id, ids[0], force_send=False, context=context)
        vals = {
            'auto_delete' : True,
        }
        mail_mail_obj.write( cr, uid, [msg_id], vals, context = context)
        mail_mail_obj.send( cr, uid, [msg_id], context = context)
        mail_send_id = mail_mail_obj.search( cr, uid, [('id','=',msg_id)], context = context)
        res = True
        if mail_send_id:
            res = False
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}
        res = super(sale_order_line, self).write(cr, uid, ids, vals, context=context)
        if vals.get('is_screen_ready',False):
            cur_rec = self.browse(cr, uid, ids, context=context)[0]
            if not cur_rec.is_notification_sent:
                if self.send_mail(cr, uid, ids, context=context):
                    self.write(cr, uid, ids, {'is_notification_sent': True}, context=context)
                else:
                    raise osv.except_osv(_('Sending Mail for Notify Screens are ready !'), _('Unable to send mail. Please contact your Administrator.'))
        return res