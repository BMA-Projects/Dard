# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import fields, models, api, _, tools
from datetime import date, time
from lxml import etree


class product_template(models.Model):
    _inherit = 'product.template'
    
    @api.multi
    def open_product_prices(self):
        return {
                 'type': 'ir.actions.act_window',
                 'name': 'Product Prices',
                 'res_model': 'product.template',
                 'res_id': self.id,
                 'view_type': 'form',
                 'view_mode': 'form',
                 'target' : 'current',
         }
    
    def get_dynamic_product_price_item(self, cr, uid, product_id):
        pricelist_item_pool  = self.pool.get('product.pricelist.item')
        page_dict = {}
        if product_id:
            pricelist_item_ids = pricelist_item_pool.search(cr, uid, [('product_tmpl_id', '=', product_id)])
            
            if pricelist_item_ids:
                for pricelist_item_obj in pricelist_item_pool.browse(cr, uid, pricelist_item_ids):
                    if str(pricelist_item_obj.price_version_id.pricelist_id.name) not in page_dict:
                        page_dict.update({pricelist_item_obj.price_version_id.pricelist_id.name: pricelist_item_obj})        
        return page_dict
        
    def get_dynamic_pricelist_ver(self, cr, uid, pricelist_id, product_id):
        pricelist_item_pool  = self.pool.get('product.pricelist.item')
        price_ver_dict = {}
        if product_id:
            pricelist_item_ids = pricelist_item_pool.search(cr, uid, [('product_tmpl_id', '=', product_id)])
            
            if pricelist_item_ids:
                for pricelist_item_obj in pricelist_item_pool.browse(cr, uid, pricelist_item_ids):
                    if pricelist_item_obj.price_version_id.pricelist_id.id == pricelist_id and str(pricelist_item_obj.price_version_id.name) not in price_ver_dict:
                        price_ver_dict.update({pricelist_item_obj.price_version_id.name: pricelist_item_obj.price_version_id})  
        return price_ver_dict                    
    
    @api.multi
    def read(self, fields=None, load='_classic_read'):
        pricelist_item_pool  = self.env['product.pricelist.item']
        res = super(product_template, self).read(fields,load=load)    
        if self._context.get('bin_size'):
            product_price_vals = {}
            for rec1 in res:
                if rec1.get('id') and self._context:
                    # To get Pricelist dict
                    page_dict = self.get_dynamic_product_price_item(rec1.get('id'))
                    for price_item_key in page_dict:
                        # Pricelist id
                        pricelist_id = page_dict.get(price_item_key) and page_dict.get(price_item_key).price_version_id.pricelist_id.id or False
                        # To get Pricelist Versions dict
                        price_ver_dict = self.get_dynamic_pricelist_ver(pricelist_id, rec1.get('id'))
                        for price_ver in price_ver_dict:
                            # Pricelist Version
                            price_ver_id = price_ver_dict.get(price_ver) and price_ver_dict.get(price_ver).id
                            start_date = price_ver_dict.get(price_ver).date_start
                            end_date = price_ver_dict.get(price_ver).date_end
                            active = price_ver_dict.get(price_ver).active
                            # Search Pricelist Items for Current product and pricelist version
                            pricelist_item_ids = pricelist_item_pool.search([('product_tmpl_id', '=', rec1.get('id')), ('price_version_id', '=', price_ver_id)], order="id")
                            # To get list of ids from list of objects
                            pricelist_item_ids = [x.id for x in pricelist_item_ids]
                            if pricelist_item_ids:
                                product_price_vals.update({
                                    'ob_' + price_item_key + '_' + price_ver +'_pp_ver_start_date': start_date,
                                    'ob_' + price_item_key + '_' + price_ver + '_pp_ver_end_date': end_date,
                                    'ob_' + price_item_key + '_' + price_ver + '_pp_ver_state': active,
                                    'ob_' + price_item_key + '_' + price_ver +'_product_price_lines': pricelist_item_ids,
                                })
                rec1.update(product_price_vals)
                
        return res
    
    @api.v7
    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(product_template, self).fields_view_get(cr, user, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if context is None:context = {}
        product_id = context.get('active_id', False)
        pricelist_item_pool  = self.pool.get('product.pricelist.item')
        pricelist_ver_pool  = self.pool.get('product.pricelist.version')
        
        if view_type == 'form':
            page_list = []
            page_dict = {}
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//notebook")
            if product_id and context.get('active_model') == 'product.template':
                page_dict = self.get_dynamic_product_price_item(cr, user, product_id)

            if nodes:
                for page_name in page_dict:
                    page_node = etree.Element('page', {'string': page_name})
                                
                    pricelist_id = page_dict.get(page_name) and page_dict.get(page_name).price_version_id.pricelist_id.id or False
                    
                    # To get Pricelist Versions
                    price_ver_dict = self.get_dynamic_pricelist_ver(cr, user, pricelist_id, product_id)
                    for price_ver in price_ver_dict:
                        extra_info_group = etree.Element('group')
                        pp_group = etree.Element('group', {'string': price_ver})
                        
                        # To find object reference of Tree view
                        v_id = self.pool.get("ir.model.data").get_object_reference(cr, user, 'ob_pricelist', "product_pricelist_item_tree_view")[1]
                        prod_temp_price_item_tree_view = pricelist_item_pool.fields_view_get(cr, user, view_id=v_id, view_type='tree', context=context, toolbar=False, submenu=False)
                                                    
                        # one2many field to show product price-qty relation
                        product_price_lines = etree.Element('field',{'name' : 'ob_' + page_name + '_' + price_ver +'_product_price_lines'})
                        res['fields'].update({'ob_' + page_name + '_' + price_ver +'_product_price_lines': {'type':'one2many', 'relation': 'product.pricelist.item', 'nolabel': '1', 'views': {'tree': prod_temp_price_item_tree_view }} })
                        
                        # To set start and End date of Pricelist Version
                        product_pricelist_ver_start_date = etree.Element('field',{'name' : 'ob_' + page_name + '_' + price_ver +'_pp_ver_start_date'})
                        product_pricelist_ver_end_date = etree.Element('field',{'name' : 'ob_' + page_name + '_' + price_ver +'_pp_ver_end_date'})
                        product_pricelist_ver_state = etree.Element('field',{'name' : 'ob_' + page_name + '_' + price_ver +'_pp_ver_state'})
                        res['fields'].update({'ob_' + page_name + '_' + price_ver + '_pp_ver_start_date': {'type':'date','string':'Start Date'} })
                        res['fields'].update({'ob_' + page_name + '_' + price_ver + '_pp_ver_end_date': {'type':'date','string':'End Date'} })
                        res['fields'].update({'ob_' + page_name + '_' + price_ver + '_pp_ver_state': {'type':'boolean','string':'Active'} })
                        
                        # To remove field label
                        product_price_lines.set('nolabel', '1')
                
                        extra_info_group.insert(1, product_pricelist_ver_start_date)
                        extra_info_group.insert(2, product_pricelist_ver_end_date)
                        extra_info_group.insert(3, product_pricelist_ver_state)
                        
                        pp_group.insert(1, extra_info_group)
                        pp_group.insert(2, product_price_lines)
                        page_node.insert(1, pp_group)
                        
                    # To set all fields to Readonly
                    fields_node = page_node.xpath("//field")
                    for new_field in fields_node:
                        new_field.set('modifiers','{"readonly":1}')
                    nodes[0].append(page_node)
            res['arch'] = etree.tostring(doc)
        return res
        
        
class product_product(models.Model):
    _inherit = 'product.product'
    
    @api.multi
    def open_product_prices(self):
        return {
                 'type': 'ir.actions.act_window',
                 'name': 'Product Prices',
                 'res_model': 'product.product',
                 'res_id': self.id,
                 'view_type': 'form',
                 'view_mode': 'form',
                 'target' : 'current',
         }
    
    def get_dynamic_product_price_item(self, cr, uid, product_id):
        pricelist_item_pool  = self.pool.get('product.pricelist.item')
        page_dict = {}
        if product_id:
            product_tmpl_id = self.read(cr, uid, product_id, ['product_tmpl_id'])[0]['product_tmpl_id'][0]
            # To get pricelist items for Product Template and Variant it self
            pricelist_item_ids = pricelist_item_pool.search(cr, uid, ['|', ('product_id', '=', product_id), ('product_tmpl_id', '=', product_tmpl_id)])
            
            if pricelist_item_ids:
                for pricelist_item_obj in pricelist_item_pool.browse(cr, uid, pricelist_item_ids):
                    if str(pricelist_item_obj.price_version_id.pricelist_id.name) not in page_dict:
                        page_dict.update({pricelist_item_obj.price_version_id.pricelist_id.name: pricelist_item_obj})        
        return page_dict

    def get_dynamic_pricelist_ver(self, cr, uid, pricelist_id, product_id):
        pricelist_item_pool  = self.pool.get('product.pricelist.item')
        price_ver_dict = {}
        if product_id:
            product_tmpl_id = self.read(cr, uid, product_id, ['product_tmpl_id'])[0]['product_tmpl_id'][0]
            # To get pricelist items for Product Template and Variant it self
            pricelist_item_ids = pricelist_item_pool.search(cr, uid, ['|', ('product_id', '=', product_id), ('product_tmpl_id', '=', product_tmpl_id)])
            
            if pricelist_item_ids:
                for pricelist_item_obj in pricelist_item_pool.browse(cr, uid, pricelist_item_ids):
                    if pricelist_item_obj.price_version_id.pricelist_id.id == pricelist_id and str(pricelist_item_obj.price_version_id.name) not in price_ver_dict:
                        price_ver_dict.update({pricelist_item_obj.price_version_id.name: pricelist_item_obj.price_version_id})  
        return price_ver_dict                    
    
    @api.multi
    def read(self, fields=None, load='_classic_read'):
        pricelist_item_pool  = self.env['product.pricelist.item']
        res = super(product_product, self).read(fields,load=load)    
        if self._context.get('bin_size'):
            product_price_vals = {}
            for rec1 in res:
                if rec1.get('id') and self._context:
                    #Product Template Id
                    product_tmpl_id = self.browse(rec1.get('id')).product_tmpl_id.id
                    
                    # To get Pricelist dict
                    page_dict = self.get_dynamic_product_price_item(rec1.get('id'))
                    for price_item_key in page_dict:
                        # Pricelist id
                        pricelist_id = page_dict.get(price_item_key) and page_dict.get(price_item_key).price_version_id.pricelist_id.id or False
                        # To get Pricelist Versions dict
                        price_ver_dict = self.get_dynamic_pricelist_ver(pricelist_id, rec1.get('id'))
                        for price_ver in price_ver_dict:
                            # Pricelist Version
                            price_ver_id = price_ver_dict.get(price_ver) and price_ver_dict.get(price_ver).id
                            start_date = price_ver_dict.get(price_ver).date_start
                            end_date = price_ver_dict.get(price_ver).date_end
                            active = price_ver_dict.get(price_ver).active
                            
                            # Search Pricelist Items for Current product and pricelist version
                            pricelist_item_ids = pricelist_item_pool.search(['|', ('product_id', '=', rec1.get('id')), ('product_tmpl_id', '=', product_tmpl_id), ('price_version_id', '=', price_ver_id)], order="id")
                            # To get list of ids from list of objects
                            pricelist_item_ids = [x.id for x in pricelist_item_ids]
                            if pricelist_item_ids:
                                product_price_vals.update({
                                    'ob_' + price_item_key + '_' + price_ver +'_pp_ver_start_date': start_date,
                                    'ob_' + price_item_key + '_' + price_ver + '_pp_ver_end_date': end_date,
                                    'ob_' + price_item_key + '_' + price_ver + '_pp_ver_state': active,
                                    'ob_' + price_item_key + '_' + price_ver +'_product_price_lines': pricelist_item_ids,
                                })
                rec1.update(product_price_vals)
                
        return res
    
    @api.v7
    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(product_product, self).fields_view_get(cr, user, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if context is None:context = {}
        product_id = context.get('active_id', False)
        pricelist_item_pool  = self.pool.get('product.pricelist.item')
        pricelist_ver_pool  = self.pool.get('product.pricelist.version')
        
        if view_type == 'form':
            page_list = []
            page_dict = {}
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//notebook")
            if product_id and context.get('active_model') == 'product.product':
                page_dict = self.get_dynamic_product_price_item(cr, user, product_id)

            if nodes:
                for page_name in page_dict:
                    page_node = etree.Element('page', {'string': page_name})
                                
                    pricelist_id = page_dict.get(page_name) and page_dict.get(page_name).price_version_id.pricelist_id.id or False
                    
                    # To get Pricelist Versions
                    price_ver_dict = self.get_dynamic_pricelist_ver(cr, user, pricelist_id, product_id)
                    for price_ver in price_ver_dict:
                        pp_group = etree.Element('group', {'string': price_ver})
                        extra_info_group = etree.Element('group')
                        
                        # To find object reference of Tree view
                        v_id = self.pool.get("ir.model.data").get_object_reference(cr, user, 'ob_pricelist', "product_pricelist_item_tree_view")[1]
                        prod_temp_price_item_tree_view = pricelist_item_pool.fields_view_get(cr, user, view_id=v_id, view_type='tree', context=context, toolbar=False, submenu=False)
                                                    
                        # one2many field to show product price-qty relation
                        product_price_lines = etree.Element('field',{'name' : 'ob_' + page_name + '_' + price_ver +'_product_price_lines'})
                        res['fields'].update({'ob_' + page_name + '_' + price_ver +'_product_price_lines': {'type':'one2many', 'relation': 'product.pricelist.item', 'nolabel': '1', 'views': {'tree': prod_temp_price_item_tree_view }} })
                        
                        # To set start and End date of Pricelist Version
                        product_pricelist_ver_start_date = etree.Element('field',{'name' : 'ob_' + page_name + '_' + price_ver +'_pp_ver_start_date'})
                        product_pricelist_ver_end_date = etree.Element('field',{'name' : 'ob_' + page_name + '_' + price_ver +'_pp_ver_end_date'})
                        product_pricelist_ver_state = etree.Element('field',{'name' : 'ob_' + page_name + '_' + price_ver +'_pp_ver_state'})
                        res['fields'].update({'ob_' + page_name + '_' + price_ver + '_pp_ver_start_date': {'type':'date','string':'Start Date'} })
                        res['fields'].update({'ob_' + page_name + '_' + price_ver + '_pp_ver_end_date': {'type':'date','string':'End Date'} })
                        res['fields'].update({'ob_' + page_name + '_' + price_ver + '_pp_ver_state': {'type':'boolean','string':'Active'} })
                        
                        # To remove field label
                        product_price_lines.set('nolabel', '1')
                        
                        extra_info_group.insert(1, product_pricelist_ver_start_date)
                        extra_info_group.insert(2, product_pricelist_ver_end_date)
                        extra_info_group.insert(3, product_pricelist_ver_state)
                        
                        pp_group.insert(1, extra_info_group)
                        pp_group.insert(1, product_price_lines)
                        page_node.insert(1, pp_group)
                    # To set all fields to Readonly
                    fields_node = page_node.xpath("//field")
                    for new_field in fields_node:
                        new_field.set('modifiers','{"readonly":1}')
                    nodes[0].append(page_node)
            res['arch'] = etree.tostring(doc)
        return res        
