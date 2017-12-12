# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
###############################################################################

from openerp.osv import fields, osv
from openerp import models, fields, api, _
from openerp.exceptions import Warning

#----------------------------------------------------------
# Products
#----------------------------------------------------------

class tag_master(models.Model):
    _name = 'tag.master'
    _description = 'Tags Master'

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    name = fields.Char('Tag Name', required=True, translate=True, select=True)
    active = fields.Boolean('Active', help="The active field allows you to hide the category without removing it.", default=1)
    product_ids = fields.Many2many('product.product', id1='product_id', id2='tag_id', string='Products')
    parent_id = fields.Many2one('tag.master', 'Parent Tags', select=True ,ondelete='cascade')
    child_id = fields.One2many('tag.master', 'parent_id', string='Child tags')

    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from tag_master where id IN %s', (tuple(ids), ))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error! You cannot create recursive hierarchy.',['parent_id'])
    ]

    @api.multi
    def unlink(self):
        for record in self.browse(self.ids):
            tag_products = self.env["product.product"].search([('tag_id', '=', record.id)])
            if tag_products:
                raise Warning(_('You cannot delete the Tags which are used by products'))
            childids = []
            for child in record.child_id:
                childids.append(child.id)
            if childids:
                child_tag_products = self.env["product.product"].search([('tag_id', 'in', childids)])
                if child_tag_products:
                    raise Warning(_('You cannot delete this Tag as its child tags are used by products'))
        return super(tag_master, self).unlink()

class product_product(models.Model):
     
    _inherit = 'product.product'
    tag_id = fields.Many2many(string="Tags",related="product_tmpl_id.tag_id")
     
    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        
        res = []
        
        if 'tag_id' in groupby:
            #remove tag_id from groupby as we have written custom code for m2m groupby 
            groupby.remove('tag_id')
            fetched_data = []
#             undefine count 
            undefine_count = len(self.search(cr,uid,domain+[['tag_id','=',False]]))
            
#             get product_template_ids by applying domain 
            product_template_ids = self.search(cr,uid,domain)
            
            if product_template_ids: 
                product_template_ids = ((tuple(product_template_ids),)) if len(product_template_ids) != 1 else "("+str(product_template_ids[0])+")"
#                 join psql query for m2m groupby result
                base_query = """select * from (select * from product_product join product_template on product_product.product_tmpl_id = product_template.id where product_product.id in %s) as pt1 join product_template_tag_rel
                             on pt1.product_tmpl_id = product_template_tag_rel.product_id"""%(product_template_ids)
                             
                cr.execute("""select 
                               ptr.tag_id,count(ptr.product_id),tm.name 
                               from ("""+base_query+""")
                               as ptr join 
                               tag_master as tm
                               on ptr.tag_id =  tm.id
                               group by
                              ptr.tag_id,tm.name;""")
                
                fetched_data = cr.dictfetchall()
                 
            res = [{'__domain': [('tag_id', '=', str(q_data['name']))]+domain, 'tag_id': str(q_data['name']), 'tag_id_count': long(q_data['count'])} for q_data in fetched_data] \
                  +[{'tag_id': 'Undefined', 'tag_id_count': undefine_count, '__domain': [('tag_id', '=', False)]+domain}]
            
        if groupby:
            res = super(product_product, self).read_group(cr, uid, domain, fields, groupby, offset=offset, limit=limit, context=context, orderby=orderby)
        return res
    

class product_template(models.Model):
    
    _inherit = 'product.template'

    tag_id = fields.Many2many('tag.master','product_template_tag_rel', id1='product_id', id2='tag_id', string='Tags')

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        res = []
        if 'tag_id' in groupby:
            #remove tag_id from groupby as we have written custom code for m2m groupby
            groupby.remove('tag_id')
            fetched_data = []
#           undefine count 
            undefine_count = len(self.search(cr,uid,domain+[['tag_id','=',False]]))
#           get product_template_ids by applying domain            
            product_template_ids = self.search(cr,uid,domain)
            
            if product_template_ids: 
                product_template_ids = ((tuple(product_template_ids),)) if len(product_template_ids) != 1 else "("+str(product_template_ids[0])+")"
#           join psql query for m2m groupby result                
                base_query = """select * from product_template join product_template_tag_rel
                             on product_template.id = product_template_tag_rel.product_id and product_template.id in %s"""%(product_template_ids)
                             
                cr.execute("""select 
                               ptr.tag_id,count(ptr.product_id),tm.name 
                               from ("""+base_query+""")
                               as ptr join 
                               tag_master as tm
                               on ptr.tag_id =  tm.id
                               group by
                              ptr.tag_id,tm.name;""")
                
                fetched_data = cr.dictfetchall()
                
            res = [{'__domain': [('tag_id', '=', str(q_data['name']))]+domain, 'tag_id': str(q_data['name']), 'tag_id_count': long(q_data['count'])} for q_data in fetched_data] \
                  +[{'tag_id': 'Undefined', 'tag_id_count': undefine_count, '__domain': [('tag_id', '=', False)]+domain}]  
            
        if groupby:
            res = super(product_template, self).read_group(cr, uid, domain, fields, groupby, offset=offset, limit=limit, context=context, orderby=orderby)
        return res
    
class res_partner_category(models.Model):
    _inherit = 'res.partner.category'

    sale_tag_id = fields.Many2many('sale.order', string='Partner Tags')
    stk_tag_id = fields.Many2many('stock.picking', string='Partner Tags')
    pro_tag_id = fields.Many2many('procurement.order', string='Partner Tags')
    inv_tag_id = fields.Many2many('account.invoice', string='Partner Tags')

class procurement_order(models.Model):
    _inherit = 'procurement.order'

    category_id = fields.Many2many('res.partner.category', string='Partner Tags')

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    category_id = fields.Many2many('res.partner.category', string='Partner Tags')

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):
        result = super(account_invoice, self).onchange_partner_id(type, partner_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            partner_tag = partner.category_id.ids or False
            if partner_tag:
                result['value'].update({'category_id': [(6, 0, partner_tag)]})
            else:
                result['value'].update({'category_id': []})
        return result

class sale_order(models.Model):
    _inherit = 'sale.order'

    category_id = fields.Many2many('res.partner.category', string='Partner Tags')

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, part, context)
        if not context:
            context = {}
        partner = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        partner_tag = partner.category_id.ids or False
        val = res.get('value', False)
        if partner_tag:
            val.update({'category_id': [(6, 0, partner_tag)]})
        else:
        	val.update({'category_id': []})
        return res

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None):
        if not context:
            context = {}
        res = super(sale_order, self).action_invoice_create(cr, uid, ids, grouped, states, date_invoice, context)
        invoice_obj = self.pool.get('account.invoice')
        category_id = self.browse(cr, uid, ids, context=context).category_id.ids
        if category_id:
             invoice_obj.write(cr, uid, res, {'category_id': [(6, 0, category_id)]}, context)
        return res

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    category_id = fields.Many2many('res.partner.category', string='Partner Tags')

    @api.model
    def create(self, vals):
        partner_id = vals.get('partner_id','')
        origin = vals.get('origin', False)
        if origin:
            sale_order = self.env['sale.order'].search([('name', '=', origin)])
            if sale_order:
                if sale_order.category_id.ids:
                    vals.update({'category_id' : [(6, 0, sale_order.category_id.ids)]})
        return super(stock_picking, self).create(vals)

    @api.model
    def _create_invoice_from_picking(self,picking, vals):
        if 'partner_id' in vals and vals.get('partner_id', False):
            partner_id = vals.get('partner_id')
            partner = self.env['res.partner'].browse(partner_id)
            partner_tag = partner.category_id.ids or False
            if partner_tag:
                vals.update({'category_id': [(6, 0, partner_tag)]})
            else:
                vals.update({'category_id': []})
        return super(stock_picking,self)._create_invoice_from_picking(picking,vals)
