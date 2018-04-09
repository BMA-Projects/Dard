# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import osv, fields
import time

# class stock_picking(osv.osv):
#     _inherit = "stock.picking"
#
#     _columns = {
#         'in_hand_date': fields.date('In Hand Date', required=True, select=True),
#     }


class stock_picking_out(osv.osv):
    _inherit = "stock.picking"

    _columns = {
        'in_hand_date': fields.date('In Hand Date'),
    }
    
    # _defaults = {
    #     'in_hand_date': lambda *a: time.strftime('%Y-%m-%d'),
    # }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
