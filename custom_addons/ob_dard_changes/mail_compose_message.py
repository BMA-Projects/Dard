# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import fields, osv

class mail_compose_message(osv.Model):
    _inherit = 'mail.compose.message'

    def get_mail_values(self, cr, uid, wizard, res_ids, context=None):
        res = super(mail_compose_message, self).get_mail_values(cr, uid, wizard, res_ids, context=context)
        if res_ids and res and res.get(res_ids[0]) and context.get('active_model') == 'sale.order':
            order_id = self.pool.get('sale.order').browse(cr, uid, res_ids, context=context)
            if order_id.state != 'draft' and order_id.state !='sent' and order_id.state!='prepared':
                res.get(res_ids[0]).update({'email_from' : 'orders@tagmaster.net'})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
