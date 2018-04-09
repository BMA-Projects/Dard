# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

import openerp
from openerp.osv import orm, osv, fields
from openerp.tools.translate import _
from lxml import etree
from openerp.osv.orm import setup_modifiers
from openerp import SUPERUSER_ID

class sale_order(osv.osv):
    _inherit='sale.order'
    _columns = {
        'support_ticket_ids': fields.one2many('crm.helpdesk', 'sale_order_id' ,'Support Ticket', readonly=True),
    }
    
    # create sale order from support ticket and link order with support ticket.
    def create(self, cr, uid, vals, context=None):
        print 'context', context
        res = super(sale_order, self).create(cr, uid, vals, context=context)
        if 'support_ticket_ids' in context:
            crm_helpdesk = self.pool.get('crm.helpdesk')
            crm_helpdesk.write(cr, uid, context['support_ticket_ids'], {'sale_order_id': res}, context=context)
        return res

class ob_crm_helpdesk(osv.osv):
    _inherit = "crm.helpdesk"
    _track = {
        'state': {
            'ob_helpdesk.mt_st_new': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'ob_helpdesk.mt_st_in_progress': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'open',
            'ob_helpdesk.mt_st_pending': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'pending',
            'ob_helpdesk.mt_st_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
            'ob_helpdesk.mt_st_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
            'ob_helpdesk.mt_st_stage': lambda self, cr, uid, obj, ctx=None: obj['state'] not in ['draft', 'open', 'pending', 'done', 'cancel']
        },
    }
    _columns = {
        'sale_order_id': fields.many2one('sale.order', 'Sale Order'),
        'parent_support_ticket_id': fields.many2one('crm.helpdesk', 'Support Tickets'),
        'child_support_ticket_ids': fields.one2many('crm.helpdesk', 'parent_support_ticket_id', 'Duplicate Support Tickets'),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not context: context = {}
        if not default: default = {}
        default.update({'sale_order_id': False, 'parent_support_ticket_id':False})
        return super(ob_crm_helpdesk,self).copy(cr, uid, id, default, context)

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(ob_crm_helpdesk, self).default_get(cr, uid, fields, context=context)
        categ_id = self.pool.get('crm.case.categ').search(cr, uid, [('name', 'ilike', 'Order Entry')])
        if categ_id:
            res.update({'categ_id': categ_id[0]})
        return res
        
    
    # for group_sale_salesman / group_sale_salesman_all_leads crm helpdesk form view is readonly except sale order id field
#    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
#        if context is None:
#            context = {}
#        res = super(ob_crm_helpdesk,self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
#        try:
#            support_manager_group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ob_helpdesk', 'group_support_manager')[1]
#        except:
#            return res
#        if uid != SUPERUSER_ID and support_manager_group_id not in [x.id for x in self.pool.get('res.users').browse(cr, uid, uid, context=context).groups_id]:
#            if view_type == 'tree':
#                doc = etree.XML(res['arch'])
#                nodes = doc.xpath("//tree")
#                for node in nodes:
#                    node.set('create', 'false')
#                res['arch'] = etree.tostring(doc)
#            elif view_type == 'form':
#                doc = etree.XML(res['arch'])
#                nodes = doc.xpath("//form")
#                for node in nodes:
#                    node.set('create', 'false')
#                nodes = doc.xpath("//field[@name='name']")
#                for node in nodes:
#                    node.set('readonly', '1')
#                    setup_modifiers(node, res['fields']['name'])
#                nodes = doc.xpath("//field[@name='section_id']")
#                for node in nodes:
#                    node.set('readonly', '1')
#                    setup_modifiers(node, res['fields']['section_id'])
#                nodes = doc.xpath("//field[@name='date']")
#                for node in nodes:
#                    node.set('readonly', '1')
#                    setup_modifiers(node, res['fields']['date'])
#                nodes = doc.xpath("//field[@name='user_id']")
#                for node in nodes:
#                    node.set('readonly', '1')
#                    setup_modifiers(node, res['fields']['user_id'])
#                nodes = doc.xpath("//field[@name='date_deadline']")
#                for node in nodes:
#                    node.set('readonly', '1')
#                    setup_modifiers(node, res['fields']['date_deadline'])
#                nodes = doc.xpath("//field[@name='partner_id']")
#                for node in nodes:
#                    node.set('readonly', '1')
#                    setup_modifiers(node, res['fields']['partner_id'])
#                nodes = doc.xpath("//field[@name='email_from']")
#                for node in nodes:
#                    node.set('readonly', '1')
#                    setup_modifiers(node, res['fields']['email_from'])
#                nodes = doc.xpath("//field[@name='priority']")
#                for node in nodes:
#                    node.set('readonly', '1')
#                    setup_modifiers(node, res['fields']['priority'])
#                nodes = doc.xpath("//field[@name='categ_id']")
#                for node in nodes:
#                    node.set('readonly', '1')
#                    setup_modifiers(node, res['fields']['categ_id'])
#                nodes = doc.xpath("//field[@name='channel_id']")
#                for node in nodes:
#                    node.set('readonly', '1')
#                    setup_modifiers(node, res['fields']['channel_id'])
#                nodes = doc.xpath("//field[@name='description']")
#                for node in nodes:
#                    node.set('readonly', '1')
#                    setup_modifiers(node, res['fields']['description'])
#                nodes = doc.xpath("//field[@name='active']")
#                for node in nodes:
#                    node.set('readonly', '1')
#                    setup_modifiers(node, res['fields']['active'])
#                nodes = doc.xpath("//field[@name='planned_cost']")
#                for node in nodes:
#                    node.set('readonly', '1')
#                    setup_modifiers(node, res['fields']['planned_cost'])
#                nodes = doc.xpath("//field[@name='ref']")
#                for node in nodes:
#                    node.set('readonly', '1')
#                    setup_modifiers(node, res['fields']['ref'])
#                nodes = doc.xpath("//field[@name='ref2']")
#                for node in nodes:
#                    node.set('readonly', '1')
#                    setup_modifiers(node, res['fields']['ref2'])
#                res['arch'] = etree.tostring(doc)
#        return res
                   
    
    # server action to send acknowledgement to the customer for support ticket.
    def action_send_confirm(self, cr, uid, context=None):
        record_id = context.get('active_id')
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ob_helpdesk', 'email_template_helpdesk_support_process')[1]
        email_template_obj = self.pool.get('email.template')
        email_template_obj.write(cr, uid, template_id, {'email_to': self.browse(cr, uid, record_id).email_from})
        mail_id = email_template_obj.send_mail(cr, uid, template_id, record_id, force_send=True, context=context)
        return True
    
    # onchange of sale order in support ticket raise warning if already linked support ticket with selected sale order
    # raise warning for if you unlink sale order from support ticket then duplicate tickets also unlinked from sale order
    def onchange_sale_order(self, cr, uid, ids, sale_order_id, context=None):
        if sale_order_id:
            sale_order_obj = self.pool.get('sale.order')
            sale_order = sale_order_obj.browse(cr, uid, sale_order_id, context=context)
            if len(sale_order.support_ticket_ids) > 0:
                for rec in sale_order.support_ticket_ids:
                    if self.browse(cr, uid, rec.id, context=context).parent_support_ticket_id.id == False:
                        raise openerp.exceptions.Warning(_('Selected Sale Order has already Support Ticket %s. This Support ticket will markup as Duplicate Support Ticket of %s.' % (rec.id, rec.id)))
        elif not sale_order_id and len(ids) > 0:
            if self.browse(cr, uid, ids[0], context=context).sale_order_id and not self.browse(cr, uid, ids[0], context=context).parent_support_ticket_id:
                soobj = self.browse(cr, uid, ids[0], context=context).sale_order_id
                soid = self.browse(cr, uid, ids[0], context=context).sale_order_id.id
                if soid:
                    ticketids = []
                    for rec in soobj.support_ticket_ids:
                        if rec.parent_support_ticket_id.id != False:
                            ticketids.append(rec.id)
                    if len(ticketids) > 0:
                        ticketids = ", ".join(map(str,ticketids))
                        raise openerp.exceptions.Warning(_('If you unlink this sale order from this support ticket, it will also unlink all duplicate tickets (%s) from this sale order' % (ticketids)))
        return True
    
    # update parent/child support ticket and sale order according link/unlink sale order in support ticket.
    def write(self, cr, uid, ids, vals, context=None):
        sale_order_obj = self.pool.get('sale.order')
        # if vals.get('state'):
        #     if vals.get('state') == 'open':
        #         self.customer_notification(cr, uid, ids, 'email_template_helpdesk_support_open', context=context)
        #     if vals.get('state') == 'pending':
        #         self.customer_notification(cr, uid, ids, 'email_template_helpdesk_support_pending', context=context)
        #     if vals.get('state') == 'cancel':
        #         self.customer_notification(cr, uid, ids, 'email_template_helpdesk_support_cancel', context=context)
        #     if vals.get('state') == 'done':
        #         self.customer_notification(cr, uid, ids, 'email_template_helpdesk_support_close', context=context)
        #     if vals.get('state') == 'draft':
        #         self.customer_notification(cr, uid, ids, 'email_template_helpdesk_support_open', context=context)
            
        if 'sale_order_id' in vals and vals['sale_order_id'] != False:
            support_ticket = self.browse(cr, uid, ids, context=context)[0]
            if support_ticket.parent_support_ticket_id.id == False and support_ticket.sale_order_id.id != vals['sale_order_id']:
                ticket_ids = self.search(cr, uid, [('parent_support_ticket_id', '=', ids[0])], context=context)
                if len(ticket_ids) > 0:
                    for ticket_id in ticket_ids:
                        self.write(cr, uid, [ticket_id], {'parent_support_ticket_id': False, 'sale_order_id': False}, context=context)
            elif support_ticket.parent_support_ticket_id.id != False and support_ticket.sale_order_id.id != vals['sale_order_id']:
                self.write(cr, uid, ids, {'parent_support_ticket_id': False}, context=context)
            
            sale_order = sale_order_obj.browse(cr, uid, vals['sale_order_id'], context=context)
            if len(sale_order.support_ticket_ids) > 0:
                for rec in sale_order.support_ticket_ids:
                    if not rec.parent_support_ticket_id and rec.id != ids[0]:
                        vals['parent_support_ticket_id'] = rec.id
        elif 'sale_order_id' in vals and vals['sale_order_id'] == False:
            vals['parent_support_ticket_id'] = False
            support_ticket = self.browse(cr, uid, ids, context=context)[0]
            if support_ticket.parent_support_ticket_id.id == False and support_ticket.sale_order_id.support_ticket_ids:
                if len(support_ticket.sale_order_id.support_ticket_ids) > 0:
                    values = {}
                    for rec in support_ticket.sale_order_id.support_ticket_ids:
                        if rec.id != ids[0]:
                            values['parent_support_ticket_id'] = False
                            values['sale_order_id'] = False
                            self.write(cr, uid, [rec.id], values, context=context)
        return super(ob_crm_helpdesk, self).write(cr, uid, ids, vals, context=context)
    
    # On Workflow update state of tickets
    def case_new(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'draft'})
        return True
    
    def case_open(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'open'})
        return True
    
    def case_pending(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'pending'})
        return True
    
    def case_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'cancel'})
        return True
    
    def case_close(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'done'})
        return True
    
    def case_reset(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'draft'})
        return True
    
    def customer_notification(self, cr, uid, ids, template, context=None):
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ob_helpdesk', template)[1]
        email_template_obj = self.pool.get('email.template')
        email_template_obj.write(cr, uid, template_id, {'email_to': self.browse(cr, uid, ids[0]).email_from})
        mail_id = email_template_obj.send_mail(cr, uid, template_id, ids[0], force_send=True, context=context)
        return True

    def create_sale_order(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        ir_model_data_obj = self.pool.get('ir.model.data')
        ir_model_data_id = ir_model_data_obj.search(cr, uid, [['model', '=', 'ir.ui.view'], ['name', '=', 'view_order_form']], context=context)
        if ir_model_data_id:
             view_id = ir_model_data_obj.read(cr, uid, ir_model_data_id, fields=['res_id'])[0]['res_id']
        context.update({'support_ticket_ids': ids})
        return {
             'name': 'Create Sale Order',
             'view_type': 'form',
             'view_mode': 'form',
             'view_id': [view_id],
             'res_model': 'sale.order',
             'context': context,
             'type': 'ir.actions.act_window',
             'nodestroy': True,
             'target': 'current',
         }
