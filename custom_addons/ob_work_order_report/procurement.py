import openerp
from openerp import models, fields, api, _
import base64
from openerp.report import report_sxw
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

class procurement_order(models.Model):
    _inherit = 'procurement.order'

    # @api.multi
    # def make_mo(self):
    #     if self.origin:
    #         sale_rec_id = self.pool.get('sale.order').search(self._cr,self._uid,[('name','=',self.origin.split(':')[0])],self._context)
    #         res = super(procurement_order, self).make_mo()
    #         mrp_rec = self.pool.get('mrp.production').browse(self._cr,self._uid,res[self.id],self._context)
    #         if mrp_rec:
    #             mrp_rec_name = mrp_rec[0].name
    #             service_name = 'ob_work_order_report.report_workorder'
    #             result, format = self.pool.get('ir.actions.report.xml').render_report(self._cr, self._uid, [res[self.id]], service_name, {'model': 'mrp.production'}, self._context)
    #             result = base64.b64encode(result)
    #             file_name = "Work Order Report" + mrp_rec_name +".pdf"
    #             self.pool.get('ir.attachment').create(self._cr, self._uid,
    #                                                           {
    #                                                            'name': file_name,
    #                                                            'datas': result,
    #                                                            'datas_fname': file_name,
    #                                                            'res_model': 'sale.order',
    #                                                            'res_id': sale_rec_id[0],
    #                                                            'type': 'binary'
    #                                                           },
    #                                                           context=self._context)
    #         return res


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def print_workorder_report_so(self):
      line_list = []
      sale_order_id = self.pool.get('sale.order').browse(self._cr,self._uid,self.id,self._context)
      for line_id in sale_order_id.order_line:
        sale_rec_id = self.env['mrp.production'].search([('sub_origin','=',line_id.sol_seq),('state','=','confirmed')])
        line_list.append(sale_rec_id.id)
      if line_list:
        for id in line_list:
          if id:
            return self.pool['report'].get_action(self._cr, self._uid, line_list, 'ob_work_order_report.report_workorder', context=self._context)
          else:
            raise osv.except_osv(_('Mo Is not created!'), _('Make sure Manufacturing Order is Created.'))
      else:
        raise osv.except_osv(_('Mo Is not created!'), _('Make sure Manufacturing Order is Created.'))