# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################

import base64
import logging
from openerp.osv import fields, osv, orm
from openerp import tools
from lxml import etree
import time
from openerp.tools.translate import _

class res_partner(orm.Model):
    _inherit = 'res.partner'  
    _columns = {
        'send_email': fields.boolean('Send Auto Email', help="Emails will be sent automatically"),}
    _defaults = {
        'send_email': True,
    }
class account_invoice(orm.Model):

    _inherit = 'account.invoice'
    _columns = {
        'send_email': fields.related('partner_id','send_email', readonly=True ,type='boolean',string='Send Auto Email'),}

class purchase_order(orm.Model):

    _inherit = 'purchase.order'
    _columns = {
        'send_email': fields.related('partner_id','send_email', readonly=True ,type='boolean',string='Send Auto Email'),}
        
class sale_order(orm.Model):

    _inherit = 'sale.order'
    _columns = {
        'send_email': fields.related('partner_id','send_email', readonly=True ,type='boolean',string='Send Auto Email'),}
        
class stock_picking(orm.Model):
    _inherit='stock.picking'
    _columns = {
        'send_email': fields.related('partner_id','send_email', readonly=True ,type='boolean',string='Send Auto Email'),}
        
class email_template(orm.Model):
    _name = "email.template"
    _inherit = 'email.template'
    _columns = {
        'auto_send': fields.boolean('Auto Send', help=" Auto Send on the template and it will be sent automatically"),}
    
    _defaults = {
        'auto_send': False,
    }

    def action_send_confirm(self, cr, uid, context=None):
        record_id=context.get('active_id')
        model=context.get('active_model')
        active_model = self.pool.get(model)

        if model=='account.invoice' and  active_model.browse(cr,uid,record_id,context=context).type in ('in_invoice','out_refund','in_refund'):
            return True
        if model=='account.voucher' and  active_model.browse(cr,uid,record_id,context=context).type=='payment':
            return True
        
        ir_model= self.pool.get('ir.model')
        mail_compose=self.pool.get('mail.compose.message')
        ir_attachment = self.pool.get('ir.attachment')
        ir_model_id = ir_model.search(cr, uid, [('model','=',model)])
        template_id=self.search(cr,uid,[('model_id','in',ir_model_id),('auto_send', '=',True)])
        
        record = active_model.browse(cr, uid, record_id, context=context)
        partner = record.partner_id or False
        email_to = partner.confirm_email or partner.email
        
        if model == 'sale.order' and template_id and email_to:
            self.write(cr, uid, template_id, {'email_to':email_to}, context=context)
        #make sure we need to send email for that partner and that the partner has email.
        record_send= partner.send_email and email_to
        if  record_send and template_id:
            values=mail_compose.generate_email_for_composer(cr,uid,template_id[0],record_id,context=context)
            values['attachment_ids']=[]
            data_attach={}
            for attach_fname, attach_datas in values.pop('attachments', []):
                data_attach = {
                        'name': attach_fname,
                        'datas': attach_datas,
                        'datas_fname': attach_fname,
                        'res_model': model,
                        'res_id':record_id,
                        'type': 'binary', 
                    }
                if data_attach:
                    values['attachment_ids'].append(ir_attachment.create(cr, uid, data_attach, context=context))
                    
            subtype = 'mail.mt_comment'
            is_log = context.get('mail_compose_log', False)
            if is_log:
                subtype = False
            
            self.send_mail(cr, uid, template_id, record_id, force_send=True, context=context)
            #active_model.message_post(cr, uid, [record_id],subtype=subtype, context=context,**values)
            
            mail_obj = self.pool.get('mail.mail')
            mail_ids = mail_obj.search(cr, uid, [('subject','=',values['subject']),('model','=',model),('res_id','=',record_id)], context=context)    
            for data in mail_obj.browse(cr,uid,mail_ids,context):
                if not data.email_to :
                    email=active_model.browse(cr,uid,record_id,context=context).partner_id.email
                    mail_obj.write(cr,uid,data.id,{'state': 'outgoing','email_to':email})
        return True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
