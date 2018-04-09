from openerp import models, fields, api, _
from openerp.report import report_sxw
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import datetime


class report_invoice(report_sxw.rml_parse):
    _name = 'report.invoice'


    def __init__(self, cr, uid, name, context):
        super(report_invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_so_ref':self._get_so_ref,
            'get_amn_rec':self.get_amn_rec,
            'get_so_ref_from_do_invoice': self._get_so_ref_from_do_invoice,
            'get_paid_after':self.get_paid_after,
            'get_number':self.get_number,

        })
        self.context = context

    def get_number(self, number):
        if number:
            split_number = list(number.rpartition('/'))
            if len(split_number) == 3:
                return split_number and split_number[2]
        return number

    def _get_so_ref_from_do_invoice(self, origin):
        res = False
        sale_obj = self.pool.get('sale.order')
        stock_picking_obj = self.pool.get('stock.picking')

        if origin:
            # On Demand
            sale_order_id = sale_obj.search(self.cr, self.uid, [('name','=', origin)], context=self.context)
            # On Delivery Order
            if not sale_order_id:
                stock_picking_id = stock_picking_obj.search(self.cr, self.uid, [('name', '=', origin)],
                                                            context=self.context)
                if stock_picking_id:
                    stock_picking_data = stock_picking_obj.browse(self.cr, self.uid, stock_picking_id,
                                                                context=self.context)
                    if stock_picking_data:
                        sale_order_id = sale_obj.search(self.cr, self.uid,
                                    [('name', '=', stock_picking_data.origin)], context=self.context)
            if sale_order_id:
                sale_order_id = sale_obj.browse(self.cr, self.uid, sale_order_id,
                                                context=self.context)
                res = sale_order_id
        return res


    def _get_so_ref(self,origin):
        res=False
        sale_obj = self.pool.get('sale.order')
        ware_obj = self.pool.get('stock.picking')
        if origin:
            origin = origin.split(':')
            sale_id = sale_obj.search(self.cr, self.uid, [('name','ilike', origin[0])], context=self.context)
            if sale_id:
                so_client_order_ref = sale_obj.browse(self.cr, self.uid, sale_id[0])
                return so_client_order_ref
            else:
                sale_ware_id = ware_obj.search(self.cr, self.uid , [('name','=',origin[0])],context=self.context)
                if sale_ware_id:
                    so_ware_order_ref = ware_obj.browse(self.cr, self.uid, sale_ware_id[0])
                    origin_id = so_ware_order_ref.origin
                    sale_w_id = sale_obj.search(self.cr, self.uid, [('name','=', origin_id)], context=self.context)
                    if sale_w_id:
                        so_client_order_w_ref = sale_obj.browse(self.cr, self.uid, sale_w_id[0])
                        return so_client_order_w_ref
                    else:
                        return res    
                else:
                    return res
        else:
            return res

    def get_amn_rec(self,amount,due):
        if (amount != 0):
            return amount - due
        else:
            return 0.0

    def get_paid_after(self,due):
        if (due != 0):
            final_res = (due * 1.5) / 100
            if (final_res > 10):
                return final_res + due
            else:
                return 10 + due
        return 0

class report_invoice_new(models.AbstractModel):
    _name = 'report.ob_invoice_dard_report.report_invoice_document'
    _inherit = 'report.abstract_report'
    _template = 'ob_invoice_dard_report.report_invoice_document'
    _wrapped_report_class = report_invoice

