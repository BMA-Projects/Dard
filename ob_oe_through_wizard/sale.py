# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, api, fields


class sale_order(models.Model):
    _inherit = 'sale.order'

    printing_note = fields.Text(string='Printing Instruction', translate=True, help="To be printed on Manufacturing order.")
    packing_note = fields.Text(string='Packing Instruction', translate=True, help="To be printed on Delivery order.")
    shipping_note = fields.Text(string='Shipping Instruction', translate=True, help="To be printed on Delivery order.")

    @api.multi
    def name_get(self):
        res = []
        for r in self.read(['client_order_ref','name']):
            if 'get_cust_po_ref' in self._context:
                if r['client_order_ref']:
                    res.append((r['id'], '%s' % (r['client_order_ref'])))
            else:
                res.append((r['id'], '%s' % (r['name'])))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
