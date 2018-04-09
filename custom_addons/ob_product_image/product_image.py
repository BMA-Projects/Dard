from openerp.osv import fields, osv
from openerp import tools
from openerp import api

class procurement_order(osv.Model):
    """
    Procurement Orders
    """
    _inherit = "procurement.order"
    _columns = {
        'image_small': fields.related('product_id', 'image_small', type='binary', string='Product Image'),
    }
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        res = super(procurement_order,self).onchange_product_id(cr, uid, ids, product_id, context)
        if not res :
            res['value'] = {}
        if product_id:
            product_data = self.pool.get("product.product").browse(cr, uid, product_id).image_small
            res['value'].update({'image_small': product_data })
        return res
    
procurement_order()

class stock_move(osv.Model):
    _inherit = 'stock.move'
    _columns = {
         'image_small': fields.related('product_id', 'image_small', type='binary', string='Product Image'),
    }
    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False, loc_dest_id=False, partner_id=False):
        
        res = super(stock_move,self).onchange_product_id(cr, uid, ids, prod_id, loc_id, loc_dest_id, partner_id)
        if not res :
            res['value'] = {}
        if prod_id:
            product_data = self.pool.get("product.product").browse(cr, uid, prod_id).image_small
            res['value'].update({'image_small': product_data })
        return res
stock_move()

class sale_order_line(osv.Model):
    _inherit = 'sale.order.line'
    _columns = {
        'image_small': fields.related('product_id', 'image_small', type='binary', string='Product Image'),
    }
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        
        res = super(sale_order_line,self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        if not res :
            res['value'] = {}
        if product:
            product_data = self.pool.get("product.product").browse(cr, uid, product).image_small
            res['value'].update({'image_small': product_data })
        return res

sale_order_line()

class account_invoice_line(osv.Model):
    _inherit = 'account.invoice.line'
    _columns = {
        'image_small': fields.related('product_id', 'image_small', type='binary', string='Product Image'),
    }

    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice', partner_id=False,
                          fposition_id=False, price_unit=False, currency_id=False, company_id=None):
        res = super(account_invoice_line, self).product_id_change(product, uom_id, qty=qty, name=name,
                                                                type=type, partner_id=partner_id,
                                                                fposition_id=fposition_id, price_unit=price_unit,
                                                                currency_id=currency_id,
                                                                company_id=company_id)
        if not res:
            res['value'] = {}
        if product:
            product_data = self.env['product.product'].browse(product).image_small
            res['value'].update({'image_small': product_data})
        return res

account_invoice_line()
