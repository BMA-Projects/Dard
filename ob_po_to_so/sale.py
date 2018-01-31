# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, fields, api, _, tools
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as dt
from lxml import etree
from openerp.http import request

class share_wizard(models.TransientModel):
     
    _inherit = 'share.wizard'
     
    def create(self, cr, uid, values, context=None):
        if 'name' in values and values.get('name') == 'Sale Order With PO':
            action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'action_orders')[1]
            values.update({'action_id':action_id})
        res = super(share_wizard,self).create(cr, uid, values, context=context)
        return res

class stock_move(models.Model):
     
    _inherit = 'stock.move' 

    @api.v7
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        context = context or {}
        result = super(stock_move, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context,
                                toolbar=toolbar, submenu=False)
        if view_type == 'form' and 'from_po_to_so' in context and context['from_po_to_so']:
            form_string = result['arch']
            form_node = etree.XML(form_string)
            button_node = form_node.xpath("//button")
            for button in button_node:
                button.getparent().remove(button)
            result['arch'] = etree.tostring(form_node)
        return result
    
class sale_order(models.Model):

    _inherit = 'sale.order'   
    
    @api.multi
    def onchange(self, values, field_name, field_onchange):
        keys = field_onchange.keys()
        for key in keys:
            if key.startswith("ob_"):
                field_onchange.pop(key)
        keys = values.keys()
        for key in keys:
            if key.startswith("ob_"):
                values.pop(key)
        try:
            return super(sale_order, self).onchange(values, field_name, field_onchange)
        except Exception:
            return False
     
    def get_dynamic_manufecture_order(self,cr, uid, sale_id,context=None):
        sale_order_data = False
        if self.search(cr, uid, [('id', '=', sale_id)]):
            sale_order_data = self.browse(cr, uid, sale_id)
        mo_obj = self.pool.get('mrp.production')
        page_list = []
        page_dict = {}
        if sale_order_data:
            mrp_ids = mo_obj.search(cr, uid, [('origin','like',sale_order_data.name),('state','not in', ['cancel'])])
            mrp_rec = mo_obj.browse(cr, uid, mrp_ids)
            value_list = []
            for mrp_rec in mrp_rec:
                if str(mrp_rec.name) not in page_dict:
                    page_dict.update({mrp_rec.name:mrp_rec})
        return page_dict
     
    def get_dynamic_purchase_order(self,cr, uid, sale_id):
        sale_order_data = False
        if self.search(cr, uid, [('id', '=', sale_id)]):
            sale_order_data = self.browse(cr, uid, sale_id)
        purchase_obj = self.pool.get('purchase.order')
        mo_obj = self.pool.get('mrp.production')
        page_list = []
        page_dict = {}
        if sale_order_data:
            for line in sale_order_data.order_line:
                if line.po_ref:
                    purchase_ids = purchase_obj.search(cr, uid, [('name','=',line.po_ref)])
                    if purchase_ids:
                        purchase_rec = purchase_obj.browse(cr, uid, purchase_ids[0])
                        value_list = []
                        if str(purchase_rec.name) not in page_dict:
                            page_dict.update({purchase_rec.name:purchase_rec})
        return page_dict
     
    @api.multi
    def open_sale_order_with_po(self):
        return {
                 'type': 'ir.actions.act_window',
                 'name': 'Sale Order With PO',
                 'res_model': 'sale.order',
                 'res_id': self.id,
                 'view_type': 'form',
                 'view_mode': 'form',
                 'target' : 'current',
         }
      
    def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification', subtype=None, parent_id=False, attachments=None, context=None, content_subtype='html', **kwargs):
        """ Overrides mail_thread message_post so that we can set the date of last action field when
            a new message is posted on the issue.
        """
         
        message_obj = self.pool.get('mail.message')
        purchase_obj = self.pool.get('purchase.order')
        sale_obj = self.pool.get('sale.order')
        mo_obj = self.pool.get('mrp.production')
        values ={}
        if context is None:
            context = {}
     
        if context.get('purchase_id',False):
            purchase_ids = purchase_obj.search(cr,uid,[('name','=',context.get('purchase_id'))],context=context)
            if purchase_ids:
                purchase_data = purchase_obj.browse(cr, uid, purchase_ids,context=context) 
                if content_subtype == 'plaintext':
                    body = tools.plaintext2html(body)
                values.update({
                    'model': 'purchase.order',
                    'res_id': purchase_data[0].id,
                    'body' : body,
                    'parent_id': False,
                })
        if context.get('mo_id',False):
            mo_ids = mo_obj.search(cr, uid, [('name','=',context.get('mo_id'))],context=context)
            if mo_ids:
                mo_data = mo_obj.browse(cr, uid, mo_ids, context=context)
                if content_subtype == 'plaintext':
                    body = tools.plaintext2html(body)
                values.update({
                    'model': 'mrp.production',
                    'res_id': mo_data[0].id,
                    'body' : body,
                    'parent_id': False,
                })
        if values:
            return message_obj.create(cr, uid, values, context=context )
        else:
            return super(sale_order, self).message_post(cr, uid, thread_id, body=body, subject=subject, type=type, subtype=subtype, parent_id=parent_id, attachments=attachments, context=context, content_subtype=content_subtype, **kwargs)
      
    @api.multi
    def read(self,fields=None,load='_classic_read'):
        res = super(sale_order,self).read(fields,load=load)
        if self._context.get('bin_size'):
            page_dict,page_dict_mo = {},[]
            purchase_mo_vals = {}
            for rec1 in res:
                if rec1.get('id') and self._context:
                    page_dict = self.get_dynamic_purchase_order(rec1.get('id'))
                    page_dict_mo = self.get_dynamic_manufecture_order(rec1.get('id'),context=self._context)
                 
                for purchase_key in page_dict:
                    if purchase_key:
                        purchase_rec = page_dict.get(purchase_key)
                        line_ids = [x.id for x in purchase_rec.order_line]
                        message_ids = [x.id for x in purchase_rec.message_ids]
                        inv_method_value = dict(purchase_rec._columns['invoice_method'].selection).get(purchase_rec.invoice_method)
                        message_follower_ids = [x.id for x in purchase_rec.message_follower_ids]
                        purchase_mo_vals.update({
                            purchase_key + '_partner_id' : purchase_rec.partner_id.id,
                            purchase_key + '_order_date' : purchase_rec.date_order,
                            purchase_key + '_supplier_ref' : purchase_rec.partner_ref,
                            purchase_key + '_source_document' : purchase_rec.origin,
                            purchase_key + '_dest_address_id' : purchase_rec.dest_address_id.id,
                            purchase_key + '_picking_type_id' : purchase_rec.picking_type_id.id,
                            purchase_key + '_purchase_order_line1' : [(6,0,line_ids)],
                            purchase_key + '_amount_untaxed' : purchase_rec.amount_untaxed,
                            purchase_key + '_amount_tax' : purchase_rec.amount_tax,
                            purchase_key + '_amount_total' : purchase_rec.amount_total,
                            purchase_key + '_purchase_message_ids1' : message_ids,
                            purchase_key + '_purchase_follower_ids' : message_follower_ids,
               
                            purchase_key + '_rfq_incoterm_id' : purchase_rec.incoterm_id.id,
                            purchase_key + '_rfq_bid_date' : purchase_rec.bid_date,
                            purchase_key + '_rfq_bid_valid_until' : purchase_rec.bid_validity,
                                   
                            purchase_key + '_del_invo_exp_date' : purchase_rec.minimum_planned_date,
                            purchase_key + '_del_invo_destination' : purchase_rec.location_id.id,
                            purchase_key + '_del_invo_received' : purchase_rec.shipped,
                            purchase_key + '_del_invo_iunvoicing_control' : inv_method_value,
                            purchase_key + '_del_invo_invoice_received' : purchase_rec.invoiced,
                            #purchase_key + '_del_invo_call_for_bids' : purchase_rec.requisition_id.id,   #### Taking the dictionary field outside ###
                            purchase_key + '_del_invo_payment_term' : purchase_rec.payment_term_id.id,
                            purchase_key + '_del_invo_fiscal_position' : purchase_rec.fiscal_position.id,
                            purchase_key + '_del_invo_validated_by' : purchase_rec.validator.id,
                            purchase_key + '_del_invo_date_approved' : purchase_rec.date_approve,
                        })
                        has_purchase_requisition_installed = self.env['ir.module.module'].\
                                            search([('name', '=', 'purchase_requisition'), ('state', '=', 'installed')])
                        if has_purchase_requisition_installed:
                            purchase_mo_vals.update\
                                ({purchase_key + '_del_invo_call_for_bids' : purchase_rec.requisition_id.id,})
                for mo_key in page_dict_mo:
                    if mo_key:
                        mo_rec = page_dict_mo.get(mo_key)
                        priority_value = dict(mo_rec._columns['priority'].selection).get(mo_rec.priority)
                        move_lines_ids = [x.id for x in mo_rec.move_lines]
                        move_lines_ids2 = [x.id for x in mo_rec.move_lines2]
                        move_created_ids = [x.id for x in mo_rec.move_created_ids]
                        move_created_ids2 = [x.id for x in mo_rec.move_created_ids2]
                        workcenter_lines = [x.id for x in mo_rec.workcenter_lines]
                        product_lines = [x.id for x in mo_rec.product_lines]
                        message_ids = [x.id for x in mo_rec.message_ids]
                        purchase_mo_vals.update({
                            'ob_' + mo_key + '_mrp_product_id' : mo_rec.product_id.id,
                            'ob_' + mo_key + '_mrp_bom_id' : mo_rec.bom_id.id,
                            'ob_' + mo_key + '_mrp_prod_qty' : mo_rec.product_qty,
                            'ob_' + mo_key + '_mrp_routing_id' : mo_rec.routing_id.id,
                            'ob_' + mo_key + '_mrp_prod_uos_qty' : mo_rec.product_uos_qty,
                            'ob_' + mo_key + '_mrp_user_id' : mo_rec.user_id.id,
                            'ob_' + mo_key + '_mrp_date_planned' : mo_rec.date_planned, 
                            'ob_' + mo_key + '_mrp_origin' : mo_rec.origin,
                            'ob_' + mo_key + '_mrp_location_src_id' : mo_rec.location_src_id.id,
                            'ob_' + mo_key + '_mrp_location_dest_id' : mo_rec.location_dest_id.id,
                            'ob_' + mo_key + '_mrp_move_lines' : move_lines_ids,
                            'ob_' + mo_key + '_mrp_move_lines2' : move_lines_ids2,
                            'ob_' + mo_key + '_mrp_move_created_ids' : move_created_ids,
                            'ob_' + mo_key + '_mrp_move_created_ids2' : move_created_ids2,
                            'ob_' + mo_key + '_mrp_workcenter_lines' : workcenter_lines,
                            'ob_' + mo_key + '_mrp_product_lines' : product_lines,
                            'ob_' + mo_key + '_mrp_priority' : priority_value,
                            'ob_' + mo_key + '_mrp_sale_ref' : mo_rec.sale_ref,
                            'ob_' + mo_key + '_mrp_sale_name' : mo_rec.sale_name,
                            'ob_' + mo_key + '_mrp_move_prod_id' : mo_rec.move_prod_id.id,
                            'ob_' + mo_key + '_mo_message_ids1' : message_ids
                        })
                rec1.update(purchase_mo_vals)
        return res
  
    @api.v7
    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(sale_order, self).fields_view_get(cr, user, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if context is None:context = {}
        sale_id = context.get('active_id',False)
        stock_move_obj  = self.pool.get('stock.move')
        page_dict_mo = {}
        
        if view_type == 'form':
            page_list = []
            page_dict = {}
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//notebook")
            if sale_id and context.get('active_model') == 'sale.order':
                page_dict = self.get_dynamic_purchase_order(cr, user,sale_id)
                page_dict_mo = self.get_dynamic_manufecture_order(cr, user, sale_id,context=context)
            if nodes:
                for page_name in page_dict:
                    page_node = etree.Element('page',{'string':page_name})
                    
                    #Notebook in Purchase order tab
                    page_node_notebook = etree.Element('notebook')
                      
                    #Pages in Purchase order tab notebook
                    page_node_product = etree.Element('page',{'string':'Products'})
                    page_node_rfq = etree.Element('page',{'string':'RFQ & Bid'})
                    page_node_deli_inv = etree.Element('page',{'string':'Deliveries & Invoices'})
                      
                    #Group in purchase order
                    page_group = etree.Element('group', {'col':"4" })

                    rfq_page_group = etree.Element('group', {'col':"2"})
                    del_invo_group = etree.Element('group', {'col':"4"})
                    footer_group = etree.Element('group', { "class":"oe_subtotal_footer oe_right" ,'colspan' :"2" ,'name' :"sale_total_inherit"})
                    chatter_class = etree.Element('div',{'class':'oe_chatter'})
                    clear_class = etree.Element('div',{'class':'oe_clear'})
                    
                    # Fields on Main purchase order tab   
                    page_partner_id = etree.Element('field', {'name': page_name + '_partner_id'})
                    purchase_order_date = etree.Element('field',{'name': page_name + '_order_date'})
                    supplier_ref = etree.Element('field',{'name': page_name + '_supplier_ref'})
                    source_document = etree.Element('field',{'name': page_name + '_source_document'})
                    cust_address = etree.Element('field', {'name': page_name + '_dest_address_id'})
                    deliver_to = etree.Element('field', {'name': page_name + '_picking_type_id'})
                      
                    # Fields on Product tab in purchase order tab
                    
                    purchase_order_line1 = etree.Element('field',{'name': page_name + '_purchase_order_line1'})
                    amount_untaxed = etree.Element('field',{'name': page_name + '_amount_untaxed' ,'widget':'monetary'})
                    amount_tax = etree.Element('field',{'name': page_name + '_amount_tax' ,'widget':'monetary'})
                    amount_total = etree.Element('field',{'name': page_name + '_amount_total' ,'widget':'monetary', "class":"oe_subtotal_footer_separator"})
                      
                     # Fields on RFQ and Bid tab.
                    rfq_incoterm_id = etree.Element('field', {'name': page_name + '_incoterm_id'})
                    rfq_bid_date = etree.Element('field', {'name': page_name + '_rfq_bid_date'})
                    rfq_bid_valid_until = etree.Element('field', {'name': page_name + '_rfq_bid_valid_until'})
                      
                    # Fields on Deliveries and Invoice tab.
                    del_invo_exp_date = etree.Element('field', {'name': page_name + '_del_invo_exp_date'})
                    del_invo_destination = etree.Element('field', {'name': page_name + '_del_invo_destination'})
                    del_invo_received = etree.Element('field', {'name': page_name + '_del_invo_received'})
                    del_invo_iunvoicing_control = etree.Element('field', {'name': page_name + '_del_invo_iunvoicing_control'})
                    del_invo_invoice_received = etree.Element('field', {'name': page_name + '_del_invo_invoice_received'})
                    del_invo_call_for_bids = etree.Element('field', {'name': page_name + '_del_invo_call_for_bids'})
                    del_invo_payment_term = etree.Element('field', {'name': page_name + '_del_invo_payment_term'})
                    del_invo_fiscal_position = etree.Element('field', {'name': page_name + '_del_invo_fiscal_position'})
                    del_invo_validated_by = etree.Element('field', {'name': page_name + '_del_invo_validated_by'})
                    del_invo_date_approved = etree.Element('field', {'name': page_name + '_del_invo_date_approved'})
                    purchase_message_ids1 = etree.Element('field',{'name': page_name + '_purchase_message_ids1','widget':"mail_thread",'options': '{"purchase_id":"' + page_name + '"}'})
                    purchase_follower_ids = etree.Element('field',{'name': page_name + '_purchase_follower_ids','widget':"mail_followers",'options': '{"purchase_id":"' + page_name + '"}'}) 

                    res['fields'].update({page_name + '_partner_id': {'relation':'res.partner','type':'many2one','string':'Supplier', 'readonly':'True'} })
                    res['fields'].update({page_name + '_order_date': {'type':'date','string':'Order Date'} })
                    res['fields'].update({page_name + '_supplier_ref': {'type':'char','string':'Supplier Reference'} })
                    res['fields'].update({page_name + '_source_document': {'type':'char','string':'Source Document'} })
                    res['fields'].update({page_name + '_dest_address_id':  {'relation':'res.partner','type':'many2one','string':'Customer Address'} })
                    res['fields'].update({page_name + '_picking_type_id':  {'relation':'res.partner','type':'many2one','string':'Deliver To'} })
                      
                    res['fields'].update({page_name + '_purchase_order_line1': {'type':'many2many', 'relation': 'purchase.order.line',} })
                    res['fields'].update({page_name + '_amount_untaxed': {'type':'float', 'string': 'Untaxed Amount',} })
                    res['fields'].update({page_name + '_amount_tax': {'type':'float', 'string': 'Taxes',} })
                    res['fields'].update({page_name + '_amount_total': {'type':'float', 'string': 'Total',} })
                         
                    res['fields'].update({page_name + '_incoterm_id': {'relation':'stock.incoterms','type':'many2one','string':'Incoterm'} })
                    res['fields'].update({page_name + '_rfq_bid_date': {'type':'date','string':'Bid Received On'} })
                    res['fields'].update({page_name + '_rfq_bid_valid_until': {'type':'date','string':'Bid Valid Until'} })
                      
                    #Fields in delivery tab.
                    res['fields'].update({page_name + '_del_invo_exp_date': {'type':'date','string':'Expected Date'} })
                    res['fields'].update({page_name + '_del_invo_destination': {'relation':'stock.location','type':'many2one','string':'Destination'} })
                    res['fields'].update({page_name + '_del_invo_received': {'type':'boolean','string':'Received'} })
#                     del_invo_iunvoicing_control,
                    res['fields'].update({page_name + '_del_invo_iunvoicing_control': {'type':'char','string':'Invoicing Control'} })
                    res['fields'].update({page_name + '_del_invo_invoice_received': {'type':'boolean','string':'Invoice Received'} })
                    res['fields'].update({page_name + '_del_invo_call_for_bids': {'relation':'purchase.requisition','type':'many2one','string':'Call for Bids'} })
                    res['fields'].update({page_name + '_del_invo_payment_term': {'relation':'account.payment.term','type':'many2one','string':'Payment Term'} })
                    res['fields'].update({page_name + '_del_invo_fiscal_position': {'relation':'account.fiscal.position','type':'many2one','string':'Fiscal Position'} })
                    res['fields'].update({page_name + '_del_invo_validated_by': {'relation':'res.users','type':'many2one','string':'Validated by'} })
                    res['fields'].update({page_name + '_del_invo_date_approved': {'type':'date','string':'Date Approved'} })
                    res['fields'].update({page_name + '_purchase_message_ids1': {'type':'many2many', 'relation': 'mail.message',} })
                    res['fields'].update({page_name + '_purchase_follower_ids': {'type':'many2many', 'relation': 'res.partner',} })
                      
                    page_group.insert(1,page_partner_id)
                    page_group.insert(2,purchase_order_date)
                    page_group.insert(3,supplier_ref)
                    page_group.insert(4,source_document)
                    page_group.insert(5,cust_address)
                    page_group.insert(6,deliver_to)
                     
                    purchase_order_line1.set('context', "{'tree_view_ref':'ob_po_to_so.purchase_order_line_tree_for_so1'}")
                    page_node_product.insert(1,purchase_order_line1)
                    page_node_product.insert(2,footer_group)
                       
                    rfq_page_group.insert(1,rfq_incoterm_id)
                    rfq_page_group.insert(2,rfq_bid_date)
                    rfq_page_group.insert(3,rfq_bid_valid_until)
                       
                    del_invo_group.insert(1,del_invo_exp_date)
                    del_invo_group.insert(2,del_invo_destination)
                    del_invo_group.insert(3,del_invo_received)
                    del_invo_group.insert(4,del_invo_iunvoicing_control)
                    del_invo_group.insert(5,del_invo_invoice_received)
                    del_invo_group.insert(6,del_invo_call_for_bids)
                    del_invo_group.insert(7,del_invo_payment_term)
                    del_invo_group.insert(8,del_invo_fiscal_position)
                    del_invo_group.insert(9,del_invo_validated_by)
                    del_invo_group.insert(10,del_invo_date_approved)                                                 
                       
                    footer_group.insert(1,amount_untaxed)
                    footer_group.insert(2,amount_tax)
                    footer_group.insert(3,amount_total)
                     
                    chatter_class.insert(1,purchase_follower_ids)
                    chatter_class.insert(2,purchase_message_ids1)
                     
                    page_node_rfq.insert(1,rfq_page_group)
                    page_node_deli_inv.insert(2,del_invo_group)     
   
                    page_node_notebook.insert(1,page_node_product)
                    page_node_notebook.insert(2,page_node_rfq)
                    page_node_notebook.insert(3,page_node_deli_inv)
   
                    page_node.insert(1,page_group)
                    page_node.insert(2,page_node_notebook)
#                     page_node.insert(3,footer_group)
                    page_node.insert(3,clear_class)
                    page_node.insert(4,chatter_class)
#                     page_node.set('readonly','1')
                    fields_node = page_node.xpath('//field')
                    for new_field in fields_node:
                        new_field.set('modifiers','{"readonly":1}')
                    nodes[0].append(page_node)
              
                if page_dict_mo:
                    for mo_page_name in page_dict_mo:
                        if mo_page_name:
                            mrp_page_node = etree.Element('page',{'string': mo_page_name})
                            
                            mo_page_group = etree.Element('group', {'col':"4" })
                            mo_page_group_1 = etree.Element('group', {'col':"2" })
                            
                            mrp_notebook = etree.Element('notebook')
                            
                            chatter_class_mo = etree.Element('div',{'class':'oe_chatter'})
                            clear_class_mo = etree.Element('div',{'class':'oe_clear'})
                            
                            mo_consu_page_group = etree.Element('group')
                            mo_consu_page_prod_consu_group = etree.Element('group',{'string':'Products to Consume'})
                            mo_consu_page_consu_prod_group = etree.Element('group',{'string':'Consumed Products'})
                            
                            mo_finish_product_group = etree.Element('group')
                            mo_produ_to_produce_group = etree.Element('group',{'string':'Products to Produces'})
                            mo_produced_product_group = etree.Element('group',{'string':'Produced Products'})
                            
                            mo_extra_info_group = etree.Element('group', {'col':"4" })
                            
                            mrp_consumed_prod_page = etree.Element('page',{'string':'Consumed Products'})
                            mrp_finished_prod_page = etree.Element('page',{'string':'Finished Products'})
                            mrp_work_orders_page = etree.Element('page',{'string': 'Work Orders'})
                            mrp_scheduled_prod_page = etree.Element('page',{'string':'Scheduled Products'})
                            mrp_extra_info_page = etree.Element('page',{'string':'Extra Information'})
                            
                            mrp_product_id = etree.Element('field', {'name': 'ob_' + mo_page_name + '_mrp_product_id'})
                            mrp_bom_id = etree.Element('field', {'name': 'ob_' + mo_page_name + '_mrp_bom_id'})
                            mrp_prod_qty = etree.Element('field',{'name': 'ob_' + mo_page_name + '_mrp_prod_qty'})
                            mrp_routing_id = etree.Element('field', {'name': 'ob_' + mo_page_name + '_mrp_routing_id'})
                            mrp_prod_uos_qty = etree.Element('field',{'name': 'ob_' + mo_page_name + '_mrp_prod_uos_qty'})
                            mrp_user_id = etree.Element('field', {'name': 'ob_' + mo_page_name + '_mrp_user_id'})
                            mrp_date_planned = etree.Element('field', {'name': 'ob_' + mo_page_name + '_mrp_date_planned'})
                            mrp_origin = etree.Element('field', {'name': 'ob_' + mo_page_name + '_mrp_origin'})
                                                                                   
                            mrp_location_src_id = etree.Element('field',{'name': 'ob_' + mo_page_name + '_mrp_location_src_id'})
                            mrp_location_dest_id = etree.Element('field',{'name': 'ob_' + mo_page_name + '_mrp_location_dest_id'})
                            
                            mrp_move_lines = etree.Element('field',{'name' : 'ob_' + mo_page_name + '_mrp_move_lines'})
                            mrp_move_lines2 = etree.Element('field',{'name' : 'ob_' + mo_page_name + '_mrp_move_lines2'})
                            mrp_move_created_ids = etree.Element('field',{'name': 'ob_' + mo_page_name + '_mrp_move_created_ids'})
                            mrp_move_created_ids2 = etree.Element('field',{'name': 'ob_' + mo_page_name + '_mrp_move_created_ids2'})
                            
                            mrp_workcenter_lines = etree.Element('field',{'name': 'ob_' + mo_page_name + '_mrp_workcenter_lines'})
                            mrp_product_lines = etree.Element('field',{'name': 'ob_' + mo_page_name + '_mrp_product_lines'})
                            
                            mrp_priority = etree.Element('field',{'name': 'ob_' + mo_page_name + '_mrp_priority'})
                            mrp_sale_ref = etree.Element('field',{'name': 'ob_' + mo_page_name + '_mrp_sale_ref'})
                            mrp_sale_name = etree.Element('field',{'name': 'ob_' + mo_page_name + '_mrp_sale_name'})
                            mrp_move_prod_id = etree.Element('field',{'name': 'ob_' + mo_page_name + '_mrp_move_prod_id'})
                            mo_message_ids1 = etree.Element('field',{'name': 'ob_' + mo_page_name + '_mo_message_ids1','widget':"mail_thread",'options': '{"mo_id":"' + mo_page_name + '"}'})
                            
                            v_id = self.pool.get("ir.model.data").get_object_reference(cr, user, 'ob_po_to_so', "stock_move_product_to_consumed_tree")[1]
                            mrp_move_lines_view = stock_move_obj.fields_view_get(cr, user, view_id=v_id, view_type='tree', context=context, toolbar=False, submenu=False)
                            
                            v_id = self.pool.get("ir.model.data").get_object_reference(cr, user, 'ob_po_to_so', "stock_move_consumed_product_tree")[1]
                            mrp_move_lines2_view = stock_move_obj.fields_view_get(cr, user, view_id=v_id, view_type='tree', context=context, toolbar=False, submenu=False)
                            
                            v_id = self.pool.get("ir.model.data").get_object_reference(cr, user, 'ob_po_to_so', "stock_move_move_created_ids_tree")[1]
                            created_ids_view = stock_move_obj.fields_view_get(cr, user, view_id=v_id, view_type='tree', context=context, toolbar=False, submenu=False)
                            
                            v_id = self.pool.get("ir.model.data").get_object_reference(cr, user, 'ob_po_to_so', "stock_move_move_created_ids2_tree")[1]
                            created_ids2_view = stock_move_obj.fields_view_get(cr, user, view_id=v_id, view_type='tree', context=context, toolbar=False, submenu=False)
                            
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_product_id': {'relation':'product.product','type':'many2one','string':'Product', } })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_bom_id': {'relation':'mrp.bom','type':'many2one','string':'Bill of Material', } })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_prod_qty': {'type':'float', 'string': 'Product Quantity',} })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_routing_id': {'relation':'mrp.routing','type':'many2one','string':'Routing', } })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_prod_uos_qty': {'type':'float', 'string': 'Product UoS Quantity',} })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_user_id': {'relation':'res.users','type':'many2one','string':'Responsible', } })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_date_planned': {'type':'date','string':'Scheduled Date'} })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_origin': {'type':'char','string':'Source Document'} })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_location_src_id': {'relation':'stock.location','type':'many2one','string':'Raw Materials Location', } })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_location_dest_id': {'relation':'stock.location','type':'many2one','string':'Finished Products Location', } })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_move_lines': {'type':'one2many', 'relation': 'stock.move','nolabel':'1','views':{'tree': mrp_move_lines_view }} })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_move_lines2': {'type':'one2many', 'relation': 'stock.move','nolabel':'1','views':{'tree': mrp_move_lines2_view }} })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_move_created_ids': {'type':'one2many', 'relation': 'stock.move','nolabel':'1','views':{'tree': created_ids_view }} })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_move_created_ids2': {'type':'one2many', 'relation': 'stock.move','nolabel':'1','views':{'tree': created_ids2_view }} })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_workcenter_lines': {'type':'one2many', 'relation': 'mrp.production.workcenter.line','nolabel':'1',} })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_product_lines': {'type':'one2many', 'relation': 'mrp.production.product.line','nolabel':'1',} })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_priority': {'type':'char', 'string': 'Priority',} })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_sale_ref': {'type':'char', 'string': 'Sale Reference',} })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_sale_name': {'type':'char', 'string': 'Sale Name',} })
                            res['fields'].update({'ob_' + mo_page_name + '_mrp_move_prod_id': {'relation':'stock.move','type':'many2one','string':'Product Move', } })
                            res['fields'].update({'ob_' + mo_page_name + '_mo_message_ids1': {'type':'many2many', 'relation': 'mail.message',} })
                            
                            
                            mo_page_group.insert(1,mrp_product_id)
                            mo_page_group.insert(2,mrp_bom_id)
                            mo_page_group.insert(3,mrp_prod_qty)
                            mo_page_group.insert(4,mrp_routing_id)
                            mo_page_group.insert(5,mrp_prod_uos_qty)
                            mo_page_group.insert(6,mrp_user_id)
                            mo_page_group.insert(7,mrp_date_planned)
                            mo_page_group.insert(8,mrp_origin)
                            
                            mo_page_group_1.insert(1,mrp_location_src_id)
                            mo_page_group_1.insert(2,mrp_location_dest_id)
                            
                            mrp_page_node.insert(1,mo_page_group)
                            mrp_page_node.insert(2,mo_page_group_1)
                            
                            mrp_move_lines.set('nolabel','1')
                            mrp_move_lines2.set('nolabel','1')
                            
                            mrp_move_lines.set('context','{"from_po_to_so":True}')
                            mrp_move_lines2.set('context','{"from_po_to_so":True}')
                            mrp_move_created_ids.set('context','{"from_po_to_so":True}')
                            mrp_move_created_ids2.set('context','{"from_po_to_so":True}')
                            
                            mo_consu_page_prod_consu_group.insert(1,mrp_move_lines)
                            mo_consu_page_consu_prod_group.insert(1,mrp_move_lines2)
                            
                            mo_consu_page_group.insert(1,mo_consu_page_prod_consu_group)
                            mo_consu_page_group.insert(2,mo_consu_page_consu_prod_group)
                            mrp_consumed_prod_page.insert(1,mo_consu_page_group)
                            
