# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime
from openerp.addons.product._common import rounding

class product_pricelist_item(osv.osv):

    def _price_field_get(self, cr, uid, context=None):
        result = super(product_pricelist_item, self)._price_field_get(cr, uid, context)
        result.append((-3, _('Fixed Price')))
        return result

    _inherit = "product.pricelist.item"

    _columns = {
        'fixed_price': fields.float('Fixed Price',
            digits_compute= dp.get_precision('Sale Price')),
        'base': fields.selection(_price_field_get, 'Based on', required=True, size=-1, help="The mode for computing the price for this rule."),
        }

product_pricelist_item()

class product_pricelist(osv.osv):
    _inherit = "product.pricelist"


    def _price_rule_get_multi(self, cr, uid, pricelist, products_by_qty_by_partner, context=None):
        context = context or {}
        for i,j,k in products_by_qty_by_partner:
            product_qty=j
        date = context.get('date') or time.strftime('%Y-%m-%d')

        products = map(lambda x: x[0], products_by_qty_by_partner)
        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.template')
        product_uom_obj = self.pool.get('product.uom')
        price_type_obj = self.pool.get('product.price.type')

        if not products:
            return {}

        version = False
        for v in pricelist.version_id:
            if ((v.date_start is False) or (v.date_start <= date)) and ((v.date_end is False) or (v.date_end >= date)):
                version = v
                break
        if not version:
            raise osv.except_osv(_('Warning!'), _("At least one pricelist has no active version !\nPlease create or activate one."))
        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = categ_ids.keys()

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            prod_ids = [product.id for product in tmpl.product_variant_ids for tmpl in products]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]
        
        # Load all rules
        cr.execute(
            'SELECT i.id '
            'FROM product_pricelist_item AS i '
            'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = any(%s)) '
                'AND (product_id IS NULL OR (product_id = any(%s))) '
                'AND ((categ_id IS NULL) OR (categ_id = any(%s))) '
                'AND (price_version_id = %s) '
            'ORDER BY sequence, min_quantity desc',
            (prod_tmpl_ids, prod_ids, categ_ids, version.id))
        
        item_ids = [x[0] for x in cr.fetchall()]
        items = self.pool.get('product.pricelist.item').browse(cr, uid, item_ids, context=context)

        price_types = {}
        
        results = {}
        for product, qty, partner in products_by_qty_by_partner:
            results[product.id] = 0.0
            rule_id = False
            price = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = product_uom_obj._compute_qty(
                        cr, uid, context['uom'], qty, product.uom_id.id or product.uos_id.id)
                except except_orm:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass
            for rule in items:
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id:
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue
                
                if rule.base == -1:
                    if rule.base_pricelist_id:
                        price_tmp = self._price_get_multi(cr, uid,
                                rule.base_pricelist_id, [(product,
                                qty, False)], context=context)[product.id]
                        ptype_src = rule.base_pricelist_id.currency_id.id
                        price_uom_id = qty_uom_id
                        price = currency_obj.compute(cr, uid,
                                ptype_src, pricelist.currency_id.id,
                                price_tmp, round=False,
                                context=context)
                elif rule.base == -2:
                    seller = False
                    for seller_id in product.seller_ids:
                        if (not partner) or (seller_id.name.id != partner):
                            continue
                        seller = seller_id
                    if not seller and product.seller_ids:
                        seller = product.seller_ids[0]
                    if seller:
                        qty_in_seller_uom = qty
                        seller_uom = seller.product_uom.id
                        if qty_uom_id != seller_uom:
                            qty_in_seller_uom = product_uom_obj._compute_qty(cr, uid, qty_uom_id, qty, to_uom_id=seller_uom)
                        price_uom_id = seller_uom
                        for line in seller.pricelist_ids:
                            if line.min_quantity <= qty_in_seller_uom:
                                price = line.price
                elif rule.base == -3:
                    if int(product_qty)==rule.min_quantity or int(product_qty) >= rule.min_quantity :
                        price=rule.fixed_price
                        rule_id=rule.id
                        price = product_uom_obj._compute_price(cr, uid, price_uom_id, price, qty_uom_id)
                        results[product.id] = (price, rule_id)
                        return results
                    else:
                        continue

                else:
                    if rule.base not in price_types:
                        price_types[rule.base] = price_type_obj.browse(cr, uid, int(rule.base))
                    price_type = price_types[rule.base]

                    # price_get returns the price in the context UoM, i.e. qty_uom_id
                    price_uom_id = qty_uom_id
                    price = currency_obj.compute(
                            cr, uid,
                            price_type.currency_id.id, pricelist.currency_id.id,
                            product_obj._price_get(cr, uid, [product], price_type.field, context=context)[product.id],
                            round=False, context=context)

                if price is not False:
                    price_limit = price
                    price = price * (1.0+(rule.price_discount or 0.0))
                    if rule.price_round:
                        price = tools.float_round(price, precision_rounding=rule.price_round)

                    convert_to_price_uom = (lambda price: product_uom_obj._compute_price(
                                                cr, uid, product.uom_id.id,
                                                price, price_uom_id))
                    if rule.price_surcharge:
                        price_surcharge = convert_to_price_uom(rule.price_surcharge)
                        price += price_surcharge

                    if rule.price_min_margin:
                        price_min_margin = convert_to_price_uom(rule.price_min_margin)
                        price = max(price, price_limit + price_min_margin)

                    if rule.price_max_margin:
                        price_max_margin = convert_to_price_uom(rule.price_max_margin)
                        price = min(price, price_limit + price_max_margin)

                    rule_id = rule.id
                break

            # Final price conversion to target UoM
            price = product_uom_obj._compute_price(cr, uid, price_uom_id, price, qty_uom_id)
            results[product.id] = (price, rule_id)
        return results
    

product_pricelist()


class sale_order(osv.osv):
    _inherit = "sale.order"
    
class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        order_data = self.browse(cr, uid, ids)
        current_order_id=[]
        price_list_id=[]
        product_rule_id=[]
        for order_line_obj in order_data:
            current_order_id = order_line_obj.order_id.id
            order_obj=self.pool.get("sale.order").browse(cr,uid,current_order_id)
            price_list_id=order_obj.pricelist_id.id
            current_date=datetime.now()
            pricelist_version_ids=self.pool.get('product.pricelist.version').search(cr,uid,[('pricelist_id','=',price_list_id),('date_end','>=',current_date),])
            pricelist_rule_ids=self.pool.get('product.pricelist.item').search(cr,uid,[('price_version_id','in',pricelist_version_ids),])
            for rule_id in self.pool.get('product.pricelist.item').browse(cr,uid,pricelist_rule_ids):
                if rule_id.base==-3:
                    product_rule_id.append(rule_id.product_id.id)
            break
        
        
        #pricelist = self.pool.get("product.pricelist").search(cr,uid, [('','','')])
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.product_id.id in product_rule_id:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, 1, line.product_id, line.order_id.partner_id)
                cur = line.order_id.pricelist_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
                cur = line.order_id.pricelist_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
    
    _columns={
              'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
              }
    
sale_order_line()
