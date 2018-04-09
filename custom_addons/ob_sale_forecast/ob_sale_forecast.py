from openerp import models, fields, api, _
from datetime import datetime,date
from openerp.exceptions import Warning
from openerp.tools.translate import _
from lxml import etree
from openerp.osv.orm import setup_modifiers
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class sale_forecast(models.Model):
	_name = 'sale.forecast' 

	name = fields.Char('Name', required=True,track_visibility='onchange')
	period = fields.Selection([('week','Week'),('month','Month'),('quarter','Quarter'),('year','Year')],'Period', required=True, copy=False, default='week')
	period_count= fields.Integer('No. of Periods', required=True)
	start_date = fields.Date(string='Start Date',required=True, default=datetime.today())
	product_ids = fields.Char(string="Product") 
	forecast_product_ids = fields.One2many('forecast.product', 'forecast_id', string='Forecast Products', default=False)
	forecast_filter_id = fields.Many2one('forecast.period',string="Filter", edit=False)
	filter_visible = fields.Boolean('filter_visible' ,defalut=False)
	warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse",select=True)
	# create_action = fields.Boolean(string="Do you want to create Supply for process quantity?", default=True)
	# required_process = fields.Selection([('buy','Buy'),('manufacture','Manufacture'),('both','Both'),('none','Not Required')],'Required Process', copy=False)
	record_generated = fields.Boolean('Record' ,defalut=False)

	@api.v7
	def onchange_forecast_filter(self, cr, uid, ids, forecast_filter_id, context=None):
		f_period_obj = self.pool.get('forecast.period')
		f_product_obj = self.pool.get('forecast.product')
		if not ids:
			return {} 
		if forecast_filter_id:
			s_rec = f_product_obj.search(cr, uid, [('forecast_id','=',ids[0]),('period_start_date','=',f_period_obj.browse(cr, uid, forecast_filter_id,context ).p_date)])
			
		else:
			s_rec = f_product_obj.search(cr, uid, [('forecast_id','=',ids[0])])
		
		return {
			'value': {'forecast_product_ids': [(4,x) for x in s_rec]},
			'domain': {'forecast_product_ids': ['id' ,'in', s_rec]}
		}

	@api.model
	def create(self, vals):
		if vals.has_key('period_count'):
			if vals['period_count'] < 0:
				raise Warning(_('Number of Periods should not be less than zero'))
		return super(sale_forecast, self).create(vals)

	@api.multi
	def write(self, vals):
		if vals.has_key('forecast_filter_id'):
			vals['forecast_filter_id'] = False
		if vals.has_key('period_count'):
			if vals['period_count'] <= 0:
				raise Warning(_('Number of Periods should be grater than zero'))
		return super(sale_forecast,self).write(vals)

	@api.multi
	def get_period(self, period, start_date, period_count):
		res, period_list = [], []
		period_env = self.env['forecast.period']
		search_period_ids = period_env.search([('forecast_id', '=', self.id)])
		if search_period_ids:
			search_period_ids.unlink()
		if period == 'week':
			for item in range(period_count):
				week_date = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
				res.append(week_date)
				new_week_date = week_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
				new_start_date = datetime.strptime(new_week_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(weeks=1) + relativedelta(days=1)
				start_date = new_start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
		elif period == 'month':
			for item in range(period_count):
				month_date = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
				res.append(month_date)
				new_month_date = month_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
				new_start_date = datetime.strptime(new_month_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=1) + relativedelta(days=1)
				start_date = new_start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
		elif period == 'quarter':
			for item in range(period_count):
				quarter_date = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
				res.append(quarter_date)
				new_quarter_date = quarter_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
				new_start_date = datetime.strptime(new_quarter_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=3) + relativedelta(days=1)
				start_date = new_start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
		elif period == 'year':
			for item in range(period_count):
				year_date = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
				res.append(year_date)
				new_year_date = year_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
				new_start_date = datetime.strptime(new_year_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(years=1) + relativedelta(days=1)
				start_date = new_start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
		for start_date in res:
			vals = {
				'name': start_date.strftime(DEFAULT_SERVER_DATE_FORMAT),
				'p_date': start_date.strftime(DEFAULT_SERVER_DATE_FORMAT),
				'forecast_id': self.id
			}
			period_list.append(period_env.create(vals))
		self.filter_visible = True
		return period_list

	@api.multi
	def generate_forecast(self):
		self.record_generated = True
		for rec in self:
			rec.write({'forecast_product_ids':[(5,0)]})
		forecast_product_obj = self.env['forecast.product']
		if self.period and self.start_date and self.period_count:
			periods = self.get_period(self.period, self.start_date, self.period_count)
		elif self.period_count <= 0:
			raise Warning(_('Number of Periods should be grater than Zero'))
			
		if self.product_ids:
			domain =  eval(self.product_ids)
			product_ids = self.env['product.product'].search(domain)
		else:
			raise Warning(_('Atleast one product should be selected!'))

		first_period = True

		for index,item in enumerate(periods):
			if self.period == 'week':
				expected_end_date = datetime.strptime(item.name, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(weeks=1)
				end_date = expected_end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
			elif self.period == 'month':
				expected_end_date = datetime.strptime(item.name, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=1)
				end_date = expected_end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
			elif self.period == 'quarter':
				expected_end_date = datetime.strptime(item.name, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=3)
				end_date = expected_end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
			elif self.period == 'year':
				expected_end_date = datetime.strptime(item.name, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(years=1)
				end_date = expected_end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
			
			for product in product_ids:
				product_template_id = product.product_tmpl_id
				# routes = self.env['product.template'].search([('id','=',product_template_id.id)]).route_ids
				# mto_route_id = self.env['stock.location.route'].search([('name','=','Make To Order')]).id
				# if routes:
				# 	if routes.filtered(lambda r: r.id == mto_route_id):
				# 		action = 'none'
				# 	else:
				# 		if routes.filtered(lambda r: r.name == 'Buy') and routes.filtered(lambda r: r.name == 'Manufacture'):
				# 			action = 'both'
				# 		else:
				# 			for route in routes:
				# 				if route.name == 'Buy':
				# 					action = 'buy'
				# 				elif route.name == 'Manufacture':
				# 					action = 'manufacture'
				# else:
				# 	action = 'none'

				ctx = self._context.copy()
				ctx.update({'from_date': item.name, 'to_date': end_date, 'warehouse': self.warehouse_id.id, 'current_model': self._model, 'rec_id': self.id})
				product_qty = self.pool.get('product.product')._product_available(self._cr, self._uid, [product.id], False, False, ctx)
				qty_list = product_qty.get(product.id)
				if first_period == True:
					new_rest_period_qty = qty_list['qty_available']
					available_qty = new_rest_period_qty
				else:
					available_qty = 0.0

				vals = {
					'name': product.name + ' on ' + str(item.name),
					'forecast_id': self.id,
					'product_id': product.id,
					'period_start_date': item.name,
					'period_end_date': end_date,
					'onhand_qty': available_qty,
					'incoming_qty': qty_list['incoming_qty'],
					'outgoing_qty': qty_list['outgoing_qty'],
					'rest_period_qty': available_qty,
					# 'action_required': action,
				}
				created_id = forecast_product_obj.create(vals)
			first_period = False

	@api.multi
	def update_action_qty(self):

		forecast_product_obj = self.env['forecast.product']
		if self.forecast_filter_id:
			recs = self.env['forecast.product'].search([('forecast_id','=',self.id),('period_start_date','=',self.forecast_filter_id.name)])
			self.forecast_filter_id = False
		else:
			recs = self.env['forecast.product'].search([('forecast_id','=',self.id)])
		for rec in recs:
			if rec.forecast_qty:
				if not rec.onhand_qty:
					previous_period_date = rec.period_start_date
					new_date = datetime.strptime(previous_period_date, DEFAULT_SERVER_DATE_FORMAT) - relativedelta(days=1)
					previous_period_end_date = new_date.strftime(DEFAULT_SERVER_DATE_FORMAT)					
					new_rest_period_qty = self.env['forecast.product'].search([('product_id','=',rec.product_id.id),('period_end_date','=',previous_period_end_date),('forecast_id','=',self.id)]).action_qty
					if new_rest_period_qty < 0:
						rec.rest_period_qty =  - (new_rest_period_qty)
					else:
						rec.rest_period_qty = 0
				else:
					rec.rest_period_qty = rec.onhand_qty 
		
				qty = rec.forecast_qty - (rec.rest_period_qty + rec.incoming_qty - rec.outgoing_qty)
				vals = {'action_qty': qty,'forecast_qty': rec.forecast_qty}
				# if qty < 0:
				# 	vals.update({'action_required':'none'})
				forecast_product_obj.browse(rec.id).write(vals)

class product_product(models.Model):
	_inherit = 'product.product'	

	@api.multi
	def _get_domain_dates(self):
		for record in self:
			if (self._context.has_key('current_model') and self._context['current_model']) and (self._context.has_key('rec_id') and self._context['rec_id']):
				# if self._context['current_model'] == 'sale.forecast':
				record_id = self._context['rec_id']
				generated_record = self.env['sale.forecast'].browse(record_id).record_generated
				if generated_record:
					from_date = self._context.get('from_date', False)
					to_date = self._context.get('to_date', False)
					domain = []
					if from_date:
						domain.append(('date_expected', '>=', from_date))
					if to_date:
						domain.append(('date_expected', '<=', to_date))
					return domain
			return super(product_product,self)._get_domain_dates()

class forecast_period(models.Model):

	_name = 'forecast.period'

	_rec_name = 'p_date'

	name = fields.Char('Period Name', edit=False)
	p_date = fields.Date('Period Date')
	forecast_id = fields.Many2one('sale.forecast', string='Forecast', edit=False)

class forecast_product(models.Model):

	_name = 'forecast.product'

	name = fields.Char('Name')
	forecast_id = fields.Many2one('sale.forecast', string='Forecast')
	product_id = fields.Many2one('product.product', string='Product')
	period_start_date = fields.Date('Start Date')
	period_end_date = fields.Date('End Date')
	sales_person = fields.Many2one('res.users', string='Salesperson')
	sales_team = fields.Many2one('crm.case.section', string='Sales Team')
	forecast_qty = fields.Float('Forecast Qty')
	onhand_qty = fields.Float('Onhand Qty')
	rest_period_qty = fields.Float('Rest Period Qty')
	incoming_qty = fields.Float('Incoming Qty')
	outgoing_qty = fields.Float('Outgoing Qty')
	action_qty = fields.Float('Action Qty')
	# document_number = fields.Char('Ref.Doc.No.')
	# action_required = fields.Selection([('buy','Buy'),('manufacture','Manufacture'),('both','Both'),('none','Not Required')],'Action Required', copy=False)

	@api.multi
	def unlink(self):
		'''
		Here as per the selection of forecast_filter_id the records other than the filter value are not managable as filter is applying on One2many field.
		so, by default unlink method is called for the records other than the filter records.
		To resolve this here unlink method is marked as false, as delete functionality has been removed  for this perticular field once the record is created.
		'''
		return False

