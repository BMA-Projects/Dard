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
    _inherit = "res.partner"

    search_contect = fields.Char(string="Search Contact")

    #To generate auto sequence for customer and supplier
    @api.model
    def create(self,vals):
        sequence = None
        if vals.get('is_company',False):
            if vals.get('supplier') and vals.get('customer'):
                sequence = self.env['ir.sequence'].sudo().next_by_code('res.partner.custSupp')
            else:
                if vals.get('customer') and not vals.get('supplier'):
                    sequence = self.env['ir.sequence'].sudo().next_by_code('res.partner.cust')
                if vals.get('supplier') and not vals.get('customer'):
                    sequence = self.env['ir.sequence'].sudo().next_by_code('res.partner.supp')
            vals['cust_number'] = sequence
        if vals.get('parent_id', False):
            name = vals.get('name', '')
            parent_id = self.browse(vals['parent_id'])
            vals['search_contect'] = parent_id and parent_id.cust_number
        return super(res_partner, self).create(vals)

    @api.multi
    def write(self, vals):
        for rec in self:
            is_delete = []
            if vals.get('child_ids', False):
                is_delete = [child[1] for child in vals['child_ids'] if child[0] == 2]
            if is_delete:
                for child in is_delete:
                    rec.browse(child).write({'search_contect': False})
            if 'parent_id' in vals.keys() and vals['parent_id'] == False:
                vals['search_contect'] = False
            elif 'parent_id' in vals.keys() and vals['parent_id'] != False:
                parent_id = rec.browse(vals['parent_id'])
                vals['search_contect'] = parent_id and parent_id.cust_number

            #TO GENERATE CUSTOMER SEQUENCE NUMBER.
            sequence = None 
            sc = rec.customer
            ss = rec.supplier
            vc = vals.get('customer',False)
            vs = vals.get('supplier',False)
            cust_in_vals = 'customer' in vals
            supp_in_vals = 'supplier' in vals
            is_company = vals.get('is_company',False)

            if (is_company and not rec.is_company) or (rec.is_company and not 'is_company' in vals):
                #conditions are here to empty the customer number if both customer and supplier are check/uncheck
                if cust_in_vals and supp_in_vals:
                    if (vc and vs) and (sc and ss): # msg for all 'noupdates' >> #OdooISSUE: because if boolean is checked and you edit > uncheck > check (getting its value in 'VALS' even it's state is not changed)
                        sequence = "noupdate"
                    elif(not vc and not vs) and (not sc and not ss):
                        sequence = "noupdate"
                    elif (not vc and not vs):
                        sequence = None
                    elif (vc and not vs):
                        sequence = self.env['ir.sequence'].sudo().next_by_code('res.partner.cust')
                    elif (not vc and vs):
                        sequence = self.env['ir.sequence'].sudo().next_by_code('res.partner.supp')
                    elif (vc and vs):
                        sequence = self.env['ir.sequence'].sudo().next_by_code('res.partner.custSupp')

                if cust_in_vals and not supp_in_vals:
                    if vc:
                        if sc:
                            sequence = "noupdate"
                        elif ss:
                            sequence = self.env['ir.sequence'].sudo().next_by_code('res.partner.custSupp')
                        elif not ss:
                            sequence = self.env['ir.sequence'].sudo().next_by_code('res.partner.cust')
                    else:
                        if not sc:
                            sequence = "noupdate"
                        elif ss:
                            sequence = self.env['ir.sequence'].sudo().next_by_code('res.partner.supp')
                        elif not ss:
                            sequence = None

                if not cust_in_vals and supp_in_vals:
                    if vs:
                        if ss:
                            sequence = "noupdate"
                        elif sc:
                            sequence = self.env['ir.sequence'].sudo().next_by_code('res.partner.custSupp')
                        elif not sc:
                            sequence = self.env['ir.sequence'].sudo().next_by_code('res.partner.supp')
                    else:
                        if not ss:
                            sequence = "noupdate"
                        elif sc:
                            sequence = self.env['ir.sequence'].sudo().next_by_code('res.partner.cust')
                        elif not sc:
                            sequence = None

                if not cust_in_vals and not cust_in_vals and is_company:
                    if ss:
                        sequence = self.env['ir.sequence'].sudo().next_by_code('res.partner.supp')
                    elif sc:
                        sequence = self.env['ir.sequence'].sudo().next_by_code('res.partner.cust')
                    elif ss and sc:
                        sequence = self.env['ir.sequence'].sudo().next_by_code('res.partner.custSupp')

                if (sequence != "noupdate" and (cust_in_vals or supp_in_vals)) or is_company:
                    vals['cust_number'] = sequence
            elif rec.is_company and is_company:
                pass
            else:
                vals['cust_number'] = sequence

            if 'is_company' in vals.keys() or rec and rec.is_company:
                if vals.get('cust_number',False):
                    for child in rec.child_ids:
                        child.write({'search_contect': vals['cust_number']})
        return super(res_partner, self).write(vals)


