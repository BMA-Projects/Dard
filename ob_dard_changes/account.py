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
    state_id = fields.Many2one(string="State", related="partner_id.state_id")

    @api.multi
    def action_open(self):
        for rec in self:
            query = "update account_invoice set state='open' where id=%s" % (rec.id)
            rec.env.cr.execute(query)
        return True

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

    search_product = fields.Char('Products')

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # list_invoice = []
        res = super(account_invoice, self).search(args, offset, limit, order)
        for rec in args:
            if rec[0] == 'search_product':
                product_ids = self.env['product.product'].search(['|', ('name', 'like', rec[2]), ('default_code', '=', rec[2])])
                invoice_lines = self.env['account.invoice.line'].search([('product_id', 'in', [x.id for x in product_ids])])
                inv_list = [x.id for x in res] + [x.invoice_id.id for x in invoice_lines]
                return self.browse(inv_list)
        return res
