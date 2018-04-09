# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models,fields ,api
from datetime import datetime,time
from openerp.tools.translate import _
from openerp.exceptions import Warning

class create_credit_payment(models.TransientModel):
    _name = 'create.credit.payment'

    @api.multi
    def create_credit(self):
        context = self.env.context or {}
        partner_obj = self.env['res.partner']
        if not self.name > 0:
            raise Warning(_('Must be Greater than Zero (0) !!!'))
        partner_obj.browse(context['active_id']).write({'fix_credit_limit':float(self.name),'credit_limit':float(self.name)})
        return True


    name = fields.Float('Credit Amount')
    #partner_id = fields.Many2one('res.partner',default=compute_default_value)




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: