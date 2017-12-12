# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from lxml import etree
from openerp.tools.translate import _
from openerp import api

class AccountInvoiceLine(osv.osv):

    _inherit = "account.invoice.line"

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
            setup_charge = line.setup_charge * (1 - (line.discount or 0.0) / 100.0)
            up_charge = line.up_charge * (1 - (line.discount or 0.0) / 100.0)
            run_charge = line.run_charge * (1 - (line.discount or 0.0) / 100.0)
            ltm_charge = line.ltm_charge  * (1 - (line.discount or 0.0) / 100.0)
            pms_charge = line.pms_charge  * (1 - (line.discount or 0.0) / 100.0)
#             taxes['total'] += setup_charge + up_charge + run_charge + ltm_charge + pms_charge
            res[line.id] = taxes['total']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res

    _columns = {
        'setup_charge': fields.float('Setup Charge'),
        'run_charge': fields.float('Run Charge'),
        'up_charge': fields.float('Up Charge'),
        'ltm_charge': fields.float('LTM Charge'),
        'pms_charge': fields.float('PMS Charge'),
        'price_subtotal': fields.function(_amount_line, string='Amount', type="float",digits_compute= dp.get_precision('Account'), store=True),
        'is_variant': fields.boolean('Is Variant'),
    }

    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice', partner_id=False,
                          fposition_id=False, price_unit=False, currency_id=False, company_id=None):
        
        res = super(AccountInvoiceLine, self).product_id_change(product, uom_id, qty=qty, name=name,
                                                                type=type, partner_id=partner_id,
                                                                fposition_id=fposition_id, price_unit=price_unit,
                                                                currency_id=currency_id, 
                                                                company_id=company_id)
        
        product_obj = self.env['product.product']
        value = res.get('value', {})
        value.update({
            'is_variant': False,
        })
        if product:
            product_rec = product_obj.browse(product)
            value.update({'is_variant': product_rec.is_variant})
        res['value'] = value
        return res
