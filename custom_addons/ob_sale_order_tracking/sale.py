# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models,fields,api,SUPERUSER_ID
from lxml import etree
# import PyV8

class sale_order(models.Model):
    _inherit = 'sale.order'

    so_tracking_id = fields.Many2one('so.tracking', string='SO Tracking', readonly='1',ondelete='cascade', select=True)
    so_tracking_stage_id = fields.Many2one('so.tracking.stage', string='SO Tracking Stage', readonly='1',ondelete='cascade', select=True)

    @api.model
    def create(self, vals):
        track_stage_obj = self.env['so.tracking.stage']
        track_obj = self.env['so.tracking']
        sale_id = super(sale_order, self).create(vals)
        tracking_vals = {}
        sale_vals = {}
        stage_id = False
        if not vals.get('so_tracking_id', False):
            stage = track_stage_obj.search([('case_default', '=', True)])
            if not stage:
                stage = track_stage_obj.search([])
            if stage:
                stage_id = stage[0].id
            sale_vals.update({'so_tracking_stage_id': stage_id})
            # tracking_vals.update({'sale_order_id': sale_id, 'partner_id': vals['partner_id'], 'confirm_date': vals['confirm_date'], \
            #             'client_order_ref': vals['client_order_ref'],'invoiced': vals['invoiced'], \
            #             'shipped': vals['shipped'], 'user_id': vals['user_id'], 'stage_id': stage_id, #'order_line': [(0, )], \
            #             'amount_untaxed': sale.amount_untaxed, 'amount_tax': sale.amount_tax, 'amount_total': sale.amount_total, 'date_order': sale.date_order})
            tracking_vals.update({'sale_order_id': sale_id.id, 'partner_id': vals.get('partner_id', False), \
                          'client_order_ref': vals.get('client_po_ref', False),'invoiced': vals.get('invoiced', False), \
                          'shipped': vals.get('shipped',False), 'user_id': vals.get('user_id', False), 'stage_id': stage_id, #'order_line': [(0, )], \
                          'amount_untaxed': sale_id.amount_untaxed, 'amount_tax': sale_id.amount_tax, 'amount_total': sale_id.amount_total, 'date_order': sale_id.date_order})
            track_id = self.env['so.tracking'].create(tracking_vals)
            if track_id:
                sale_vals.update({'so_tracking_id': track_id.id})
                self.browse(sale_id.id).write(sale_vals)
        return sale_id

    @api.one
    def write(self, vals):
        tracking_vals = {}
        so_tracking_obj = self.env['so.tracking']
        res = super(sale_order, self).write(vals)
        if self.ids and not isinstance(self.ids, (list)):
            self.ids = [self.ids]
        # tarcking_fields = ['sale_order_id', 'partner_id', 'confirm_date', 'client_order_ref', 'rush_order', 'invoiced', 'shipped', 'user_id', 'stage_id']    
        tarcking_fields = ['sale_order_id', 'partner_id', 'client_order_ref', 'invoiced', 'shipped', 'user_id', 'stage_id']
        for order in self:
            so_tracking_id = order.so_tracking_id and order.so_tracking_id.id
            if so_tracking_id:
                tracking_vals.update({'amount_untaxed': order.amount_untaxed, 'amount_tax': order.amount_tax, 'amount_total': order.amount_total, 'client_order_ref': self.client_po_ref})
                for tfield in tarcking_fields:
                    if vals.has_key(tfield) and vals.get(tfield, False):
                        tracking_vals.update({tfield: vals.get(tfield, False)})
                so_tracking_obj.browse(so_tracking_id).write(tracking_vals)
        return res

    # def my_method(self,cr,uid,ids,context=None):
        
    #     # obj_model = self.pool.get('ir.ui.view')
    #     # model_data_ids = obj_model.search(cr,uid,[('model','=','sale.order.allow'),('name', '=', 'stage.change.wizard.form')], limit=1)
    #     # compose_form = obj_model.read(cr, uid, model_data_ids,)
    #     # print "xxxxxxxxxxxxxxddddddddddddddddddddddddddddddddddxxxxxxxx",compose_form
    #     # ctx = dict(
    #     #     default_model='sale.order',
    #     # )
    #     # return {
    #     #     'name': _('Confirm Action'),
    #     #     'type': 'ir.actions.act_window',
    #     #     'view_type': 'form',
    #     #     'view_mode': 'form',
    #     #     'res_model': 'sale.order.allow',
    #     #     'views': [(compose_form, 'form')],
    #     #     'target': 'new',
    #     #     'context': ctx,
    #     # }
    #     models_data = self.pool.get('ir.model.data')
    #     result = models_data._get_id(cr, uid, 'ob_sale_order_tracking', 'stage_change_wizard_form')
    #     v_id = models_data.browse(cr, uid, result, context=context).res_id
    #     print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwe",v_id
    #     return {
    #             'view_mode': 'form',
    #             'views': [(v_id, 'form')],
    #             'view_id': v_id,
    #             'res_model': 'sale.order.allow',
    #             'view_type': 'form',
    #             'type': 'ir.actions.act_window',
    #             'context': context,
    #             'target': 'new',
    #         }


    @api.v7
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'so_tracking_stage_id': False,
            'so_tracking_id': False,
            'ship_dt': False,
        })
        return super(sale_order, self).copy(cr, uid, id, default, context=context)


    @api.multi
    def create_tracking(self, vals):
        tracking_obj = self.env['so.tracking']
        track_stage_obj = self.env['so.tracking.stage']
        tracking_vals = {}
        sale_vals = {}
        stage_id = False
        stage = track_stage_obj.search([('case_default', '=', True)])
        if not stage:
            stage = track_stage_obj.search([])
        if stage:
            stage_id = stage[0].id
        sale_vals.update({'so_tracking_stage_id': stage_id})
        self.write(sale_vals)
        for so in self:
            if not so.so_tracking_id:
                # tracking_vals.update({'sale_order_id': so.id, 'partner_id': so.partner_id.id, 'confirm_date': so.confirm_date, \
       #                        'client_order_ref': so.client_order_ref, 'rush_order': so.rush_order, 'invoiced': so.invoiced, \
       #                        'shipped': so.shipped, 'user_id': so.user_id.id, 'stage_id': stage_id,
       #                        'amount_untaxed': so.amount_untaxed, 'amount_tax': so.amount_tax, 'amount_total': so.amount_total, 'date_order': so.date_order})
                tracking_vals.update({'sale_order_id': so.id, 'partner_id': so.partner_id.id,\
                              'client_order_ref': so.client_order_ref, 'invoiced': so.invoiced, \
                              'shipped': so.shipped or False, 'user_id': so.user_id.id, 'stage_id': stage_id,
                              'amount_untaxed': so.amount_untaxed, 'amount_tax': so.amount_tax, 'amount_total': so.amount_total, 'date_order': so.date_order})
                track_id = tracking_obj.create(tracking_vals)
                if track_id:
                    if isinstance(track_id, (long, int)):
                        self.write({'so_tracking_id':track_id})
                    else:
                        self.write({'so_tracking_id':track_id.id})

        return True

    def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification', subtype=None, parent_id=False, attachments=None, context=None, \
            content_subtype='html', **kwargs):
        """ To post Sales Order messages in related Tracking
        """
        message_obj = self.pool.get('mail.message')
        sale_obj = self.pool.get('so.tracking')
        values ={}
        if context is None:
            context = {}
        res = super(sale_order, self).message_post(cr, uid, thread_id, body=body, subject=subject, type=type, subtype=subtype, parent_id=parent_id, \
            attachments=attachments, context=context, content_subtype=content_subtype, **kwargs)
        if res:
            data = message_obj.browse(cr, uid, res, context=context)
            so_data = self.browse(cr, uid, thread_id)
            values.update({
                'model': 'so.tracking',
                'res_id': so_data.so_tracking_id.id,
                'body' : data.body,
                'parent_id': False,
                'author_id': data.author_id.id
            })
            if values:
                message_obj.create(cr, SUPERUSER_ID, values=values, context=context)
        return res

class sale_order_line(models.Model):

    _inherit = 'sale.order.line'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        context = context or {}
        result = super(sale_order_line, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context,
                                toolbar=toolbar, submenu=False)
        if view_type == 'form' and 'from_so_tracking' in context and context['from_so_tracking']:
            form_string = result['arch']
            form_node = etree.XML(form_string)
            button_node = form_node.xpath("//button")
            for button in button_node:
                button.getparent().remove(button)
            result['arch'] = etree.tostring(form_node)
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
