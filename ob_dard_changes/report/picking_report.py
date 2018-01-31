# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api, _
from openerp.report import report_sxw
from openerp.osv import osv
from datetime import datetime

class picking_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(picking_parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_po_ref': self._get_po_ref,
            'currunt_date': self._currunt_date,
            })
    
    def _get_po_ref(self,origin):
        sale_obj = self.pool.get('sale.order')
        if origin:
            sale_id = sale_obj.search(self.cr, self.uid, [('name', '=', origin)])
            if sale_id:return sale_obj.browse(self.cr, self.uid, sale_id[0]).client_po_ref
        return False
    
    def _currunt_date(self):
        i = datetime.now()
        return i.strftime('%m/%d/%y')
        
class report_picking(osv.AbstractModel):
    _name = 'report.stock.report_picking'
    _inherit = 'report.abstract_report'
    _template = 'stock.report_picking'
    _wrapped_report_class = picking_parser