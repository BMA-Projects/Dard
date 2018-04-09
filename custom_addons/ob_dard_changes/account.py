# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning

class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    client_po_ref = fields.Char("Customer PO Number", copy=False)
    zorch_sale_order = fields.Char("Zorch Sales order", copy=False)
    zorch_po_number = fields.Char("Zorch PO Number", copy=False)
    zorch_visible = fields.Boolean('Zorch Fields Visible')

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):
        result = super(account_invoice, self).onchange_partner_id(type, partner_id)
        result['value'].update({'client_po_ref': '', 'zorch_po_number': '', 'zorch_sale_order':''})
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            zorch_id = self.env['ir.model.data'].get_object_reference('ob_dard_changes', 'zorch_categ_id')[1]
            if partner.category_id and zorch_id in partner.category_id.ids:
                result['value'].update({'zorch_visible':True})
            else:
                result['value'].update({'zorch_visible':False})
        else:
            result['value'].update({'zorch_visible':False})
        return result

    @api.multi 
    def copy(self, default=None):
        res = super(account_invoice, self).copy(default={'picking_id':False})
        return res
    
    
    @api.multi
    def action_invoice_sent(self):
        res = super(account_invoice, self).action_invoice_sent()
        
        user_browse = self.env['res.users'].browse(self._uid)
        for group in user_browse.groups_id:
            if group.name == 'Sales Person':
                if self.user_id.id != self.partner_id.user_id.id:
                    raise except_orm(_('Access Error!'),
                                     _('You cannot Send Mail to Other User\'s Customers.'))
#                     raise Warning(_('You cannot Send Mail to Other User\'s Customers'))
        return res
        