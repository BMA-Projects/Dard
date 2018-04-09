from openerp import fields, models, api, _
from datetime import date

class update_last_year_qty(models.TransientModel):
    _name = 'update.last.year.qty'

    update_last_year_qty = fields.Float('Update Last Year QTY', default=0)

    @api.multi
    def update_qty(self):
        wizard_id = self.env['product.product'].browse(self._context.get('active_id'))
        if self.update_last_year_qty > 0:
            wizard_id.total_sold_qty_last_year = self.update_last_year_qty