# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
import base64
import xlsxwriter
import csv
import os.path
from openerp import models,fields ,api, _
from datetime import datetime,time
from openerp.exceptions import except_orm

class ranking_report(models.TransientModel):
	_name = 'ranking.report'


	limit = fields.Integer("Limit")
	filter_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Supplier'),
		('sales_level','Sales'), ('purchase_level','Purchase'),
		('product', 'Product'), ('sales_person', "Sales Person"),
		('state', "State")], 'Report On', default='customer')
	customer_filter = fields.Selection([('max_order', 'Max Orders'), ('max_value', 'Max Value')], 
		'Customer Filter', default='max_order')
	supplier_filter = fields.Selection([('max_order', 'Max Orders'), ('max_value', 'Max Value')], 'Supplier Filter', default='max_order')
	sales_filter = fields.Selection([('order_value', 'Order Values'), ('order_qty', 'Order Quatity')], 
		'Sales Filter', default='order_value')
	purchase_filter = fields.Selection([('order_value', 'Order Values'), ('order_qty', 'Order Quatity')], 
		'Purchase Filter', default='order_value')
	product_filter = fields.Selection([('max_product_sold', 'Max Product Sold'),
		('state', 'State Wise')], 'Product Filter', default='max_product_sold')
	salesperson_filter = fields.Selection([('no_of_order', 'No of Order'), ('order_qty', 'Order Quatity')], 
		'Salesperson Filter', default='no_of_order')
	territory_filter = fields.Selection([('no_of_order', 'No of Order'), ('order_amount', 'Order Amount')], 
		'State Filter', default='no_of_order')

	product_id = fields.Many2one('product.product', string="Find Product")

	@api.multi
	def get_ranking_data(self):
		if self.filter_type == 'customer':
			if self.customer_filter == 'max_order':
				self._cr.execute("""select DISTINCT(partner_id), count(id) total from sale_order where state not in ('draft','sent','cancel') group by partner_id order by total desc;""")
				res = self._cr.fetchall()
				if len(res) < self.limit or self.limit < 1:
					raise except_orm(_('Invalid top limit'),_('Please enter a valid limit between 1 and %d'%(len(res))))
				final_res = (res[0 : self.limit])
				col_data = ['Name', 'Total']
				final_data = []
				for res in final_res:
					data = []
					data.append(self.env['res.partner'].browse(res[0]).name)
					data.append(res[1])
					final_data.append(data)
				return self.generate_excel(col_data, final_data)

			else:
				self._cr.execute("""select DISTINCT(partner_id), sum(amount_total) total from sale_order where state not in ('draft','sent','cancel') group by partner_id having sum(amount_total) > 0 order by total desc;""")
				res = self._cr.fetchall()
				if len(res) < self.limit or self.limit < 1:
					raise except_orm(_('Invalid top limit'),_('Please enter a valid limit between 1 and %d'%(len(res))))
				final_res = (res[0 : self.limit])
				col_data = ['Name', 'Total']
				final_data = []
				for res in final_res:
					if res[1] <= 0.0:
						continue
					data = []
					data.append(self.env['res.partner'].browse(res[0]).name)
					data.append(res[1])
					final_data.append(data)
				return self.generate_excel(col_data, final_data)

		elif self.filter_type == 'supplier':
			if self.supplier_filter == 'max_order':
				self._cr.execute("""select DISTINCT(partner_id), count(id) total from purchase_order where state not in ('draft','sent','cancel') group by partner_id order by total desc;""")
				res = self._cr.fetchall()
				if len(res) < self.limit or self.limit < 1:
					raise except_orm(_('Invalid top limit'),_('Please enter a valid limit between 1 and %d'%(len(res))))
				final_res = (res[0 : self.limit])
				col_data = ['Name', 'Total']
				final_data = []
				for res in final_res:
					data = []
					data.append(self.env['res.partner'].browse(res[0]).name)
					data.append(res[1])
					final_data.append(data)
				return self.generate_excel(col_data, final_data)

			else:
				self._cr.execute("""select DISTINCT(partner_id), sum(amount_total) total from purchase_order where state not in ('draft','sent','cancel') group by partner_id having sum(amount_total) > 0 order by total desc;""")
				res = self._cr.fetchall()
				if len(res) < self.limit or self.limit < 1:
					raise except_orm(_('Invalid top limit'),_('Please enter a valid limit between 1 and %d'%(len(res))))
				final_res = (res[0 : self.limit])
				col_data = ['Name', 'Total']
				final_data = []
				for res in final_res:
					data = []
					if res[1] <= 0.0:
						continue
					data.append(self.env['res.partner'].browse(res[0]).name)
					data.append(res[1])
					final_data.append(data)
				return self.generate_excel(col_data, final_data)

		elif self.filter_type == 'sales_level':
			if self.sales_filter == 'order_value':
				self._cr.execute("""select id, max(amount_total) from sale_order where state not in ('draft','sent','cancel') group by id having max(amount_total) > 0 order by amount_total desc;
	;""")
				res = self._cr.fetchall()
				if len(res) < self.limit or self.limit < 1:
					raise except_orm(_('Invalid Top Limit'),_('Please enter a valid limit between 1 and %d'%(len(res))))
				final_res = (res[0 : self.limit])
				col_data = ['Name', 'Total']
				final_data = []
				for res in final_res:
					data = []
					if res[1] <= 0.0:
						continue
					data.append(self.env['sale.order'].browse(res[0]).name)
					data.append(res[1])
					final_data.append(data)
				return self.generate_excel(col_data, final_data)
			else:
				self._cr.execute("""select order_id, sum(product_uos_qty) as total from sale_order_line where order_id in
					(select id from sale_order where state not in ('draft','sent','cancel')) 
					group by order_id having sum(product_uos_qty) > 0 order by total desc;
	;""")
				res = self._cr.fetchall()
				if len(res) < self.limit or self.limit < 1:
					raise except_orm(_('Invalid Top Limit'),_('Please enter a valid limit between 1 and %d'%(len(res))))
				final_res = (res[0 : self.limit])
				col_data = ['Name', 'Total']
				final_data = []
				for res in final_res:
					data = []
					if res[1] <= 0.0:
						continue
					data.append(self.env['sale.order'].search([('id','=',res[0])]).name)
					data.append(res[1])
					final_data.append(data)
				return self.generate_excel(col_data, final_data)

		elif self.filter_type == 'purchase_level':
			if self.purchase_filter == 'order_value':
				self._cr.execute("""select id, max(amount_total) from purchase_order where state not in ('draft','sent','cancel') group by id having max(amount_total) > 0 order by amount_total desc;""")
				res = self._cr.fetchall()
				if len(res) < self.limit or self.limit < 1:
					raise except_orm(_('Invalid Top Limit'),_('Please enter a valid limit between 1 and %d'%(len(res))))
				final_res = (res[0 : self.limit])
				col_data = ['Name', 'Total']
				final_data = []
				for res in final_res:
					data = []
					if res[1] <= 0.0:
						continue
					data.append(self.env['purchase.order'].browse(res[0]).name)
					data.append(res[1])
					final_data.append(data)
				return self.generate_excel(col_data, final_data)
			else:
				self._cr.execute("""select order_id, sum(product_qty) as total from purchase_order_line where order_id in
				(select id from purchase_order where state not in ('draft','sent','cancel'))
				group by order_id order by total desc;
	;""")
				res = self._cr.fetchall()
				if len(res) < self.limit or self.limit < 1:
					raise except_orm(_('Invalid Top Limit'),_('Please enter a valid limit between 1 and %d'%(len(res))))
				final_res = (res[0 : self.limit])
				col_data = ['Name', 'Total']
				final_data = []
				for res in final_res:
					data = []
					if res[1] <= 0.0:
						continue
					data.append(self.env['purchase.order'].search([('id','=',res[0])]).name)
					data.append(res[1])
					final_data.append(data)
				return self.generate_excel(col_data, final_data)

		elif self.filter_type == 'product':
			if self.product_filter == 'max_product_sold':
				self._cr.execute("""select sol.product_id, count(sol.product_id) as qty from sale_order_line sol 
					where order_id in (select id from sale_order where state not in ('draft','sent','cancel')) and 
					sol.product_id in(select id from product_product where product_tmpl_id in 
					(select id from product_template where type != 'service')) 
					group by sol.product_id having count(sol.product_id) > 0 order by qty desc;""")
				
				res = self._cr.fetchall()
				if len(res) < self.limit or self.limit < 1:
					raise except_orm(_('Invalid Top Limit'),_('Please enter a valid limit between 1 and %d'%(len(res))))
				final_res = (res[0 : self.limit])
				col_data = ['Name', 'Total']
				final_data = []
				for res in final_res:
					data = []
					product_id = self.env['product.product'].browse(res[0])
					if not product_id:
						continue
					name = product_id.name
					i = 1
					if len(product_id.attribute_value_ids) > 0:
						name += " ("
						for attribute in product_id.attribute_value_ids:
							name += attribute.name
							if i != len(product_id.attribute_value_ids):
								name += ", "
								i += 1
						name += ")"
					data.append(name)
					data.append(res[1])
					final_data.append(data)
				return self.generate_excel(col_data, final_data)

			else:
				self._cr.execute("""select sol.id from sale_order_line sol,sale_order so where so.state not in('draft','cancel','sent') and sol.product_id=%d and sol.order_id=so.id;
;"""%(self.product_id.id))
				sale_order_line_ids = self._cr.fetchall()
				ids = [v for v in sale_order_line_ids]
				sale_order_lines = self.env['sale.order.line'].search([('id','in',ids)])
				res = {}
				for sol in sale_order_lines:
					if sol.order_id and sol.order_id.partner_id and sol.order_id.partner_id.state_id:
						if sol.order_id.partner_id.state_id.id in res:
							res[sol.order_id.partner_id.state_id.id] += sol.product_uos_qty
						else:
							res.update({sol.order_id.partner_id.state_id.id: sol.product_uos_qty})

				final_res = []
				if self.limit < 1:
					raise except_orm(_('Invalid Top Limit'),_('Please enter a valid limit'))
				if len(res) == 0:
					raise except_orm(_('Warning'),_('No sale order created for this product'))
				res = sorted(res.iteritems(), key=lambda (k,v): v)
				if len(res) < self.limit:
					final_res = (res[0:])
				else:
					final_res = (res[len(res) - self.limit :])
				final_res.reverse()

				col_data = ['Name', 'Total']
				final_data = []
				for res in final_res:
					data = []
					data.append(self.env['res.country.state'].browse(res[0]).name)
					data.append(res[1])
					final_data.append(data)
				return self.generate_excel(col_data, final_data)
			
		elif self.filter_type == 'sales_person':
			if self.salesperson_filter == 'no_of_order':
				self._cr.execute("""select user_id, count(id) as total from sale_order where state not in ('draft','sent','cancel') group by user_id having count(id) > 0 order by total desc;""")
				res = self._cr.fetchall()
				if len(res) < self.limit or self.limit < 1:
					raise except_orm(_('Invalid Top Limit'),_('Please enter a valid limit between 1 and %d'%(len(res))))
				final_res = (res[0 : self.limit])
				col_data = ['Name', 'Total']
				final_data = []
				for res in final_res:
					data = []
					if res[1] <= 0.0:
						continue
					data.append(self.env['res.users'].browse(res[0]).name)
					data.append(res[1])
					final_data.append(data)
				return self.generate_excel(col_data, final_data)

			else:
				self._cr.execute("""select user_id, sum(amount_total) as total from sale_order where state not in ('draft','sent','cancel') group by user_id having sum(amount_total) > 0 order by total desc;""")
				res = self._cr.fetchall()
				if len(res) < self.limit or self.limit < 1:
					raise except_orm(_('Invalid Top Limit'),_('Please enter a valid limit between 1 and %d'%(len(res))))
				final_res = (res[0 : self.limit])
				col_data = ['Name', 'Total']
				final_data = []
				for res in final_res:
					data = []
					if res[1] <= 0.0:
						continue
					data.append(self.env['res.users'].browse(res[0]).name)
					data.append(res[1])
					final_data.append(data)
				return self.generate_excel(col_data, final_data)

		elif self.filter_type == 'state':
			sale_order = self.env['sale.order']
			if self.territory_filter == 'no_of_order':
				sale_orders = sale_order.search([('state','not in',['draft','sent','cancel']),('amount_total', '>', 0)])
				res = {}
				for order in sale_orders:
					if order.partner_id and order.partner_id.state_id:
						if order.partner_id.state_id.id in res:
							res[order.partner_id.state_id.id] += 1
						else:
							res.update({order.partner_id.state_id.id: 1})

				if len(res) < self.limit or self.limit < 1:
					raise except_orm(_('Invalid Top Limit'),_('Please enter a valid limit between 1 and %d'%(len(res))))
				res = sorted(res.iteritems(), key=lambda (k,v): v)
				final_res = (res[len(res) - self.limit :])
				final_res.reverse()

				col_data = ['Name', 'Total']
				final_data = []
				for res in final_res:
					data = []
					if res[1] <= 0.0:
						continue
					data.append(self.env['res.country.state'].browse(res[0]).name)
					data.append(res[1])
					final_data.append(data)
				return self.generate_excel(col_data, final_data)

			else:
				sale_orders = sale_order.search([('state','not in',['draft','sent','cancel']),('amount_total','>',0)])
				res = {}
				for order in sale_orders:
					if order.partner_id and order.partner_id.state_id:
						if order.partner_id.state_id.id in res:
							res[order.partner_id.state_id.id] += order.amount_total
						else:
							res.update({order.partner_id.state_id.id: order.amount_total})

				if len(res) < self.limit or self.limit < 1:
					raise except_orm(_('Invalid Top Limit'),_('Please enter a valid limit between 1 and %d'%(len(res))))
				res = sorted(res.iteritems(), key=lambda (k,v): v)
				final_res = (res[len(res) - self.limit :])
				final_res.reverse()

				col_data = ['Name', 'Total']
				final_data = []
				for res in final_res:
					data = []
					if res[1] <= 0.0:
						continue
					data.append(self.env['res.country.state'].browse(res[0]).name)
					data.append(res[1])
					final_data.append(data)
				return self.generate_excel(col_data, final_data)

	@api.multi
	def generate_excel(self, col_data, datas):
		workbook = xlsxwriter.Workbook('/tmp/reports.xlsx')
		worksheet = workbook.add_worksheet()
		row = 0
		col = 0
		for column_name in col_data:
			worksheet.write(row, col, column_name)
			col += 1
		row += 1
		for data in datas:
			col = 0
			for value in data:
				worksheet.write(row, col, value)
				col += 1
			row += 1
		workbook.close()

		with open("/tmp/reports.xlsx", 'r') as myfile:
			data = myfile.read()
			myfile.close()
		result = base64.b64encode(data)

		attachment_obj = self.env['ir.attachment']
		attachment_id = attachment_obj.create({'name': 'reports.xlsx', 'datas_fname': 'reports.xlsx', 'datas': result})
		download_url = '/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=' + str(attachment_id.id)
		base_url = self.env['ir.config_parameter'].get_param('web.base.url')

		return {
			"type": "ir.actions.act_url",
			"url": str(base_url) + str(download_url),
			"target": "new",
		}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: