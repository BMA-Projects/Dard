from openerp import models, fields, api, _
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import workflow

def create_invoice_attachment(cr,uid, inv_id, attachment_ids,attachment_obj,context):
	for att in attachment_ids:
		attachment = attachment_obj.browse(cr,uid,att,context=context)
		attachment_obj.create(cr,uid,{
					'res_id':inv_id,
					'res_model':'account.invoice',
					'type': 'binary',
					'datas':attachment.datas,'name':attachment.name},context=context)

class sale_order(models.Model):
	_inherit = 'sale.order'
	
	def _make_invoice(self, cr, uid, order, lines, context=None):
		inv_id = super(sale_order,self)._make_invoice(cr,uid,order,lines,context)
		if inv_id:
			attachment_obj =  self.pool.get('ir.attachment')
			attachment_ids = attachment_obj.search(cr, uid, [('res_id','=',order.id),('res_model','=','sale.order')])
			create_invoice_attachment(cr, uid, inv_id, attachment_ids, attachment_obj, context)
		return inv_id


class sale_advance_payment_inv(osv.osv_memory):
	_inherit = "sale.advance.payment.inv"
	_description = "Sales Advance Payment Invoice"

	def _create_invoices(self, cr, uid, inv_values, sale_id, context=None):
		res = super(sale_advance_payment_inv, self)._create_invoices(cr, uid, inv_values=inv_values, sale_id=sale_id, context=context)
		if res:
			attachment_obj =  self.pool.get('ir.attachment')
			attachment_ids = attachment_obj.search(cr, uid, [('res_id','=',sale_id),('res_model','=','sale.order')])
			create_invoice_attachment(cr, uid, res, attachment_ids, attachment_obj, context)
		return res



class sale_order_line_make_invoice(osv.osv_memory):
	_inherit = "sale.order.line.make.invoice"
	_description = "Sale OrderLine Make_invoice"
	
	def make_invoices(self, cr, uid, ids, context=None):
		sales_order_line_obj = self.pool.get('sale.order.line')
		sale_line_ids = sales_order_line_obj.browse(cr, uid, context.get('active_ids', []), context=context)
		attachment_obj =  self.pool.get('ir.attachment')
		res = super(sale_order_line_make_invoice,self).make_invoices(cr,uid,ids, context=context)
		if res.get('res_id', False):
			attachment_ids = attachment_obj.search(cr, uid, [('res_id','=',sale_line_ids[0].order_id.id),('res_model','=','sale.order')])
			create_invoice_attachment(cr, uid, res.get('res_id', False), attachment_ids, attachment_obj, context)
		else:
			attachment_ids = attachment_obj.search(cr, uid, [('res_id','=',sale_line_ids[0].order_id.id),('res_model','=','sale.order')])
			for invoice in sale_line_ids[0].order_id.invoice_ids:
				account_attachment = attachment_obj.search(cr, uid, [('res_id','=',invoice.id),('res_model','=','account.invoice')])
				if not account_attachment:
					create_invoice_attachment(cr, uid, invoice.id, attachment_ids, attachment_obj, context)
		return res
