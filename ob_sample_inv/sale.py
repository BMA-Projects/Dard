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

    is_sample = fields.Boolean(string='Sample')
    sample_type_id = fields.Many2one('sample.type', string='Sample Type')

    @api.onchange('is_sample')
    def _onchange_is_sample(self):
        self.sample_type_id = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: