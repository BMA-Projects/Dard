# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from lxml import etree
from openerp.tools.translate import _
from openerp.exceptions import Warning
import openerp
from openerp import api
import re


class SaleOrder(osv.osv):

    _inherit = 'sale.order'
    
    def onchange(self, cr, uid, ids, values, field_name, field_onchange, context=None):
        keys = field_onchange.keys()
        for key in keys:
            if key.endswith("_imprint_color"):
                field_onchange.pop(key)
            if key.endswith("imprint_position"):
                field_onchange.pop(key)
        return super(SaleOrder, self).onchange(cr, uid, ids, values, field_name, field_onchange, context=context)
        
    def copy(self, cr, uid, id, default, context=None):
        ir_model_data = self.pool.get('ir.model.data')
        if not context: context = {}
        if not default: default = {}
        context=dict(context)

        order_lines = self.read(cr, uid, id, ['order_line'],context=context)
        if isinstance(order_lines, list):
            context.update({'from_copy': True, 'copy_lines' : order_lines[0].get('order_line')})
        elif isinstance(order_lines, dict):
            context.update({'from_copy': True, 'copy_lines' : order_lines.get('order_line')})
            
        sale_line_obj = self.pool.get('sale.order.line')
        old_list = []
        for sale_order_data in self.browse(cr, uid, id, context=context):
            for sale_line in sale_order_data.order_line: 
                if sale_line.parent_order_line_id:
                    old_list.append(sale_line.parent_order_line_id)
        old_list = list(set(old_list))
        res = super(SaleOrder, self).copy(cr, uid, id, default, context=context)
        prod_c_name = {'setup_charge': "Setup Charge",'up_charge': "Up Charge",'ltm_charge': "LTM Charge",'pms_charge': "PMS Charge",'run_charge': "Run Charge"}
        for sale_order_data in self.browse(cr, uid,[res], context=context):
            for line in sale_order_data.order_line:
                if line.parent_order_line_id in old_list:
                    context.update({'delete_from_copy':True})
                    sale_line_obj.unlink(cr, uid, line.id, context=context)
        #         else:
        #             print "call elfseererwerwewe+++++++++++++++++++=="
        #             imprint_data_fields = line.imprint_data_fields
        #             if not imprint_data_fields:
        #                 continue
        #             imprint_data_fields = eval(imprint_data_fields)

        #             prod_c_name = {'setup_charge': "Setup Charge",'up_charge': "Up Charge",'ltm_charge': "LTM Charge",'pms_charge': "PMS Charge",'run_charge': "Run Charge"}
        #             if line.product_id.is_variant:
        #                 ir_model_data = self.pool.get('ir.model.data')
        #                 product_name = line.name or ''
        #                 product_uom = ir_model_data.get_object_reference(cr, uid, 'product', "product_uom_hour")[1]
        #                 # for cname in ['setup_charge','up_charge','ltm_charge','pms_charge','run_charge']:
        #                 c_name = ''
        #                 c_name_list = []
        #                 c_charge = ''
        #                 if line.up_charge:
        #                     c_charge = line.up_charge
        #                     c_name = "up_charge"
        #                     if c_charge:
        #                         product_id = ir_model_data.get_object_reference(cr, uid, 'ob_product_variant', "product_product_" + c_name + "_service")[1]
        #                         setup_vals = {
        #                             'name' : prod_c_name.get(c_name) + " - " + product_name,
        #                             'product_id' : product_id,
        #                             'product_uom_qty' : 1,
        #                             'product_uos_qty' : 1,
        #                             'product_uom' : product_uom,
        #                             'price_unit' : c_charge,
        #                             'is_variant' : False,
        #                             'product_uos': False,
        #                             'is_charge_service' : True,
        #                             'parent_order_line_id' : line.id,
        #                             'order_id' : line.order_id.id,
        #                         }
        #                         new_id = self.pool.get('sale.order.line').create(cr, uid, setup_vals, context=context)

        #                 if line.setup_charge:
        #                     c_charge = line.setup_charge
        #                     c_name = "setup_charge"
        #                     if c_charge:
        #                         product_id = ir_model_data.get_object_reference(cr, uid, 'ob_product_variant', "product_product_" + c_name + "_service")[1]
        #                         setup_vals = {
        #                             'name' : prod_c_name.get(c_name) + " - " + product_name,
        #                             'product_id' : product_id,
        #                             'product_uom_qty' : 1,
        #                             'product_uos_qty' : 1,
        #                             'product_uom' : product_uom,
        #                             'price_unit' : c_charge,
        #                             'is_variant' : False,
        #                             'product_uos': False,
        #                             'is_charge_service' : True,
        #                             'parent_order_line_id' : line.id,
        #                             'order_id' : line.order_id.id,
        #                         }
        #                         new_id = self.pool.get('sale.order.line').create(cr, uid, setup_vals, context=context)

        #                 if line.ltm_charge:
        #                     c_charge = line.ltm_charge
        #                     c_name = "ltm_charge"
        #                     if c_charge:
        #                         product_id = ir_model_data.get_object_reference(cr, uid, 'ob_product_variant', "product_product_" + c_name + "_service")[1]
        #                         setup_vals = {
        #                             'name' : prod_c_name.get(c_name) + " - " + product_name,
        #                             'product_id' : product_id,
        #                             'product_uom_qty' : 1,
        #                             'product_uos_qty' : 1,
        #                             'product_uom' : product_uom,
        #                             'price_unit' : c_charge,
        #                             'is_variant' : False,
        #                             'product_uos': False,
        #                             'is_charge_service' : True,
        #                             'parent_order_line_id' : line.id,
        #                             'order_id' : line.order_id.id,
        #                         }
        #                         new_id = self.pool.get('sale.order.line').create(cr, uid, setup_vals, context=context)

        #                 if line.pms_charge:
        #                     c_charge = line.pms_charge
        #                     c_name = "pms_charge"
        #                     if c_charge:
        #                         product_id = ir_model_data.get_object_reference(cr, uid, 'ob_product_variant', "product_product_" + c_name + "_service")[1]
        #                         setup_vals = {
        #                             'name' : prod_c_name.get(c_name) + " - " + product_name,
        #                             'product_id' : product_id,
        #                             'product_uom_qty' : 1,
        #                             'product_uos_qty' : 1,
        #                             'product_uom' : product_uom,
        #                             'price_unit' : c_charge,
        #                             'is_variant' : False,
        #                             'product_uos': False,
        #                             'is_charge_service' : True,
        #                             'parent_order_line_id' : line.id,
        #                             'order_id' : line.order_id.id,
        #                         }
        #                         new_id = self.pool.get('sale.order.line').create(cr, uid, setup_vals, context=context)

        #                 if line.run_charge:
        #                     c_charge = line.run_charge
        #                     c_name = "run_charge"
        #                     if c_charge:
        #                         product_id = ir_model_data.get_object_reference(cr, uid, 'ob_product_variant', "product_product_" + c_name + "_service")[1]
        #                         setup_vals = {
        #                             'name' : prod_c_name.get(c_name) + " - " + product_name,
        #                             'product_id' : product_id,
        #                             'product_uom_qty' : 1,
        #                             'product_uos_qty' : 1,
        #                             'product_uom' : product_uom,
        #                             'price_unit' : c_charge,
        #                             'is_variant' : False,
        #                             'product_uos': False,
        #                             'is_charge_service' : True,
        #                             'parent_order_line_id' : line.id,
        #                             'order_id' : line.order_id.id,
        #                         }
        #                         new_id = self.pool.get('sale.order.line').create(cr, uid, setup_vals, context=context)
        # return res
        return res
        
    
    @api.v7
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if not context:
            context = {}
            
        prod_vari_dim_type_obj = self.pool.get('product.variant.dimension.type')
        prod_dim_type_obj = self.pool.get('product.dimension.type')
        sale_order_line_obj = self.pool.get('sale.order.line')
        prod_vari_dim_type_ids = prod_vari_dim_type_obj.search(cr, uid, [
            ('attribute_field_type', '!=', 'none')])
        for prod_vari_dim_type_rec in prod_vari_dim_type_obj.browse(cr, uid, prod_vari_dim_type_ids):
            field_name = str(prod_vari_dim_type_rec.name).lower().replace(" ", "_")
            field_string = prod_vari_dim_type_rec.name
            
            fields = sale_order_line_obj._fields.keys()
            if field_name not in fields:
                int_obj = re.findall(r'\d+',field_name)
                if int_obj:
                    
                    from num_to_word import int2word
                    word = int2word(int(int_obj[0]))
                    word = word.strip()
                    space_removed = word.replace(' ', '_')  #word.split(' ').join('_')
                    whole_word = space_removed.replace('-', '_')  #space_removed.split('-').join('_')
                    field_name = field_name.replace(int_obj[0], whole_word.strip())
                    field_name = field_name.replace('-','_')#field_name.split('-').join('_')
                    field_name = field_name.replace("__", "_")
