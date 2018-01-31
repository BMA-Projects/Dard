# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, fields, api, _
from lxml import etree


class res_partner(models.Model):
    _inherit = 'res.partner'

    risk_level = fields.Selection([('high','High Level'), ('medium','Medium Level'), ('low','Low Level')], 'Risk Level', help='Risk Level for Supplier')
    is_approved = fields.Boolean(string='Approved', help='Set the supplier as approved', readonly=True)


    @api.multi
    def supplier_approved(self):
         self.write({'is_approved':True})
         return True

    @api.multi
    def supplier_dis_approved(self):
         self.write({'is_approved':False})
         return True

    def copy(self, cr, uid, ids, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'is_approved': False,
            'risk_level': False,
        })
        return super(res_partner, self).copy(cr, uid, ids, default=default, context=context)

class product_product(models.Model):
    _inherit = "product.product"

    last_review_date = fields.Date('Last Review Date', select=True, help="Last Review Date of product.")


class product_supplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(product_supplierinfo, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        context = self._context.copy()
        context.update({'from_purchase':1})
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='name']")
        for node in nodes:
            node.set('context', str(context))
        res['arch'] = etree.tostring(doc)
        return res

class purchase_requisition_partner(models.Model):
     _inherit = "purchase.requisition.partner"

     @api.model
     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(purchase_requisition_partner, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        context = self._context.copy()
        context.update({'from_purchase':1})
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='partner_id']")
        for node in nodes:
            node.set('context', str(context))
        res['arch'] = etree.tostring(doc)
        return res

class purchase_order(models.Model):
    _inherit="purchase.order"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        context = self._context.copy()
        partner = self.env['res.partner'].browse(context.get('active_id'))
        if partner.is_approved:
            context.update({'default_partner_id': context.get('active_id')})
        res = super(purchase_order, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        context.update({'from_purchase':1})
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='partner_id']")
        for node in nodes:
            node.set('context', str(context))
        res['arch'] = etree.tostring(doc)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: