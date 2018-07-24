from openerp import models, fields, api, _


class MultiEntriesWiz(models.TransientModel):
    _name = 'multi.entries.wiz'

    @api.multi
    def confirm_multi_entries(self):
        payment_ids = self.env['account.move'].browse(self._context.get('active_ids'))
        for payment in payment_ids:
            if payment.state == 'draft':
                payment.button_validate()