#                     field_name = field_name.replace(" ", "_")
                
                if prod_vari_dim_type_rec.attribute_field_type != 'dropdown':
                    temp_field = openerp.fields.Many2many(comodel_name='product.variant.dimension.option', string=field_string)
                else:
                    temp_field = openerp.fields.Many2one(comodel_name='product.variant.dimension.option', string=field_string, model_name="sale.order.line")
                temp_field.model_name = "sale.order.line"
                temp_field.comodel_name = "product.variant.dimension.option"
                temp_field.name = field_name
                temp_field.inverse_fields = []
                temp_field._triggers = []
                sale_order_line_obj._fields.update({field_name:temp_field})
    
        
        result = super(SaleOrder, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context,
                                                        toolbar=toolbar, submenu=False)
        if view_type == 'form' and result['fields'].get('order_line', False):
            form_fields = result['fields'].get('order_line').get('views').get('form').get('fields')
            form_string = result['fields'].get('order_line').get('views').get('form').get('arch')
            form_node = etree.XML(form_string)
            grp2_node = form_node.xpath("//form/group[3]/group[2]")
            prod_vari_dim_type_ids = prod_vari_dim_type_obj.search(cr, uid, [
                ('attribute_field_type', '!=', 'none')], context=context)
            for prod_vari_dim_type_rec in prod_vari_dim_type_obj.browse(cr, uid, prod_vari_dim_type_ids, context=context):
                
                field_name = str(prod_vari_dim_type_rec.name).lower().replace(" ", "_")
                field_string = prod_vari_dim_type_rec.name
                form_attr = '{"invisible":["|","|",["is_variant","=",false],["has_imprint_method","=",false],["imprint_method","=",false]]}'
                
                int_obj = re.findall(r'\d+',field_name)
                if int_obj:
                    
                    from num_to_word import int2word
                    word = int2word(int(int_obj[0]))
                    word = word.strip()
                    space_removed = word.replace(' ', '_')  #word.split(' ').join('_')
                    whole_word = space_removed.replace('-', '_')  #space_removed.split('-').join('_')
                    field_name = field_name.replace(int_obj[0], whole_word.strip())
                    field_name = field_name.replace('-','_')#field_name.split('-').join('_')
                    field_name = field_name.replace("__", "_")
