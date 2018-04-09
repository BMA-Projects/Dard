# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models,fields ,api
from datetime import datetime,date
from openerp.tools.translate import _
from openerp.exceptions import Warning
from openerp import tools


class ob_product_turn_report_wizard(models.TransientModel):
    _name = 'ob.product.turn.report.wizard'
    _description = 'Print Product turn report'

    date_from = fields.Datetime('From', required=True, default=fields.Datetime.now())
    location_id = fields.Many2one('stock.location',string='Location')

    @api.multi
    def action_open_window(self):
        obj_model = self.env['ir.model.data']
        model_tree_view_ids = obj_model.search([('model','=','ir.ui.view'),('name','=','view_product_turn_tree')])
        resource_id = model_tree_view_ids.res_id
        model_form_view_ids = obj_model.search([('model','=','ir.ui.view'),('name','=','product_normal_form_view')])
        form_id = model_form_view_ids.res_id
        data = self.read([], ['date_from','location_id'])
        if datetime.strptime(data[0]['date_from'],tools.DEFAULT_SERVER_DATETIME_FORMAT) > datetime.now():
            raise Warning(_("You can't calaclulate turns for future date. !!!"))
        return {
            'name': _('Current Inventory'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(resource_id,'tree'),(form_id,'form')],
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            'context': {
                       'from_wizard' : True,
                       'date_from': data[0]['date_from'],
                       'location_id' : data[0]['location_id'] or False
            },
            'domain': [('type', '<>', 'service')],
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
