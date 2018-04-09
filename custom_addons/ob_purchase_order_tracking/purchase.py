# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, fields, api, _
from openerp.osv import osv

class procurement_order(osv.osv):
    
    _inherit = 'procurement.order'

    def make_po(self, cr, uid, ids, context=None):
        context.update({'is_make_po': True, 'session_user':uid})
        return super(procurement_order, self).make_po(cr, uid, ids, context=context)


class purchase_order(models.Model):

    _inherit = 'purchase.order'

    po_tracking_id = fields.Many2one('po.track', string='PO Tracking', readonly=True)
    po_tracking_stage_id = fields.Many2one(string = 'PO Tracking Stage', related = 'po_tracking_id.stage_id' ,readonly=True)
    
    @api.model
    def create(self,vals):
        track_stage_obj = self.env['po.track.stage']
        track_obj = self.env['po.track']
        sale_obj = self.env['sale.order']
        purchase_rec = super(purchase_order, self).create(vals)
        tracking_vals = {}
        purchase_vals = {}
        stage_id = False
        if vals.get('po_tracking_stage_id', False):
            stage_id = vals.get('po_tracking_stage_id', False)
        if not stage_id:
            comp_id = self.env.user.company_id.id
            if 'session_user' in self._context:
                user_id = self._context.get("session_user")
                comp_id = self.env['res.users'].search([('id','=',user_id)]).company_id.id
            stage_id = track_stage_obj.search([('case_default', '=', True),('company_id','=',comp_id)])
            if stage_id:
                stage_id = stage_id[0].id
        if purchase_rec.order_line:
            for line in purchase_rec.order_line:
                if line.so_ref:
                    sale_rec = sale_obj.search([('name','=',line.so_ref)])
                    tracking_vals.update({'sale_order_ids':[(4,sale_rec.id)]})

        tracking_vals.update({
            'purchase_order_id' : purchase_rec.id,
        	'partner_id': purchase_rec.partner_id.id,
            'order_line' : purchase_rec.order_line,
        	'confirm_date': purchase_rec.date_approve,
            'partner_ref': purchase_rec.partner_ref,
            'dest_add_id' : purchase_rec.location_id.id,
            'stage_id': stage_id,
            'amount_untaxed': purchase_rec.amount_untaxed, 
            'amount_tax': purchase_rec.amount_tax,
            'date_order' : purchase_rec.date_order,
            'amount_total': purchase_rec.amount_total,
            'date_order': purchase_rec.date_order,
            'currency' : purchase_rec.currency_id.id})
            
        if vals.get('origin'):
            sale_rec = sale_obj.search([('name','=',vals.get('origin').split(':')[0])])
            tracking_vals.update({
                'sale_order_id' : sale_rec.id,
                'sale_partner_id' : sale_rec.partner_id.id,
                'sale_date_order' : sale_rec.date_order,
                'sale_cust_po' : sale_rec.client_order_ref,
                'is_paid' : sale_rec.invoiced,
                'is_delivered' : sale_rec.shipped,
                'sale_order_processor' : sale_rec.user_id.id,
                'sale_order_line' : sale_rec.order_line,
                'sale_amount_untaxed': sale_rec.amount_untaxed, 
                'sale_amount_tax': sale_rec.amount_tax,
                'sale_amount_total': sale_rec.amount_total,
            })
        track_rec = track_obj.create(tracking_vals)
        if track_rec:
            purchase_rec.write({'po_tracking_id': track_rec.id,'po_tracking_stage_id': stage_id})
        return purchase_rec

    @api.multi
    def write(self,vals):
        tracking_vals = {}
        po_tracking_obj = self.env['po.track']
        sale_obj = self.env['sale.order']
        purchase_rec = super(purchase_order, self).write(vals)
        tarcking_fields = ['purchase_order_id', 'partner_id', 'confirm_date', 'partner_ref','stage_id','dest_add_id','date_order','currency']
        po_tracking_id = self.po_tracking_id and self.po_tracking_id.id
        # if purchase_rec.order_line:
        #     for line in purchase_rec.order_line:
        #         if line.so_ref:
        #             sale_rec = sale_obj.search([('name','=',line.so_ref)])
        #             tracking_vals.update({'sale_order_ids':[(4,sale_rec.id)]})
        if po_tracking_id:
            tracking_vals.update({'amount_untaxed': self.amount_untaxed, 'amount_tax': self.amount_tax, 'amount_total': self.amount_total})
            for tfield in tarcking_fields:
                if vals.has_key(tfield) and vals.get(tfield, False):
                    tracking_vals.update({tfield: vals.get(tfield, False)})
            if vals.get('po_tracking_stage_id'):
                tracking_vals.update({'stage_id': vals.get('po_tracking_stage_id', False)})
            self.po_tracking_id.write(tracking_vals)
        for line in self.order_line:
            if not line.po_tracking_id:
                line.write({'po_tracking_id':po_tracking_id,'po_tracking_stage_id':self.po_tracking_id.stage_id.id or False})
        return purchase_rec

    @api.multi
    def copy(self,default):
        if not default:
            default = {}
        stage_id = False
        track_stage_obj = self.env['po.track.stage']
        stage_id = track_stage_obj.search([('case_default', '=', True)])
        if stage_id:
            stage_id = stage_id[0].id
        default.update({
            'po_tracking_stage_id': stage_id,
        })
        return super(purchase_order, self).copy(default)

    @api.multi
    def create_tracking(self):
        tracking_obj = self.env['po.track']
        track_stage_obj = self.env['po.track.stage']
        tracking_vals = {}
        stage_id = False
        sale_obj = self.env['sale.order']
        if not stage_id:
            stage_id = track_stage_obj.search([('case_default', '=', True)])
            if stage_id:
                stage_id = stage_id[0].id
        self.write( {'po_tracking_stage_id': stage_id})

        tracking_vals.update({
            'purchase_order_id': self.id,
            'partner_id': self.partner_id.id,
            'order_line' : self.order_line,
            'confirm_date': self.date_approve,
            'partner_ref': self.partner_ref,
            'dest_add_id' : self.location_id.id,
            'stage_id': stage_id, 
            'amount_untaxed': self.amount_untaxed, 
            'amount_tax': self.amount_tax,
            'amount_total': self.amount_total,
            'date_order': self.date_order,
            'currency' : self.currency_id.id})
            
        if self.origin:
            sale_rec = sale_obj.search([('name','=',self.origin.split(':')[0])])
            tracking_vals.update({
                'sale_order_id' : sale_rec.id,
                'sale_partner_id' : sale_rec.partner_id.id,
                'sale_date_order' : sale_rec.date_order,
                'sale_cust_po' : sale_rec.client_order_ref,
                'is_paid' : sale_rec.invoiced,
                'is_delivered' : sale_rec.shipped,
                'sale_order_processor' : sale_rec.user_id.id,
                'sale_order_line' : sale_rec.order_line,
                'sale_amount_untaxed': sale_rec.amount_untaxed, 
                'sale_amount_tax': sale_rec.amount_tax,
                'sale_amount_total': sale_rec.amount_total,
            })
        track_id = tracking_obj.create(tracking_vals)
        if track_id:
            self.write({'po_tracking_id': track_id.id, 'po_tracking_stage_id': stage_id})
        return True

    @api.cr_uid_ids_context
    def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification', subtype=None, parent_id=False, attachments=None, context=None, content_subtype='html', **kwargs):
        """ Overrides mail_thread message_post so that we can set the date of last action field when
            a new message is posted on the issue.
        """
        res = super(purchase_order, self).message_post(cr, uid, thread_id, body=body, subject=subject, type=type, subtype=subtype, parent_id=parent_id, attachments=attachments, context=context, content_subtype=content_subtype, **kwargs)
        if 'flag_post_message' in context and context.get("flag_post_message",False):
            message_obj = self.pool.get('mail.message')
            purchase_obj = self.pool.get('purchase.order')
            values ={}
            if context is None:
                context = {}
            if res:
                data = message_obj.browse(cr, uid, res, context=context)
                po_track_data = self.browse(cr, uid,thread_id)
                po_obj_data = purchase_obj.browse(cr, uid,thread_id)
                values.update({
                    'model': 'po.track',
                    'res_id': po_obj_data.po_tracking_id.id or False,
                    'body' : data.body,
                    'parent_id': False,
                })
                if values:
                    message_obj.create(cr, uid, values, context=context )
        return res

class purchase_order_line(models.Model):
    
    _inherit = 'purchase.order.line'

    @api.model
    def create(self,vals):
        po_line_rec = super(purchase_order_line,self).create(vals)
        sale_obj = self.env['sale.order']
        purchase_obj = self.env['purchase.order']

        if po_line_rec.order_id.po_tracking_id:
            purchase_obj = purchase_obj.search([('id','=',po_line_rec.order_id.id)])
            if po_line_rec.so_ref:
                sale_rec = sale_obj.search([('name','=',po_line_rec.so_ref)])
                purchase_obj.po_tracking_id.write( {'sale_order_ids':[( 4,sale_rec.id ) ] } )
        return po_line_rec

    @api.multi
    def read(self,fields, load='_classic_read'):
        po_track = self.env['po.track']
        res = super(purchase_order_line,self).read(fields,load=load)
        for data in res:
            if data.get('po_tracking_id',False):
                pt_id = data.get('po_tracking_id')
                if not isinstance(pt_id, (int, long)):
                    pt_id = data.get('po_tracking_id')[0]
                po_track_data = po_track.browse(pt_id)
                data.update({'since1':po_track_data.since,'max_time_limit1':po_track_data.stage_id.max_time_limit})
        return res

    po_tracking_id = fields.Many2one('po.track', string='PO Tracking',store=True)
    po_tracking_stage_id = fields.Many2one('po.track.stage',string = 'PO Tracking Stage',store=True)
    since1 = fields.Integer(string = 'Since',)
    max_time_limit1 = fields.Integer(string = 'Max time limit',store=True)
    
    @api.multi
    def open_tracking(self):
        res_id = self.po_tracking_id.id
        return {
                 'type': 'ir.actions.act_window',
                 'name': 'PO Tracking',
                 'res_model': 'po.track',
                 'res_id': res_id,
                 'view_type': 'form',
                 'view_mode': 'form',
                 'target' : 'current',
         }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
