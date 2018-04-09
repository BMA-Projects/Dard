# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.tools.translate import _
from openerp import models, fields, api, _
from openerp import SUPERUSER_ID
from datetime import datetime

class product_cron(models.Model):
    _name = 'product.cron'

    @api.model
    def check_product_qty(self):
        company_id = self.env.user.company_id.id
        product_list, index = [],1

        orderpoint = self.env['stock.warehouse.orderpoint'].search([('company_id', '=', company_id)])
        template_rec = self.env.ref('ob_tag_master.product_qty_reminder_email')

        for op in orderpoint:
            prod_virtual_qty = op.product_id.virtual_available
            op_min_qty = op.product_min_qty
            attribs = ''
            if prod_virtual_qty <= op_min_qty:
                for attrib_val_rec in op.product_id.attribute_value_ids:
                    attribs = attribs + attrib_val_rec.attribute_id.name + ': ' + attrib_val_rec.name + ', '
                attribs = attribs[:-2] or '-'
                product_list.append({
                    'count': index,
                    'prod_name': op.product_id.name,
                    'attribs': attribs,
                    'sku': op.product_id.default_code or '-',
                    'qty':  prod_virtual_qty,
                    'incoming_qty': op.product_id.incoming_qty})
                index = index+1
        ctx = self.env.context.copy()
        ctx['email_date'] = str(datetime.strptime(str(datetime.now()), '%Y-%m-%d %H:%M:%S.%f').date())
        if product_list:
            ctx.update({'product_list': product_list})
        self.pool['email.template'].send_mail(self.env.cr, self.env.uid, template_rec.id, SUPERUSER_ID, force_send=True, context=ctx)
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
