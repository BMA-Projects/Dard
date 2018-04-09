# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.report import report_sxw
from openerp import api
import ast

class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_imprint_data': self.get_imprint_data,
            'get_sample_data': self.get_sample_data
        })

    def get_imprint_data(self,line):
        if line.imprint_data:
            imprint_data = ast.literal_eval(line.imprint_data)
            final_data = ''
            temp_data = ''
            for value in imprint_data:
                if type(imprint_data[value])==list:
                    for val in imprint_data[value]:
                        for data in self.pool.get('product.variant.dimension.option').browse(self.cr, self.uid, val[2]):
                            temp_data +=  str(data.name) + ','
                    if temp_data:
                        final_data += value.capitalize().replace("_", " ") + ':' + temp_data + '\n'
                    temp_data=''
                else:
                    for data in produ_vari_dime_option_obj.browse(self.cr, self.uid, [imprint_data[value]]):
                        final_data += value.capitalize().replace("_", " ") + ':' + str(data.name) + '\n' 
            return final_data

    def get_sample_data(self,sale):
        sale_obj = self.pool.get('sale.order')
        sample = 'NO'
        if sale:
            sale_fields = sale_obj.fields_get(self.cr, self.uid)
            if 'sample_type_id' in sale_fields:
                sample = sale.sample_type_id.name or 'NO'
        return sample

report_sxw.report_sxw('report.sale.order.ack', 'sale.order', 'addons/ob_order_confirmation/report/sale_order_ack_receipt.rml', parser=order, header="external")
