# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, fields, api, _, osv
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as dt
from lxml import etree
from openerp.http import request
from openerp.exceptions import Warning

class sale_order(models.Model):

    _inherit = 'sale.order'

    po_tracking_id = fields.Many2one('po.track', string='PO Tracking', readonly=True)
    
class po_stage_email_from(models.Model):
    
    _name = 'po.stage.email.from'
  
    name = fields.Char(string='Email', required=True, size=64)
    email_id = fields.Many2one('po.track.stage')


class po_stage_email_type(models.Model):
    
    _name = 'po.stage.email.type'
  
    name = fields.Char(string='Email Type', required=True, size=64)

class po_track_stage(models.Model):
    _name = 'po.track.stage'
    _description = 'Purchase Order Tracking stage'
    _order = 'sequence'
  
    name = fields.Char(string='Stage Name', required=True, size=64, translate=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer('Sequence')
    case_default = fields.Boolean(string='Default for New Tracking',
                    help="If you check this field, this stage will be proposed by default on each new SO tracking.")
    fold = fields.Boolean(string='Folded by Default',
                    help="This stage is not visible, for example in status bar or kanban view, when there are no records in that stage to display.")
    max_time_limit = fields.Integer(string="Max Time Limit")
    is_mail = fields.Boolean(string="E-mail Required", help="If true than mail sending is complusory for move in this stage.")
    email_ids = fields.Many2many(comodel_name='ir.mail_server',column1='smtp_user',string='Email IDs')
    email_type_id = fields.Many2one('po.stage.email.type', string="Email Type")
    email_template_id = fields.Many2one('email.template', string="Default Template")
    email_from_id = fields.One2many('po.stage.email.from', 'email_id',string="Email From")
    company_id = fields.Many2one("res.company", "Company", default=lambda self: self.env.user.company_id)

    _sql_constraints = [
          ('sequence_satge_uniq', 'Check(1=1)', 'The sequence of stage must be unique !')
    ]

    @api.onchange('case_default')
    def _onchange_case_default(self):
        if self.case_default:
            search_data = self.search([('case_default', '=', True),('company_id','=',self.env.user.company_id.id)])
            for data in search_data:
                data.write({'case_default': False })

class share_wizard(models.TransientModel):
     
    _inherit = 'share.wizard'
     
    def create(self, cr, uid, values, context=None):
        if 'name' in values and values.get('name') == 'PO Tracking':
            action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ob_purchase_order_tracking', 'open_purchase_tracking')[1]
            values.update({'action_id':action_id})
        res = super(share_wizard,self).create(cr, uid, values, context=context)
        return res

class po_track(models.Model):
    _name = 'po.track'
    _description = 'Po Track'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char(string='Tracking No', readonly=True)
    partner_id = fields.Many2one('res.partner', string="Vendor", readonly=True)
    stage_id = fields.Many2one('po.track.stage', string='PO tracking Stages', track_visibility='onchange')
    dest_add_id = fields.Many2one('stock.location', string="Shipped TO", readonly=True)
    purchase_order_id =  fields.Many2one('purchase.order', string='Purchase Order', readonly=True)
    order_line =  fields.One2many(string='order_line',related='purchase_order_id.order_line', readonly=True)
    date_order = fields.Datetime(string = 'Order Date', readonly=True)
    confirm_date =  fields.Datetime(string='Order Confirm On', readonly=True)
    currency = fields.Many2one('res.currency',string='Currency', readonly=True)
    partner_ref = fields.Char(string='Supplier Reference', readonly=True)
    amount_untaxed =  fields.Float(string='Untaxed Amount' , readonly=True)
    amount_tax = fields.Float(string='Taxes', readonly=True)
    amount_total = fields.Float(string='Total', help="The total amount." , readonly=True)
    color = fields.Integer(string='Color Index', readonly=True)
    update_time = fields.Datetime(string='Updated time')
    since = fields.Integer(string = 'Since')
    company_id = fields.Many2one("res.company","Company",compute='_get_company_id',store=True)
    
    _order="since desc"
    
    @api.multi
    @api.depends('purchase_order_id.company_id')
    def _get_company_id(self):
        for rec in self:
            rec.company_id = rec.purchase_order_id.company_id
    
    def _read_group_stage_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        stage_obj = self.pool.get('po.track.stage')
        result = stage_obj.name_search(cr, uid, '', context=context)
        return result, {}

    _group_by_full = {
        'stage_id': _read_group_stage_ids,
    }

    @api.v8
    def get_dynamic_sale_order(self, sale_id):
        po_track_data = self.browse(sale_id)
        sale_obj = self.env['sale.order']
        page_list = []
        page_dict = {}
        if po_track_data.purchase_order_id:
            for line in po_track_data.purchase_order_id.order_line:
                if line.so_ref:
                    sale_rec = sale_obj.search([('name','=',line.so_ref)])
                    value_list = []
                    if str(sale_rec.name) not in page_dict:
                        page_dict.update({sale_rec.name:sale_rec})
        return page_dict

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(po_track, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         def get_view_id(xid, name):
#             try:
#                 return self.env['ir.model.data'].xmlid_to_res_id('po_track.' + xid, raise_if_not_found=True)
#             except ValueError:
#                 try:
#                     return self.env['ir.ui.view'].search([('name', '=', name)], limit=1).id
#                 except Exception:
#                     return False    # view not found

#         if context.get('active_model') == 'po.track' and context.get('active_ids'):
#             partner = self.env['po.track'].browse(context['active_ids'])[0]
#             if not view_type:
#                 view_id = get_view_id('view_po_track_tree', 'po.track.tree')
#                 view_type = 'tree'
#             elif view_type == 'form':
#                 view_id = get_view_id('view_po_track_form', 'po.track.form')

        # return res
        
        if view_type == 'form':
            po_track_data = self.browse(self._context.get('active_id'))
            sale_obj = self.env['sale.order']
            page_list = []
            page_dict = {}
            context = self._context
            doc = etree.XML(res['arch'])
            fields_dict = res['fields']
            nodes = doc.xpath("//notebook")
            page_dict = self.get_dynamic_sale_order(self._context.get('active_id'))
            if nodes:
                for page_name in page_dict:
        
                    page_node = etree.Element('page',{'string':page_name})
                    page_group = etree.Element('group', {'col':"4"})
                    footer_group = etree.Element('group', { "class":"oe_subtotal_footer oe_right" ,'colspan' :"2" ,'name' :"sale_total_inherit"})
                    chatter_class = etree.Element('div',{'class':'oe_chatter'})
                    clear_class = etree.Element('div',{'class':'oe_clear'})
                    
                    page_partner_id = etree.Element('field', {'name': page_name + '_partner_id'})
                    sale_order_date = etree.Element('field',{'name': page_name + '_order_date'})
                    customer_po_number = etree.Element('field',{'name': page_name + '_cust_po_number'})
                    confirm_date = etree.Element('field',{'name': page_name + '_confirm_date'})
                    is_rush_order = etree.Element('field',{'name': page_name + '_is_rush_order'})
                    is_sample = etree.Element('field',{'name': page_name + '_is_sample'})
                    is_paid = etree.Element('field',{'name': page_name + '_is_paid'})
                    is_delivered = etree.Element('field',{'name': page_name + '_is_delivered'})
                    sale_order_line = etree.Element('field',{'name': page_name + '_sale_order_line'})
                    amount_untaxed = etree.Element('field',{'name': page_name + '_amount_untaxed' ,'widget':'monetary'})
                    amount_tax = etree.Element('field',{'name': page_name + '_amount_tax' ,'widget':'monetary'})
                    amount_total = etree.Element('field',{'name': page_name + '_amount_total' ,'widget':'monetary', "class":"oe_subtotal_footer_separator"})
                    sale_message_ids1 = etree.Element('field',{'name': page_name + '_sale_message_ids1','widget':"mail_thread",'options': '{"sale_id":"' + page_name + '","custom_flag":1}'})
    
                    res['fields'].update({page_name + '_partner_id': {'relation':'res.partner','type':'many2one','string':'Customer'} })
                    res['fields'].update({page_name + '_order_date': {'type':'date','string':'Order Date'} })
                    res['fields'].update({page_name + '_cust_po_number': {'type':'char','string':'Customer PO Number'} })
                    res['fields'].update({page_name + '_confirm_date': {'type':'date','string':'Confirm Date'} })
                    res['fields'].update({page_name + '_is_rush_order': {'type':'boolean','string':'Is Rush Order'} })
                    res['fields'].update({page_name + '_is_sample': {'type':'boolean','string':'Is Sample'} })
                    res['fields'].update({page_name + '_is_paid': {'type':'boolean','string':'Paid'} })
                    res['fields'].update({page_name + '_is_delivered': {'type':'boolean','string':'Delivered'} })
                    res['fields'].update({page_name + '_sale_order_line': {'type':'many2many', 'relation': 'sale.order.line',} })
                    res['fields'].update({page_name + '_amount_untaxed': {'type':'float', 'string': 'Untaxed Amount',} })
                    res['fields'].update({page_name + '_amount_tax': {'type':'float', 'string': 'Taxes',} })
                    res['fields'].update({page_name + '_amount_total': {'type':'float', 'string': 'Total',} })
                    res['fields'].update({page_name + '_sale_message_ids1': {'type':'many2many', 'relation': 'mail.message',} })
                    
                    page_group.insert(1,page_partner_id)
                    page_group.insert(2,sale_order_date)
                    page_group.insert(3,customer_po_number)
                    page_group.insert(4,confirm_date)
                    page_group.insert(5,is_rush_order)
                    page_group.insert(6,is_sample)
                    page_group.insert(7,is_paid)
                    page_group.insert(8,is_delivered)
                    page_group.insert(9,sale_order_line)
                    footer_group.insert(1,amount_untaxed)
                    footer_group.insert(2,amount_tax)
                    footer_group.insert(3,amount_total)
                    chatter_class.insert(1,sale_message_ids1)
    
                    page_node.insert(1,page_group)
                    page_node.insert(2,sale_order_line)
                    page_node.insert(3,footer_group)
                    page_node.insert(4,clear_class)
                    page_node.insert(5,chatter_class)
                    nodes[0].append(page_node)
                    
            res['arch'] = etree.tostring(doc)
        return res
 
    @api.model
    def create(self,vals):
    	sale_obj = self.env['sale.order']
        purchase_order_line = self.env['purchase.order.line']
    	track_stage_obj = self.env['po.track.stage']
    	sale_vals = {}
        stage_id = False
        if vals.get('name','/')=='/':
            vals['name'] = self.env['ir.sequence'].get('po.tracking') or '/'
        if vals.get('stage_id',False):
            vals.update({'update_time':datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        res = super(po_track, self).create(vals)
        for line in res.purchase_order_id.order_line:
            if line:
                line.write({'po_tracking_id':res.id, 'po_tracking_stage_id':res.stage_id.id,'since1':res.since,'max_time_limit1':res.stage_id.max_time_limit})
        return res
    
    @api.v8
    def calculate_since_value(self, upd_time=False):
        from_date = datetime.strptime(datetime.strftime(datetime.now(),dt), dt)
        time_diff =  from_date - datetime.strptime(upd_time, dt)
        total_time = time_diff.total_seconds()/3600
        return total_time

    @api.multi
    def read(self,fields, load='_classic_read'):
        res = super(po_track,self).read(fields,load=load)
        for rec1 in res:
            page_dict = self.get_dynamic_sale_order(rec1.get('id'))
            sale_vals = {}
            for sale_key in page_dict:
                sale_rec = page_dict.get(sale_key)
                line_ids = [x.id for x in sale_rec.order_line]
                message_ids = [x.id for x in sale_rec.message_ids]
                sale_vals.update({
                    sale_key + '_partner_id' : sale_rec.partner_id.id,
                    sale_key + '_order_date' : sale_rec.date_order,
                    sale_key + '_cust_po_number' : sale_rec.client_order_ref,
                    sale_key + '_confirm_date' : sale_rec.date_order,
                    sale_key + '_is_rush_order' : False,
                    sale_key + '_is_sample' : False,
                    sale_key + '_is_paid' : sale_rec.invoiced,
                    sale_key + '_is_delivered' : sale_rec.shipped,
                    sale_key + '_sale_order_line' : [(6,0,line_ids)],
                    sale_key + '_amount_untaxed' : sale_rec.amount_untaxed,
                    sale_key + '_amount_tax' : sale_rec.amount_tax,
                    sale_key + '_amount_total' : sale_rec.amount_total,
                    sale_key + '_sale_message_ids1' : message_ids

                })
            rec1.update(sale_vals)
        stage_obj = self.env['po.track.stage']
        vals = {}
        for data in self:
            time_limit = data.stage_id.max_time_limit
            if data.update_time:
                t_time = self.calculate_since_value(data.update_time)
                if not t_time:
                    t_time = 0
                vals.update({'since':t_time,})
                if t_time >= time_limit and time_limit != 0:
                    vals.update({'color':2})
                else:
                    vals.update({'color':0})
                if data:
                    data.write(vals)
        return res

    @api.multi
    def write(self,vals):
        purchase_id = False
        purchase_vals = {}
        purchase_line_vals = {}
#         purchase_obj = self.env['purchase.order']
        
        for po_rec in self:
            if 'stage_id' in vals:
                stage_id = vals.get('stage_id', False)
                if stage_id:
                    stage_comp_id = self.env['po.track.stage'].search([('id','=',stage_id)]).company_id.id
                    if stage_comp_id != po_rec.company_id.id:
                        raise Warning(_("Not able to move to this stage as it is belong to different company.")) 
        
        
        if self.purchase_order_id and self.purchase_order_id.id and vals.get('stage_id', False):
            purchase_vals.update({'po_tracking_stage_id': vals.get('stage_id', False)})
            purchase_line_vals.update({'po_tracking_stage_id': vals.get('stage_id', False),'since1': 0})
        if vals.get('stage_id',False):
            upd_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.write({'update_time': upd_time, 'since': 0})
        if purchase_vals:
#             purchase_obj.write(purchase_vals)
            if purchase_line_vals:
                for line in self.purchase_order_id.order_line:
                    line.write(purchase_line_vals) 
        return super(po_track, self).write(vals)
    
    def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification', subtype=None, parent_id=False, attachments=None, context=None, content_subtype='html', **kwargs):
        """ Overrides mail_thread message_post so that we can set the date of last action field when
            a new message is posted on the issue.
        """
       
        message_obj = self.pool.get('mail.message')
        purchase_obj = self.pool.get('purchase.order')
        sale_obj = self.pool.get('sale.order')
        values ={}
        if context is None:
            context = {}
        res = super(po_track, self).message_post(cr, uid, thread_id, body=body, subject=subject, type=type, subtype=subtype, parent_id=parent_id, attachments=attachments, context=context, content_subtype=content_subtype, **kwargs)
        if res:
            data = message_obj.browse(cr, uid, res, context=context)
            po_track_data = self.browse(cr, uid,thread_id)

            values.update({
                'model': 'purchase.order',
                'res_id': po_track_data.purchase_order_id.id,
                'body' : data.body,
                'parent_id': False,
            })

            sale_id = context.get('sale_id',False)
            if sale_id:
                sale_ids = sale_obj.search(cr,uid,[('name','=',sale_id)],context=context)
                if sale_ids:
                    sale_data = sale_obj.browse(cr, uid, sale_ids,context=context) 
                
                values.update({
                    'model': 'sale.order',
                    'res_id': sale_data[0].id,
                    'body' : data.body,
                    'parent_id': False,
                })
            
            if values:
                message_obj.create(cr, uid, values, context=context )
        return res
    
    @api.multi
    def open_view(self):
#         print dir(self)
        return {
                 'type': 'ir.actions.act_window',
                 'name': 'PO Tracking',
                 'res_model': 'po.track',
                 'res_id': self.id,
                 'view_type': 'form',
                 'view_mode': 'form',
                 'target' : 'current',
         }
    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
