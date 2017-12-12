from openerp import models, api
from openerp.tools.translate import _
from openerp.osv import fields, osv
class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"
    
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _compute_price(self):
        stk_config_obj = self.pool.get('stock.config.settings')
        values = stk_config_obj.default_get(self._cr, self.env.user.id, ['producut_id'], context = None)
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        if 'product_id' in values and values['product_id']:
            if int(values['product_id']) == self.product_id.id:
                taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
                self.price_subtotal = price
            else:
                taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
                self.price_subtotal = taxes['total']
        else:
            raise osv.except_osv(_('Warning'), _('Please Configure the Handling Service Product '))
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)