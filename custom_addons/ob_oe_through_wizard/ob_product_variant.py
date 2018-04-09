# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, api, fields, _

class product_variant_dimension_type(models.Model):
    
    _inherit = "product.variant.dimension.type"

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        template_obj = self.env['product.template']
        res = super(product_variant_dimension_type, self).name_search(name, args=None, operator='ilike', limit=100)
        context = self._context.copy()
        if 'from_wizard' in context and context['from_wizard'] and 'product_template_id' in context and context['product_template_id']:
            dim_ids = template_obj.browse(context['product_template_id']).product_dimension_type_ids
            dim_type_ids = []
            for dim_id in dim_ids:
                if dim_id.product_dimension_id2.attribute_field_type == "none":
                    dim_type_ids.append(dim_id.product_dimension_id2.id)
            return super(product_variant_dimension_type, self).name_search(name, args=[('id','in',dim_type_ids)], operator='ilike', limit=100)
        return super(product_variant_dimension_type, self).name_search(name, args=None, operator='ilike', limit=100)


class product_variant_dimension_option(models.Model):
    
    _inherit = "product.variant.dimension.option"

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        context = self._context.copy()
        template_obj = self.env['product.template']
        product_obj = self.env['product.product']
        prod_dim_type_obj = self.env['product.dimension.type']
        if 'from_oe_wizard' in context and context['from_oe_wizard'] and 'dim_type_id' in context and context['dim_type_id'] and context.get('product_id', False):
            product = product_obj.browse(context['product_id'])
            template_id = product.product_tmpl_id.id
            dim_type_ids = template_obj.browse(template_id).product_dimension_type_ids
            dim_options = []
            for dim_type_id in dim_type_ids:
                if dim_type_id.product_dimension_id2.id == context['dim_type_id']:
                    for dim_option in dim_type_id.product_dimension_option_id:
                        if 'dim_option_ids' in context and context['dim_option_ids']:
                            if context['dim_option_ids'] and context['dim_option_ids'][0] and \
                                context['dim_option_ids'][0][2] and dim_option.id in context['dim_option_ids'][0][2]:
                                pass
                            else:
                                dim_options.append(dim_option.id)
            return super(product_variant_dimension_option, self).name_search(name, args=[('id','in',dim_options)], operator=operator, limit=100)                
        return super(product_variant_dimension_option, self).name_search(name, args=args, operator=operator, limit=100)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: