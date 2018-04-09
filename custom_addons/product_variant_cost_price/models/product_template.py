# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def create_variant_ids(self):
        """Write in the new created variants the current template cost price.
        """
        variants_per_template = {}
        for template in self:
            variants_per_template[template] = (
                template.standard_price, template.product_variant_ids)
        obj = self.with_context(bypass_down_write=True)
        res = super(ProductTemplate, obj).create_variant_ids()
        for template in self:
            (template.product_variant_ids -
             variants_per_template[template][1]).write(
                {'standard_price': variants_per_template[template][0]})
        return res

    @api.multi
    def write(self, vals):
        """Propagate to the variants the template cost price (if modified)."""
        res = super(ProductTemplate, self).write(vals)
        if ('standard_price' in vals and
                not self.env.context.get('bypass_down_write')):
            self.mapped('product_variant_ids').write(
                {'standard_price': vals['standard_price']})
        return res

    def get_history_price(self, cr, uid, product_tmpl, company_id, date=None, context=None):
        if context is None:
            context = {}
        if date is None:
            date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        price_history_obj = self.pool.get('product.price.history')
        product_obj = self.pool.get('product.product')
        products = product_obj.search(cr, uid, [('product_tmpl_id','=',product_tmpl)])
        
        if context.get('inventory_product_id'):
            product_id = context['inventory_product_id']
            price_history_product_obj = self.pool.get('product.price.history.product')
            history_ids_product = price_history_product_obj.search(cr, uid, [('company_id', '=', company_id), ('product_id', '=', product_id.id), ('datetime', '<=', date)], limit=1)
            if history_ids_product:                    
                return price_history_product_obj.read(cr, uid, history_ids_product[0], ['cost'], context=context)['cost']
          
        else:
            history_ids = price_history_obj.search(cr, uid, [('company_id', '=', company_id), ('product_template_id', '=', product_tmpl), ('datetime', '<=', date)], limit=1)
            if history_ids:
                return price_history_obj.read(cr, uid, history_ids[0], ['cost'], context=context)['cost']
          
        return 0.0
