from openerp import models, fields, api, _


class CustomerEnhancement(models.Model):
    _inherit = 'res.partner'
    # _name = 'customer.enhancement'

    customer_id = fields.Char(string='Old Customer ID')
    customer_code = fields.Char(string='Old Customer Code')
    suppl_id = fields.Char(string='Old Supplier ID')




    # att_product_id = fields.Many2one('product.product', string="Product", )
    # prod_uom_qty = fields.Float(string="Quantity")
    # prod_uom = fields.Many2one('product.uom', string="UOM")
    # prod_unit_price = fields.Float(string="Unit price")
    # prod_discount = fields.Float(string="Discount (%)" ,digits_compute= dp.get_precision('Discount'), readonly=True,)
    # prod_tax_id = fields.Many2many("account.tax","sale_line_atta_tax", 'sale_line_tax_id','tax_id',string="Taxes")
    # sale_prod_att_id = fields.Many2one('sale.order.line', string="Product Attachment")