#                     field_name = field_name.replace(" ", "_")
                    
                form_cnt = "{'from_sale': True, 'product_id':product_id, 'imprint_method':imprint_method,'dimension_type_id' : " + str(prod_vari_dim_type_rec.id) + ", 'options': " + field_name + "}"
                field_def = {
                    'name': field_name,
                    'context': form_cnt,
                    'class': field_name + ' ' + 'product_variant_child_attributes',
                    'modifiers': form_attr,
                    'options': "{'no_create': True, 'no_create_edit':True, 'custom_field': true, 'is_side': true}}",
                    'on_change': "onchange_imprint_method_fields(product_id, charges_data," + field_name + ", " + str(prod_vari_dim_type_rec.id) + ", line_no_of_color, line_no_of_pms_code, line_no_of_free_color, line_no_of_free_side, imprint_method, pms_code)"
                    }
                field_type = 'many2one'
                
                if prod_vari_dim_type_rec.dimension_type == 'color':
                    field_def.update({'options': "{'no_create': True, 'no_create_edit':True, 'custom_field': true, 'is_color': true}",})

                
                if prod_vari_dim_type_rec.attribute_field_type != 'dropdown':
                    field_type = 'many2many'
                    field_def.update({'widget': 'many2many_tags'})
                form_fields[field_name] = {
                    'type': field_type,
                    'relation': 'product.variant.dimension.option',
                    'string': field_string
                }
                temp_node = etree.Element('field', field_def)
                grp2_node[0].append(temp_node)
            result['fields'].get('order_line').get('views').get('form')['arch'] = etree.tostring(form_node)
        return result