#                             mrp_move_created_ids.set('context', "{'tree_view_ref':'ob_po_to_so.stock_move_move_created_ids_tree'}")
                            mrp_move_created_ids.set('nolabel','1')
                            mo_produ_to_produce_group.insert(1,mrp_move_created_ids)
                            
#                             mrp_move_created_ids2.set('context', "{'tree_view_ref':'ob_po_to_so.stock_move_move_created_ids2_tree'}")
                            mrp_move_created_ids2.set('nolabel','1')
                            mo_produced_product_group.insert(1,mrp_move_created_ids2)
                            
                            mo_finish_product_group.insert(1,mo_produ_to_produce_group)
                            mo_finish_product_group.insert(2,mo_produced_product_group)
                            
                            mrp_finished_prod_page.insert(1,mo_finish_product_group)
                            
                            mrp_workcenter_lines.set('context', "{'tree_view_ref':'ob_po_to_so.mrp_workcenter_line_tree'}")
                            mrp_work_orders_page.insert(1,mrp_workcenter_lines)
                            
                            mrp_scheduled_prod_page.insert(1,mrp_product_lines)
                            
                            mo_extra_info_group.insert(1,mrp_priority)
                            mo_extra_info_group.insert(2,mrp_sale_ref)
                            mo_extra_info_group.insert(3,mrp_sale_name)
                            mo_extra_info_group.insert(4,mrp_move_prod_id)
                            
                            mrp_extra_info_page.insert(1,mo_extra_info_group)
                            
                            mrp_notebook.insert(1,mrp_consumed_prod_page)
                            mrp_notebook.insert(2,mrp_finished_prod_page)
                            mrp_notebook.insert(3,mrp_work_orders_page)
                            mrp_notebook.insert(4,mrp_scheduled_prod_page)
                            mrp_notebook.insert(5,mrp_extra_info_page)
                            
                            chatter_class_mo.insert(1,mo_message_ids1)
                            
                            mrp_page_node.insert(3,mrp_notebook)
                            
                            mrp_page_node.insert(4,clear_class_mo)
                            mrp_page_node.insert(5,chatter_class_mo)
                            
                            mrp_fields_node = mrp_page_node.xpath('//field')
                            for mrp_field in mrp_fields_node:
                                mrp_field.set('modifiers','{"readonly":1}')
                            nodes[0].append(mrp_page_node)
            res['arch'] = etree.tostring(doc)
        return res
