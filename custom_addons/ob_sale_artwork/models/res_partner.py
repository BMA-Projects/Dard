# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api, _

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    confirm_email = fields.Char('Order Confirmation Email', size=240)
    ship_track_email = fields.Char('Order Shipment tracking Email', size=240)
    order_proof_email = fields.Char('Order Proof Email', size=240)
    allow_send_by_email = fields.Boolean('Receive Send By Email', default=True)
    # account_email = fields.Char('Accounting Email')
    
    _defaults = {
        'notify_email': lambda *args: 'none',
    }

    @api.multi
    def name_get(self):
        '''context : parent_model_name is fetch from partner_ids field of mail.compose.message  '''
        res = super(res_partner ,self).name_get()
        if self._context.get('show_email') and self._context.get('parent_model_name', False) and self._context.get('parent_model_name') == 'sale.order.line.images':
            for record in self:
                name = record.name
                if self._context.get('show_email') and record.order_proof_email:
                    name = "%s (%s)" % (name, record.order_proof_email)
                    res.append((record.id, name))
                elif self._context.get('show_email') and record.email:
                    name = "%s (%s)" % (name, record.email)
                    res.append((record.id, name))
            return res
        return res