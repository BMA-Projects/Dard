# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import except_orm

class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.multi
    #Send Order Acknowledgement mail to customer
    def action_button_confirm(self):
        tmpl_obj = self.env['email.template']
        partner_obj = self.env['res.partner']
        partner_fields = partner_obj.fields_get()
        res = super(sale_order, self).action_button_confirm()
        email_to = False
        support_email = self.company_id.support_email
        support_phone = self.company_id.support_phone
        try:
            template = self.env.ref('ob_order_confirmation.order_acknowledgement_template')
        except ValueError:
            template = False
        for rec in self:
            if partner_fields.has_key('confirm_email'):
                email_to = rec.partner_id.confirm_email
            if not email_to:
                email_to = rec.partner_id.email
            if not email_to:
                raise except_orm(_('Warning!'), _('Please define email address for customer %s.') % (rec.partner_id.name))
            if not support_email and not support_phone:
                raise except_orm(_('Warning!'), _('Please define email address and phone number for company %s.') % (self.company_id.name))
            if not support_email and support_phone:
                raise except_orm(_('Warning!'), _('Please define email address for company %s.') % (self.company_id.name))
            if not support_phone and support_email:
                raise except_orm(_('Warning!'), _('Please define phone number for company %s.') % (self.company_id.name))
            if template and email_to:
                template.write({'email_to': email_to, 'email_from': rec.company_id.email})
                template.send_mail(rec.id, True)
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