class sale_order_line(osv.osv):

    _inherit = 'sale.order.line'

    _columns = {
        'setup_charge': fields.float('Setup Charge'),
        'run_charge': fields.float('Run Charge'),
        'up_charge': fields.float('Up Charge'),
        'ltm_charge': fields.float('LTM Charge'),
        'pms_charge': fields.float('PMS Charge'),
        'imprint_method': fields.many2one('product.variant.dimension.type', 'Imprint Method'),
        'imprint_data_fields': fields.char('Imprint Data Key'),
        'imprint_data': fields.char('Imprint Data'),
        'charges_data': fields.char('Charges Data'),
        'is_variant': fields.boolean('Is Variant'),
        'apply_pms_charge': fields.boolean('Apply PMS Charge'),
        'pms_code': fields.many2many('pms.code', 'pms_code_values', 'code_id', 'line_id', 'PMS Code'),
        'temp_qty': fields.integer("Temp Qty"),
        'has_imprint_method': fields.boolean('Has Imprint Method'),
        'is_charge_service': fields.boolean('Is Charge Service'),
        'parent_order_line_id': fields.many2one('sale.order.line','Parent Line'),
        'line_no_of_pms_code': fields.integer('No of PMS Code'),
        'line_no_of_color': fields.integer('No of Color'),
        'line_no_of_position': fields.integer('No of Position'),
        'line_no_of_free_color': fields.integer('No of Free Color'),
        'line_no_of_free_side': fields.integer('No of Free Color'),
        'line_attr_max_val': fields.integer('Attribute Max Value'),
        'is_blank_order' : fields.boolean('Blank Order'),
    }

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        res = super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, line, account_id=account_id, context=context)
        if line.is_variant and not line.invoiced:
            res.update({
                'setup_charge': line.setup_charge,
                'run_charge': line.run_charge,
                'ltm_charge': line.ltm_charge,
                'pms_charge': line.pms_charge,
                'up_charge': line.up_charge,
                'is_variant': line.is_variant,
            })
        return res

    def copy(self, cr, uid, id, default=None, context=None):
        context = dict(context)
        context.update({'copu': 'yes'})
        res = super(sale_order_line,self).copy(cr, uid, id, default, context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        dimension_pool = self.pool.get('product.variant.dimension.type')
        if context is None:
            context = {}
        imprint_data = {}
        imprint_data_fields = vals.get('imprint_data_fields', False)
        if imprint_data_fields and not context.get('from_copy'):
            imprint_data_fields = eval(imprint_data_fields)
            for field in imprint_data_fields:
                if vals.get(field, False):
                    imprint_data.update({field: vals.get(field)})
                    vals.pop(field)
                    vals.update({'imprint_data': str(imprint_data)})
        res = super(sale_order_line, self).create(cr, uid, vals, context=context)
        if not context.get('copu'):
            if vals.get("is_variant",False):
                ir_model_data = self.pool.get('ir.model.data')
                product_name = vals.get('name')
                # Imprint Method to add in description
                imprint_method = False
                if vals.get('imprint_method'):
                    imprint_method = dimension_pool.browse(cr, uid, vals.get('imprint_method')).name
                product_uom = ir_model_data.get_object_reference(cr, uid, 'product', "product_uom_hour")[1]
                prod_c_name = {'setup_charge': "Setup Charge",'up_charge': "Up Charge",'ltm_charge': "LTM Charge",'pms_charge': "PMS Charge",'run_charge': "Run Charge"}
                for cname in ['setup_charge','up_charge','ltm_charge','pms_charge','run_charge']:
                    product_id = ir_model_data.get_object_reference(cr, uid, 'ob_product_variant', "product_product_" + cname + "_service")[1]
                    c_charge = vals.get(cname,False)
                    if c_charge:
                        c_vals = {
                            'name' : imprint_method and '[' + imprint_method + '] ' + prod_c_name.get(cname) + " - " + product_name or prod_c_name.get(cname) + " - " + product_name,
                            'product_id' : product_id,
                            'product_uom_qty' : 1,
                            'product_uos_qty' : 1,
                            'product_uom' : product_uom,
                            'price_unit' : c_charge,
                            'is_variant' : False,
                            'product_uos': False,
                            'is_charge_service' : True,
                            'parent_order_line_id' : res or res[0],
                            'order_id' : vals.get('order_id'), 
                        }
                        new_id = self.pool.get('sale.order.line').create(cr, uid, c_vals, context=context)
        return res

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        if not context:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        values = super(sale_order_line, self).read(cr, uid, ids, fields, context, load)
        for val in values:
            imprint_data = val.get('imprint_data', False)
            
            if imprint_data:
                val.update(eval(imprint_data))
        if isinstance(ids, (int, long)):
            values = values[0]
        return values

    def unlink(self, cr, uid, ids, context=None):
        ir_model_data = self.pool.get('ir.model.data')
        if not context.get('from_unlink_itself',False) and context.get('from_write_itself',False):
            return super(sale_order_line, self).unlink(cr, uid, ids, context=context)
        if isinstance(ids, (int, long)):
            ids = [ids]
        service_line_ids = []
        # Search if Order Line exist or not
        ids = self.search(cr, uid, [('id', 'in', ids)])
        for line_rec in self.browse(cr, uid, ids, context=context):
            if line_rec.is_variant:
                service_line_ids += self.search(cr, uid, [('parent_order_line_id','=', line_rec.id)], context=context)
            if line_rec.is_charge_service and not 'delete_from_copy' in context:
                charges_dict = {}
                for cname in ['setup_charge','up_charge','ltm_charge','pms_charge','run_charge']:
                    product_id = ir_model_data.get_object_reference(cr, uid, 'ob_product_variant', "product_product_" + cname + "_service")[1]
                    if line_rec.product_id.id == product_id:
                        charges_dict.update({cname:0.0})
                context.update({'from_write_itself': True, 'from_unlink_itself': True})
                self.write(cr, uid, [line_rec.parent_order_line_id.id], charges_dict, context=context)
        return super(sale_order_line, self).unlink(cr, uid, ids + service_line_ids, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        dimension_pool = self.pool.get('product.variant.dimension.type')
        sale_order_obj = self.pool.get("sale.order")
        order_line_ids = []
        if context is None:
            context = {}
        context = context.copy()
        imprint_data = {}
        ir_model_data = self.pool.get('ir.model.data')
        sale_order_obj = self.pool.get("sale.order")
        if context.get('from_write_itself',False) and context.get('from_update_itself',False):
            context.pop('from_write_itself')
            context.pop('from_update_itself')
            return True
        if context.get('from_write_itself',False) or context.get('from_update_itself',False):
            if context.get('from_write_itself'):
                context.pop('from_write_itself')
            if context.get('from_update_itself'):
                context.pop('from_update_itself')        
            return super(sale_order_line, self).write(cr, uid, ids, vals, context=context)
        prod_c_name = {'setup_charge': "Setup Charge",'up_charge': "Up Charge",'ltm_charge': "LTM Charge",'pms_charge': "PMS Charge",'run_charge': "Run Charge"}
        # Search if Order Line exist or not
        if isinstance(ids, list):
            ids = self.search(cr, uid, [('id', 'in', ids)])
        if isinstance(ids, (int, long)):
            ids = self.search(cr, uid, [('id', '=', ids)])
        for rec in self.browse(cr, uid, ids, context=context):
            imprint_data_fields = vals.get('imprint_data_fields', False)
            if not imprint_data_fields:
                imprint_data_fields = rec.imprint_data_fields
            if not imprint_data_fields:
                continue
            imprint_data_fields = eval(imprint_data_fields)
            # To update Imprint_data field with new or existing imprint_data_fields values
            if rec.imprint_data:
                rec_imprint_data = eval(rec.imprint_data)
            else:
                rec_imprint_data = False        
            for field in imprint_data_fields:
                if vals.get(field, False):
                    imprint_data.update({field: vals.get(field)})
                    vals.pop(field)
                    vals.update({'imprint_data': str(imprint_data)})
                elif not vals.get(field, False) and rec_imprint_data and rec_imprint_data.get(field, False):
                    imprint_data.update({field: rec_imprint_data.get(field)})
                    vals.update({'imprint_data': str(imprint_data)})                
            # Imprint Method Name from vals
            imprint_method = False
            if vals.get('imprint_method'):
                imprint_method = dimension_pool.browse(cr, uid, vals.get('imprint_method')).name
                
            if 'is_variant' in vals:
                if vals.get('is_variant',False):
                    product_name = vals.get('name')
                    product_uom = ir_model_data.get_object_reference(cr, uid, 'product', "product_uom_hour")[1]
                    for cname in ['setup_charge','up_charge','ltm_charge','pms_charge','run_charge']:
                        product_id = ir_model_data.get_object_reference(cr, uid, 'ob_product_variant', "product_product_" + cname + "_service")[1]
                        c_charge = vals.get(cname,False)
                        if c_charge:
                            setup_vals = {
                                'name' : imprint_method and '[' + imprint_method + '] ' + prod_c_name.get(cname) + " - " + product_name or prod_c_name.get(cname) + " - " + product_name,
                                'product_id' : product_id,
                                'product_uom_qty' : 1,
                                'product_uos_qty' : 1,
                                'product_uom' : product_uom,
                                'price_unit' : c_charge,
                                'is_variant' : False,
                                'product_uos': False,
                                'is_charge_service' : True,
                                'parent_order_line_id' : rec.id,
                                'order_id' : rec.order_id.id,
                            }
                            new_id = self.pool.get('sale.order.line').create(cr, uid, setup_vals, context=context)
                else:
                    child_order_line_ids = self.search(cr, uid, [('parent_order_line_id','=',rec.id)], context=context)
                    for child_id in child_order_line_ids:
                        context.update({'from_write_itself':True})
                        context.update({'from_update_itself':True})
                        self.pool.get("sale.order").write(cr, uid, [rec.order_id.id], {'order_line': [(2, child_id, False)]}, context=context)
            else:
                if rec.is_variant:
                    for cname in ['setup_charge','up_charge','ltm_charge','pms_charge','run_charge']:
                        product_id = ir_model_data.get_object_reference(cr, uid, 'ob_product_variant', "product_product_" + cname + "_service")[1]
                        # Imprint Method Name from existing record
                        if not vals.get('imprint_method') and rec.imprint_method:
                            imprint_method = rec.imprint_method.name
                            
                        product_uom = ir_model_data.get_object_reference(cr, uid, 'product', "product_uom_hour")[1]
                        order_line_ids = self.search(cr, uid, [('parent_order_line_id','=',rec.id),('product_id','=',product_id)], context=context)
                        if cname in vals:
                            c_charge = vals.get(cname,False)
                            if c_charge:
                                p_name = vals.get('name',False)
                                if not p_name:
                                    p_name = rec.name
                                new_vals = {
                                    'price_unit': c_charge,
                                    'name' : imprint_method and '[' + imprint_method + '] ' + prod_c_name.get(cname) + " - " + p_name or prod_c_name.get(cname) + " - " + p_name,
                                }
                                context.update({'from_write_itself':True})
                                if order_line_ids:
                                    new_res = self.write(cr, uid, order_line_ids, new_vals, context=context)
                                else:
                                    setup_vals = {
                                        'name' : imprint_method and '[' + imprint_method + '] ' + prod_c_name.get(cname) + " - " + p_name or prod_c_name.get(cname) + " - " + p_name,
                                        'product_id' : product_id,
                                        'product_uom_qty' : 1,
                                        'product_uos_qty' : 1,
                                        'product_uom' : product_uom,
                                        'price_unit' : c_charge,
                                        'is_variant' : False,
                                        'product_uos': False,
                                        'is_charge_service' : True,
                                        'parent_order_line_id' : rec.id,
                                        'order_id' : rec.order_id.id,
                                    }
                                    new_id = self.pool.get('sale.order.line').create(cr, uid, setup_vals, context=context)
                            else:
                                cntx = context.copy()
                                cntx.update({'from_write_itself':True})
                                cntx.update({'from_update_itself':True})
                                if order_line_ids:
                                    self.pool.get("sale.order").write(cr, uid, [rec.order_id.id], {'order_line': [(2, order_line_ids[0])]}, context=cntx)
                        else:
                            if 'name' in vals and order_line_ids:
                                line_rec = self.browse(cr, uid, order_line_ids, context=context)[0]
                                new_vals = {
                                    'name' : imprint_method and '[' + imprint_method + '] ' + prod_c_name.get(cname) + " - " + vals.get('name','') or prod_c_name.get(cname) + " - " + vals.get('name',''),
                                }
                                new_res = self.write(cr, uid, order_line_ids, new_vals, context=context)
                            # Update Imprint Method name in service product description if method changed
                            if vals.get('imprint_method') and order_line_ids:
                                p_name = vals.get('name',False)
                                imprint_method = dimension_pool.browse(cr, uid, vals.get('imprint_method')).name
                                if not p_name:
                                    p_name = rec.name
                                    
                                new_vals = {
                                    'name' : imprint_method and '[' + imprint_method + '] ' + prod_c_name.get(cname) + " - " + p_name or prod_c_name.get(cname) + " - " + p_name,
                                }
                                new_res = self.write(cr, uid, order_line_ids, new_vals, context=context)
                                
                if rec.is_charge_service and 'price_unit' in vals:
                    for cname in ['setup_charge','up_charge','ltm_charge','pms_charge','run_charge']:
                        product_id = ir_model_data.get_object_reference(cr, uid, 'ob_product_variant', "product_product_" + cname + "_service")[1]
                        if product_id == rec.product_id.id:
                            context = dict(context)
                            context.update({'from_write_itself':True})
                            new_res = self.write(cr, uid, [rec.parent_order_line_id.id], {cname: vals.get('price_unit')}, context=context)
        res = super(sale_order_line, self).write(cr, uid, ids, vals, context=context)
        return res
    
    def onchange_is_blank_order(self, cr, uid, ids, imprint_data, context=None):
        res = {}
        context = context or {}
        res['value'] = {'imprint_method': None,'setup_charge':0.0, 'run_charge':0.0, 'up_charge':0.0, 'ltm_charge':0.0, 'pms_charge':0.0}
        return res
    
    def onchange_product_qty(self, cr, uid, ids, charges_data, qty=0, context=None):
        context = context or {}
        res = {}
        c_data = {}
        if charges_data:
            c_data = eval(charges_data)
        c_data.update({'qty': qty})
        res['value'] = {'charges_data': str(c_data)}
        return res

    def onchange_imprint_method(self, cr, uid, ids, product_id, imprint_method, qty=False, context=None):
        if not context:
            context = {}
        vals = {}
        setup_charge_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ob_product_variant', 'product_variant_setup_charge')[1]
        run_charge_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ob_product_variant', 'product_variant_run_charge')[1]
        if product_id:
            product_obj = self.pool.get('product.product')
            product_rec = product_obj.browse(cr, uid, [product_id], context=context)[0]
            keys = []
            for product_dimension_type_rec in product_rec.product_tmpl_id.product_dimension_type_ids:
                field_name = product_dimension_type_rec.product_dimension_id2.name
                if not imprint_method and product_dimension_type_rec.product_dimension_id2.attribute_field_type != 'none':
                    
                    int_obj = re.findall(r'\d+',field_name)
                    if int_obj:
                        from num_to_word import int2word
                        word = int2word(int(int_obj[0]))
                        word = word.strip()
                        space_removed = word.replace(' ', '_')  #word.split(' ').join('_')
                        whole_word = space_removed.replace('-', '_')  #space_removed.split('-').join('_')
                        field_name = field_name.replace(int_obj[0], whole_word.strip())
                        field_name = field_name.replace('-','_')#field_name.split('-').join('_')
                        field_name = field_name.replace("__", "_")
#                         field_name = field_name.replace(" ", "_")
#                     keys.append(field_name)
                    keys.append(str(field_name).lower().replace(" ","_"))
                if product_dimension_type_rec.product_dimension_id2.attribute_field_type != 'none' \
                        and imprint_method in [child_id.id for child_id in product_dimension_type_rec.product_dimension_child_ids]:
                    
                    int_obj = re.findall(r'\d+',field_name)
                    if int_obj:
                        from num_to_word import int2word
                        word = int2word(int(int_obj[0]))
                        word = word.strip()
                        space_removed = word.replace(' ', '_')  #word.split(' ').join('_')
                        whole_word = space_removed.replace('-', '_')  #space_removed.split('-').join('_')
                        field_name = field_name.replace(int_obj[0], whole_word.strip())
                        field_name = field_name.replace('-','_')#field_name.split('-').join('_')
                        field_name = field_name.replace("__", "_")
#                         field_name = field_name.replace(" ", "_")
#                     keys.append(field_name)
                    keys.append(str(field_name).lower().replace(" ","_"))
                    if product_dimension_type_rec.dimension_type == 'color':
                        vals.update({'line_attr_max_val': product_dimension_type_rec.attribute_max_value})
                        for charge in product_dimension_type_rec.attribute_to_charge_ids:
                            if setup_charge_id == charge.product_charges_id.id:
                                vals.update({'line_no_of_free_color': charge.max_free_attributes})

                    if product_dimension_type_rec.dimension_type == 'side':
                        for charge in product_dimension_type_rec.attribute_to_charge_ids:
                            if run_charge_id == charge.product_charges_id.id:
                                vals.update({'line_no_of_free_side': charge.max_free_attributes})
            for key in keys:
                vals.update({key: False})
                vals.update({'pms_code': False})
            vals.update({"imprint_data_fields": str(keys)})
        if qty:
            c_data = {'qty': qty}
            vals.update({"charges_data": str(c_data)})
        vals.update({
            'line_no_of_color': 0,
            'line_no_of_pms_code': 0,
            'line_no_of_position': 0,
        })
        return {'value': vals}

    def calculate_pms_code(self, cr, uid, ids, product_id, pms_code, context=None):
        if not context:
            context = {}
        pms_charge = 0.0
        if product_id:
            product_obj = self.pool.get('product.product')
            product_rec = product_obj.browse(cr, uid, [product_id], context=context)[0]
            pms_charge = product_rec.pms_charge
            if pms_code:
                pms_code = pms_code[0][2]
                pms_charge = len(pms_code) * pms_charge
        return pms_charge

    def onchange_imprint_method_fields(self, cr, uid, ids, product_id, charges_data, field_value, field_id, line_no_of_color, line_no_of_pms_code, line_no_of_free_color, line_no_of_free_side, imprint_method_id, pms_code=False, context=None):
        c_data = {}
        vals = {}
        if charges_data:
            c_data = eval(charges_data)
        if pms_code:
            pms_charge = self.calculate_pms_code(cr, uid, ids, product_id, pms_code, context=context)
            c_data.update({'pms_code': pms_code[0][2]})
            vals.update({
                'pms_charge': pms_charge,
                'line_no_of_pms_code': len(pms_code[0][2])
            })
            product_obj = self.pool.get('product.product')
            product_rec = product_obj.browse(cr, uid, [product_id], context=context)[0]
            for dimension_type in product_rec.product_tmpl_id.product_dimension_type_ids:
                if imprint_method_id in [child_id.id for child_id in dimension_type.product_dimension_child_ids]:
                    if dimension_type.attribute_max_value:
                        if dimension_type.dimension_type == 'color':
                            pms_codes = c_data.get('pms_code', [])
                            color_codes = c_data.get(dimension_type.product_dimension_id2.id, [])
                            limit_attrs = len(pms_codes) + len(color_codes)
                            if dimension_type.attribute_max_value < limit_attrs:
                                return {}

        if field_value:
            product_obj = self.pool.get('product.product')
            product_rec = product_obj.browse(cr, uid, [product_id], context=context)[0]
            if isinstance(field_value, list):
                field_value = field_value[0][2]
                for dimension_type in product_rec.product_tmpl_id.product_dimension_type_ids:
                    if imprint_method_id in [child_id.id for child_id in dimension_type.product_dimension_child_ids]:
                        if dimension_type.product_dimension_id2.id == field_id:
                            limit_attrs = len(field_value)
                            if dimension_type.dimension_type == 'color':
                                pms_codes = c_data.get('pms_code',[])
                                limit_attrs += len(pms_codes)
                                vals.update({'line_no_of_color': len(field_value)})
                            if dimension_type.dimension_type == 'side':
                                vals.update({'line_no_of_position': len(field_value)})
                            if dimension_type.attribute_max_value and dimension_type.attribute_max_value < limit_attrs:
                                return {}
                if field_value:
                    c_data.update({field_id: field_value})
                else:
                    if field_id in c_data.keys():
                        c_data.pop(field_id)
            else:
                c_data.update({field_id: field_value})
        vals.update({'charges_data': str(c_data)})
        return {'value': vals}

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False,
                          name='', partner_id=False, lang=False, update_tax=True, date_order=False,
                          packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        product_obj = self.pool.get('product.product')
        value = res.get('value', {})
        value.update({
                'p_qty': qty
            })
        if not flag:
            value.update({
                'setup_charge': 0.0,
                'run_charge': 0.0,
                'imprint_method': False,
                'is_variant': False,
                'line_no_of_color': 0,
                'line_no_of_pms_code': 0,
                'line_no_of_position': 0,
                'line_no_of_free_color': 0,
                'line_no_of_free_side': 0,
                'line_attr_max_val': 0,
                'is_charge_service': False,
                'imprint_data_fields': "[]",
            })
        else:
            value.update({
                'temp_qty': qty
            })
        if product:
            product_rec = product_obj.browse(cr, uid, [product], context=context)[0]
            value.update({'up_charge': product_rec.up_charge})
            value.update({'is_charge_service': product_rec.is_charge_service})
            if qty < product_rec.min_qty_ltm:
                value.update({'ltm_charge': product_rec.ltm_charge})
            else:
                value.update({'ltm_charge': 0.00})
            if not flag:
                if not product_rec.is_variant:
                    value.update({'imprint_method': False})
                has_imprint_method = False
                for dimension in product_rec.product_tmpl_id.product_dimension_type_ids:
                    if dimension.product_dimension_id2.attribute_field_type == 'none':
                        has_imprint_method = True
                value.update({'has_imprint_method': has_imprint_method})
                value.update({'is_variant': product_rec.is_variant})
                if not product_rec.apply_pms_charge:
                    value.update({'pms_code': False})
                value.update({'apply_pms_charge': product_rec.apply_pms_charge})
        res['value'] = value
        return res

    def line_calculate_charges(self, cr, user, ids, product_id, line_no_of_pms_code, line_no_of_color, line_no_of_position, line_no_of_free_color, line_no_of_free_side, charges_data, imprint_method, qty, context=None):
        return self.pool.get('calculate.charge').line_calculate_charges(cr, user, ids, product_id, line_no_of_pms_code, line_no_of_color, line_no_of_position, line_no_of_free_color, line_no_of_free_side, charges_data, imprint_method, qty, context=context)
