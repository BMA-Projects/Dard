# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import fields, osv, orm
import logging


_logger = logging.getLogger(__name__)


class product_product(osv.osv):

    _inherit = "product.product"

    _columns = {
        'product_web_id': fields.char('WebIDitem'),
        'serial_no': fields.char('Serial Number', size=15, help="Serial number is a unique code assigned for identification of Product."),
        'processing_days': fields.integer('Processing Days', help="Product requires some days to process order."),
        'ltm_charge': fields.float('LTM Charge'),
        'min_qty_ltm': fields.integer('Min Qty LTM', help="Minimum qty to apply Charges"),
        'pms_charge': fields.float('PMS Charge'),
        'up_charge': fields.float('UP Charge'),
        'is_variant': fields.boolean('Is Variant'),
        'apply_pms_charge': fields.boolean('Apply PMS Charge'),
        'is_charge_service': fields.boolean('Is Charge Service'),
	    'variant_loc_rack': fields.char('Product Rack', size=256),
        'variant_loc_row': fields.char('Product Row', size=256),
        'variant_loc_case': fields.char('Product Case', size=256),
    }

    def fields_get(self, cr, user, allfields=None, context=None, write_access=True, attributes=None):
        res = super(product_product, self).fields_get(cr, user, allfields=None, context=None, write_access=True, attributes=None)
        for location in ['loc_rack','loc_case','loc_row']:
            if res.has_key(location):res[location]['selectable'] = False
        return res
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        cur_rec = self.browse(cr, uid, [id], context=context)[0]
        default.update({'product_tmpl_id': cur_rec.product_tmpl_id.id})
        return super(product_product, self).copy(cr, uid, id, default, context)

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        product_tmpl_id = vals.get('product_tmpl_id')
        if product_tmpl_id:
            product_tmpl_obj = self.pool.get('product.template')
            product_tmpl = product_tmpl_obj.browse(cr, uid, [product_tmpl_id], context=context)[0]
            vals.update({
                'ltm_charge': product_tmpl.ltm_charge,
                'pms_charge': product_tmpl.pms_charge,
                'min_qty_ltm': product_tmpl.min_qty_ltm,
                'apply_pms_charge': product_tmpl.apply_pms_charge,
            })
        attribute_value_ids = vals.get('attribute_value_ids', False)
        product_attr_val_obj = self.pool.get("product.attribute.value")
        if attribute_value_ids and len(attribute_value_ids[0]) > 2:
            attribute_ids = attribute_value_ids[0][2]
            up_charge = 0
            for attribute_id in attribute_ids:
                attribute = product_attr_val_obj.browse(cr, uid, attribute_id, context=context)
                if attribute.up_charge:
                    up_charge += attribute.up_charge
            vals.update({'up_charge': up_charge})
        return super(product_product, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        product_tmpl_id = vals.get('product_tmpl_id')
        if product_tmpl_id:
            product_tmpl_obj = self.pool.get('product.template')
            product_tmpl = product_tmpl_obj.browse(cr, uid, [product_tmpl_id], context=context)[0]
            vals.update({
                'ltm_charge': product_tmpl.ltm_charge,
                'pms_charge': product_tmpl.pms_charge,
                'min_qty_ltm': product_tmpl.min_qty_ltm,
                'apply_pms_charge': product_tmpl.apply_pms_charge,
            })
        return super(product_product, self).write(cr, uid, ids, vals, context=context)

class product_charges(osv.osv):
    _name = "product.charges"
    _description = "Extra Charges on product"

    _columns = {
        'name': fields.char('Charge Name', size=128, required=True),
    }

class product_variant_dimension_type(orm.Model):
    
    _name = "product.variant.dimension.type"
    
    _description = "Dimension Type"

    _columns = {
        'description': fields.char('Description', size=64, translate=True),
        'name': fields.char('Dimension Type Name', size=64, required=True),
        'option_ids': fields.one2many('product.variant.dimension.option', 'dimension_id',
                                      'Dimension Options'),
        'product_tmpl_id': fields.many2many('product.template', 'product_template_dimension_rel',
                                            'dimension_id', 'template_id', 'Product Template'),
        'attribute_field_type': fields.selection([
            ('none', 'None'),
            ('dropdown', 'DropDown'),
            ('multiselection', 'Multi Selection')], 'Attribute Field Type'),
        'dimension_type': fields.selection([('color','Color'),('side','Side')],"Type")
    }

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not context:
            context = {}
        if not args:
            args = []
        ids = []
        
        if context.get('from_sale', False):
            product_id = context.get('product_id', False)
            if not product_id:
                return self.name_get(cr, user, [], context)
            product_obj = self.pool.get("product.product")
            product_rec = product_obj.browse(cr, user, [product_id], context=context)[0]
            for product_dimension in product_rec.product_tmpl_id.product_dimension_type_ids:
                if product_dimension.product_dimension_id2.attribute_field_type == 'none':
                    found_flag = False
                    for product_dimension_child in product_rec.product_tmpl_id.product_dimension_type_ids:
                        if product_dimension_child.product_dimension_id2.attribute_field_type != 'none':
                            child_ids = [x.id for x in product_dimension_child.product_dimension_child_ids]
                            if product_dimension.product_dimension_id2.id in child_ids:
                                found_flag = True
                    if found_flag:
                        ids.append(product_dimension.product_dimension_id2.id)
            return self.name_get(cr, user, ids, context)
        if context.get("from_charges", False):
            product_tmpl_id = context.get('product_tmpl_id',False)
            if not product_tmpl_id:
                return super(product_variant_dimension_type, self).name_search(cr, user, name, args=args, operator=operator, context=context, limit=limit)
            product_tmpl_obj = self.pool.get('product.template')
            product_tmpl_rec = product_tmpl_obj.browse(cr, user, [product_tmpl_id], context=context)[0]
            for attr_to_charge in product_tmpl_rec.attribute_to_charge_ids:
                ids.append(attr_to_charge.product_dim_id.id)
            args += [['id', 'not in', ids]]
        if context.get('from_child', False):
            child_ids = []
            product_tmpl_id = context.get('product_tmpl_id', False)
            if product_tmpl_id:
                product_template_obj = self.pool.get('product.template')
                product_tmpl_rec = product_template_obj.browse(cr, user, [product_tmpl_id], context=context)[0]
                for dim_type in product_tmpl_rec.product_dimension_type_ids:
                    if dim_type.product_dimension_id2.attribute_field_type == 'none':
                        child_ids.append(dim_type.product_dimension_id2.id)
                product_dimension_child_ids = context.get('product_dimension_child_ids')[0][2]
                if product_dimension_child_ids:
                    for child in product_dimension_child_ids:
                        child_ids.remove(child)
                return self.name_get(cr, user, child_ids, context=context)
            else:
                return self.name_get(cr, user, [], context=context)
        return super(product_variant_dimension_type, self).name_search(cr, user, name, args=args, operator=operator, context=context, limit=limit)



class product_dimension_type(osv.osv):
    _name = "product.dimension.type"
    _description = "Product dimension type"
    _rec_name = 'complete_name'

    def _get_full_name(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        vals = self.browse(cr, uid, ids, context=context)
        for val in vals:
            res[val.id] = val.product_dimension_id2.name
        return res

    _columns = {
        'product_dimension_id2': fields.many2one('product.variant.dimension.type','Dimension Type Name',ondelete='cascade'),
        'product_dimension_option_id': fields.many2many('product.variant.dimension.option', 'product_dimension_values', 'dimension_id', 'option_id', 'Dimension Value'),
        'product_tmpl_id': fields.many2many('product.template', 'product_template_dimension_rel',
                                            'dimension_id', 'template_id', 'Product Template'),
        'product_dimension_child_ids': fields.many2many('product.variant.dimension.type', 'product_dimension_type_values', 'dim_child_id', 'dim_parent_id', 'Dimension Type'),
        'product_dim_id': fields.many2one('product.template', 'Template ID', ondelete='cascade'),
        'complete_name': fields.function(_get_full_name, store=True, string="Name", type='char'),
        'attribute_to_charge_ids': fields.one2many('attribute.to.charge', 'product_dimension_type_id', 'Attribute To Charge'),
        'mandatory_dimension': fields.boolean('Mandatory Dimension'),
        'attribute_field_type': fields.char('Attribute Field Type'),
        'attribute_max_value': fields.integer('Attribute Max Value', help="Maximum Attribute value."),
        'dimension_type': fields.selection([('color','Color'),('side','Side')],"Type")
    }

    def onchange_product_dimension(self, cr, uid, ids, product_dimension_id, context=None):
        vals_id = []
        cr.execute('select id from product_variant_dimension_type where attribute_field_type=%s',('none',))
        product_dimentsion_ids = cr.fetchall()
        vals_id = [vals_id[0] for vals_id in product_dimentsion_ids]
        vals = {
            'attribute_field_type': False,
            'product_dimension_option_id': False
        }
        if product_dimension_id:
            product_variant_dimension_type_obj = self.pool.get('product.variant.dimension.type')
            product_variant_dimension_type_rec = product_variant_dimension_type_obj.browse(cr, uid, [product_dimension_id], context=context)[0]
            vals.update({
                'attribute_field_type': product_variant_dimension_type_rec.attribute_field_type,
                'dimension_type': product_variant_dimension_type_rec.dimension_type
            })
        return {
            'value': vals,
            'domain': {'product_dimension_child_ids': [('id', 'in', vals_id)]}
        }

class charges_charges(osv.osv):
    _name = "charges.charges"
    _description = "Charges"

    _columns = {
        'attribute_to_charge_id': fields.many2one('attribute.to.charge', 'Attribute to charge', ondelete='cascade'),
        'from_qty': fields.integer('Quantity Start', required=True),
        'to_qty': fields.integer('Quantity End', required=True),
        'charge_amount': fields.float('Amount to Charge', required=True),
    }

class attribute_to_charge(osv.osv):
    _name = "attribute.to.charge"
    _description = "Attribute to Charge"

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(attribute_to_charge, self).default_get(cr, uid, fields, context=context)
        if context.get('from_charge', False):
            res.update({'attribute_field_type': context.get('attribute_field_type',False)})
        return res

    _columns = {
        'product_charges_id': fields.many2one('product.charges', 'Charge Type', required=True, ondelete='cascade'),
        'product_dimension_type_id': fields.many2one('product.dimension.type', 'Product Dimension Type', ondelete='cascade',),
        'per_qty': fields.boolean('Per Quantity'),
        'per_dim_value': fields.boolean('Per Dimension Value'),
        'amount_charge': fields.float('Amount'),
        'charges_id': fields.one2many('charges.charges', 'attribute_to_charge_id', 'Charges'),
        'max_free_attributes': fields.integer('Max Free Attributes', help="Maximum Free Attribute."),
        'product_dim_id': fields.many2one('product.variant.dimension.type', 'Dimension Type Name', ondelete='cascade'),
        'product_dim_op_id': fields.many2many('product.variant.dimension.option', 'product_dimension_option_values', 'dimension_id', 'option_id', 'Dimension Value'),
        'attribute_field_type': fields.char('Attribute Field Type'),
        'benefit': fields.boolean('Benefit', help='To apply benefit for free attribute, for particular amount consider this charge.'),
        'is_both_side': fields.boolean('Is Both Side', help="This field is decide the charge will apply for both side if and only if the selected attribute will be selection field and added the option for both side. e.g. If there is a selection field and that will be contain the options like. front side, both side. So, for the setting up the charges for both side this fields shuold be true."),
    }


class pms_code(osv.osv):
    _name = "pms.code"
    _columns = {
        'name': fields.char('PMS Code')
    }
    
    _sql_constraints = [
        ('pms_name_unique', 'unique (name)', 'You can not enter duplicate PMS Code !')
    ]

class product_template(orm.Model):

    _inherit = "product.template"

    _columns = {
        'ltm_charge': fields.float('LTM Charge'),
        'pms_charge': fields.float('PMS Charge'),
        'min_qty_ltm': fields.integer('Min Qty LTM', help="Minimum qty to apply Charges"),
        'product_dimension_type_ids': fields.one2many('product.dimension.type', 'product_dim_id', 'Dimension Types'),
        'apply_pms_charge': fields.boolean('Apply PMS Charge'),
        'is_variant': fields.boolean('Has Dimension')
    }
    
    def fields_get(self, cr, user, allfields=None, context=None, write_access=True, attributes=None):
        res = super(product_template, self).fields_get(cr, user, allfields=None, context=None, write_access=True, attributes=None)
        for location in ['loc_rack','loc_case','loc_row']:
            if res.has_key(location):res[location]['selectable'] = False
        return res
    
    def write(self, cr, uid, ids, values, context=None):
        if context is None:
            context = {}

        res = super(product_template, self).write(cr, uid, ids, values, context=context)
        if 'attribute_line_ids' in values:
            flag = True
            for vls in values.get('attribute_line_ids'):
                if vls[0]==1:
                    if 'value_ids' in vls[2]:
                        for val_id in vls[2].get('value_ids'):
                            if val_id[0]==6 and val_id[2]:
                                flag=False
            if flag:
                return res
        for cur_rec in self.browse(cr, uid, ids, context=context):
            ltm_charge = cur_rec.ltm_charge
            pms_charge = cur_rec.pms_charge
            min_qty_ltm = cur_rec.min_qty_ltm
            apply_pms_charge = cur_rec.apply_pms_charge
            product_obj = self.pool.get('product.product')
            if isinstance(ids, (int, long)):
                ids= [ids]
            product_ids = product_obj.search(cr, uid, [('product_tmpl_id', 'in', ids)], context=context) or []
            for product in product_ids:
                product_obj.write(cr, uid, [product], {
                    'is_variant': cur_rec.is_variant,
                    'ltm_charge': ltm_charge,
                    'pms_charge': pms_charge,
                    'min_qty_ltm': min_qty_ltm,
                    'apply_pms_charge': apply_pms_charge}, context=context)
        return res

    def add_all_option(self, cr, uid, ids, context=None):
        value_obj = self.pool.get('product.variant.dimension.value')
        for template in self.browse(cr, uid, ids, context=context):
            values_ids = value_obj.search(cr, uid, [['product_tmpl_id', '=', template.id],
                                                    '|', ['active', '=', False],
                                                         ['active', '=', True]], context=context)
            value_obj.write(cr, uid, values_ids,
                            {'active': True},
                            context=context)
            values = value_obj.browse(cr, uid, values_ids, context=context)
            existing_option_ids = [value.option_id.id for value in values]
            vals = {'value_ids': []}
            for dim in template.product_dimension_type_ids:
                if dim.product_dimension_id2.mandatory_dimension:
                    for option in dim.product_dimension_option_id:
                        if not option.id in existing_option_ids:
                            vals['value_ids'] += [[0, 0, {'option_id': option.id}]]
            self.write(cr, uid, [template.id], vals, context=context)
        return True

    def button_generate_variants(self, cr, uid, ids, context=None):
        ltm_charge = self.browse(cr, uid, ids, context)[0].ltm_charge
        pms_charge = self.browse(cr, uid, ids, context)[0].pms_charge
        min_qty_ltm = self.browse(cr, uid, ids, context)[0].min_qty_ltm
        apply_pms_charge = self.browse(cr, uid, ids, context)[0].apply_pms_charge
        context.update({'ltm_charge': ltm_charge, 'pms_charge': pms_charge, 'min_qty_ltm': min_qty_ltm, 'apply_pms_charge': apply_pms_charge})
        res = super(product_template, self).button_generate_variants(cr, uid, ids, context=context)
        return res

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        cur_rec = self.browse(cr, uid, [id], context=context)[0]
        default.update({'name': cur_rec.name + " (copy)"})
        new_id = super(product_template, self).copy(cr, uid, id, default, context)
        return new_id


class ProductVariantDimensionOption(osv.osv):

    _name = "product.variant.dimension.option"
    _description = "Dimension Option"

    def _get_dimension_values(self, cr, uid, ids, context=None):
        dimvalue_obj = self.pool.get('product.variant.dimension.value')
        return dimvalue_obj.search(cr, uid, [('dimension_id', 'in', ids)], context=context)

    _columns = {
        'name': fields.char('Dimension Option Name', size=256, required=True),
        'code': fields.char('Code', size=64),
        'sequence': fields.integer('Sequence'),
        'dimension_id': fields.many2one('product.variant.dimension.type',
                                        'Dimension Type', ondelete='cascade'),
    }

    _order = "dimension_id, sequence, name"

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not context:
            context = {}
        if not args:
            args = []

        if context.get('from_charges', False):
            option_ids = context.get('product_dim_option_id')[0][2]
            charges_option_ids = context.get('product_dim_op_id')[0][2]
            for charges_op in charges_option_ids:
                option_ids.remove(charges_op)
            return self.name_get(cr, user, option_ids, context=context)

        if context.get('from_sale', False):
            product_id = context.get('product_id',False)
            dimension_type_id = context.get('dimension_type_id',False)
            imprint_method = context.get('imprint_method', False)

            if not product_id or not dimension_type_id or not imprint_method:
                return self.name_get(cr, user, [], context)
            product_obj = self.pool.get("product.product")
            product_rec = product_obj.browse(cr, user, [product_id], context=context)[0]
            ids = []
            for product_dimension in product_rec.product_tmpl_id.product_dimension_type_ids:
                child_ids = [child.id for child in product_dimension.product_dimension_child_ids]
                if product_dimension.product_dimension_id2.id == dimension_type_id and imprint_method in child_ids:
                    for option in product_dimension.product_dimension_option_id:
                        ids.append(option.id)
            option_ids = context.get('options', False)
            if isinstance(option_ids, list):
                option_ids = option_ids[0][2]
                for option in option_ids:
                    if option in ids:
                        ids.remove(option)
            return self.name_get(cr, user, ids, context)
        return super(ProductVariantDimensionOption, self).name_search(cr, user, name, args=args, operator=operator, context=context, limit=limit)


class product_attribute_value(osv.osv):
    _inherit = "product.attribute.value"

    _columns = {
        'up_charge': fields.float('Up Charge'),
    }

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        product_obj = self.pool.get('product.product')
        if 'up_charge' in vals and context.get('active_model', False) == 'product.template' and 'active_id' in context:
            for rec in self.browse(cr, uid, ids, context=context):
                for product_id in rec.product_ids:
                    if product_id.product_tmpl_id.id == context.get('active_id'):
                        new_charge = 0
                        for attribute_value_id in product_id.attribute_value_ids:
                            if attribute_value_id.id == rec.id:
                                new_charge += vals.get('up_charge')
                            else:
                                new_charge += attribute_value_id.up_charge
                        product_obj.write(cr, uid, product_id.id, {'up_charge': new_charge}, context=context)
        res = super(product_attribute_value, self).write(cr, uid, ids, vals, context=context)
        return res
