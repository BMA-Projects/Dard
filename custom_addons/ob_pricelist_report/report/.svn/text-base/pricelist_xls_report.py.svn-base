import base64
import StringIO
import xlsxwriter
from openerp import models, fields, api, _

class xls_product_pricelist_wizard(models.TransientModel):
	_name = 'xls.product.pricelist.wizard'
	
	
	@api.multi
 	def product_pricelist_xls(self):
 		output =  StringIO.StringIO()
 		workbook = xlsxwriter.Workbook(output, {'in_memory': True})
 		worksheet = workbook.add_worksheet()
 		bold = workbook.add_format({'bold': True})
 		pricelist_item_obj = self.env['product.pricelist.item']
 		pricelist_item_browse_objs = pricelist_item_obj.search([],order='product_tmpl_id desc,min_quantity')
 		header_row = ['Pricelist Name', 'Currency', 'Version Name', 'Product Template Name', 'Product Name', 'Qty', 'Price', 'Discount']		
 		row = 0
 		[worksheet.write(row, header_cell, header_row[header_cell],bold) for header_cell in range(0,len(header_row))]
 		for pricelist_item in pricelist_item_browse_objs: 			
 			if pricelist_item.price_version_id and pricelist_item.price_version_id.pricelist_id.id in self._context.get('active_ids', False):
				row += 1
				row_data = [
							pricelist_item.price_version_id.pricelist_id.name,
							pricelist_item.price_version_id.pricelist_id.currency_id and pricelist_item.price_version_id.pricelist_id.currency_id.name,
							pricelist_item.price_version_id.name,
							pricelist_item.product_tmpl_id and pricelist_item.product_tmpl_id.name or '',
							pricelist_item.product_id and pricelist_item.product_id.name or '',
							pricelist_item.min_quantity,
							pricelist_item.price_surcharge,
							pricelist_item.price_discount,
						]
				[worksheet.write(row, col, row_data[col]) for col in range(0,len(row_data))]
 		workbook.close()
 		output.seek(0)
 		result = base64.b64encode(output.read())
 		attachment_obj = self.env['ir.attachment']
 		attachment_id = attachment_obj.create({'name': 'product_pricelist.xlsx', 'datas_fname': 'product_pricelist.xlsx', 'datas': result})
 		download_url = '/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=' + str(attachment_id.id)
 		base_url = self.env['ir.config_parameter'].get_param('web.base.url')
 		return {
 			"type": "ir.actions.act_url",
 			"url": str(base_url) + str(download_url),
 			"target": "self",
 		}