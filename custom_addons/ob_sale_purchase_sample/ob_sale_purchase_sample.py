# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

import ast
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
from openerp import api, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_compare

class sale_configuration(osv.osv_memory):
    _inherit = 'sale.config.settings'

    _columns = {
        'group_convert_order_in_zero': fields.boolean("Convert Order in Sample with Zero Price", implied_group='ob_sale_purchase_sample.group_sample_order'),
        }

class sale_order(osv.osv):

    _inherit = 'sale.order'

    _columns = {
        'is_sample': fields.boolean('Sample', select=True, help="Is this a Sample Quotation/Sale Order?"),


        "sample_type": fields.many2one('sample.type', 'Types', select=True),
        'follow_up': fields.datetime('Follow Up', help="Follow up data should be greater then current date."),
        'alarm_id': fields.many2one('calendar.alarm', 'Reminder', help="Set an alarm at this time, before TODO call occurs" ),
        }
    
    def copy(self, cr, uid, ids, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'is_sample': False,
        })
        return super(sale_order, self).copy(cr, uid, ids, default, context=context)

    def copy_quotation(self, cr, uid, ids, context=None):
        res_id = self.copy(cr, uid, ids[0], context=None)
        my_fields = self.fields_get(cr, uid, context=context)
        if my_fields.get('is_sample'):
            self.write(cr, uid, [res_id], {'is_sample': False}, context=context)
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'view_order_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales Order'),
            'res_model': 'sale.order',
            'res_id': res_id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

    def onchange_sample(self, cr, uid, ids, is_sample, context=None):
        return {'value': {'sample_type': False}}

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        res = super(sale_order, self).write(cr, uid, ids, vals, context=context)
        if 'from_write_itself' in context and 'from_update_itself' in context:
            if context.get('from_write_itself',False) and context.get('from_update_itself',False):
                return res
        if ids and not isinstance(ids, (list)):
            ids = [ids]
        cur_record = self.browse(cr, uid, ids, context=context)[0]
        sale_config_obj = self.pool.get('sale.config.settings')
        fields = sale_config_obj.fields_get(cr, uid, context=context)
        config_res = sale_config_obj.default_get(cr, uid, fields, context=context)
        orderline_obj = self.pool.get('sale.order.line')
        orderline_fields = orderline_obj.fields_get(cr, uid, context=context)
        if config_res.has_key('group_convert_order_in_zero') and config_res['group_convert_order_in_zero'] == True and cur_record and 'is_sample' in vals and vals.get('is_sample',False):
            if 'parent_order_line_id' in orderline_fields:
                valid_line_ids = [line.id for line in cur_record.order_line if line.parent_order_line_id.id == False]
                for line_id in valid_line_ids:
                    line_vals = {
                        'price_unit': 0,
                        'discount': 0,
                        'tax_id': [[6, 0, []]]
                    }
                    orderline_obj.write(cr, uid, [line_id], line_vals, context=context)
            else:
                for line_id in cur_record.order_line:
                    line_vals = {
                            'price_unit': 0,
                            'discount': 0,
                            'tax_id': [[6, 0, []]]
                    }
                    orderline_obj.write(cr, uid, [line_id.id], line_vals, context=context)
        return res


    def _prepare_order_line_procurement(self, cr, uid, order, line, group_id=False, context=None):
        result = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order, line, group_id=group_id, context=context)
        if order.is_sample or False:
            result.update({'is_sample': order.is_sample})
        if order.sample_type or None:
            result.update({'sample_type': order.sample_type.id})
        return result

    # def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
    #     res = super(sale_order, self)._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned, context=context)
    #     if order.is_sample or False:
    #         res.update({'is_sample': order.is_sample})
    #     if order.sample_type or None:
    #         res.update({'sample_type': order.sample_type.id})
    #     return res

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        res = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context=context)
        if order.is_sample or False:
            res.update({'is_sample': order.is_sample})
        if order.sample_type or None:
            res.update({'sample_type': order.sample_type.id})
        return res

    def action_ship_create(self, cr, uid, ids, context=None):
        if not context: context = {}
        procurement_obj = self.pool.get('procurement.order')
        for order in self.browse(cr, uid, ids, context=context):
            if order.procurement_group_id.procurement_ids:
                for proc in order.procurement_group_id.procurement_ids:
                    procurement_obj.write(cr, uid, [proc.id], {'is_sample': proc.is_sample, 'sample_type': proc.sample_type.id}, context=context)
        return super(sale_order, self).action_ship_create(cr, uid, ids, context)


    def scheduler_manage_activity(self, cr, uid, domain=[], model_name=False, context=None):
        #This method is called by a cron task
        if context is None:
            context = {}
        time_now = (fields.datetime.context_timestamp(cr, uid, datetime.now(), context=context).strftime('%H:%M'))
        time_now2 = (fields.datetime.context_timestamp(cr, uid, datetime.now(), context=context)).date()
        template_id = 'email_template_sale_sample'
        ids = self.search(cr, uid, domain, offset=0, limit=None, order=None, context=context, count=False)
        alarm_object = self.pool.get('calendar.alarm')
        default_time = "{0:0=2d}".format(23) + ':' + "{0:0=2d}".format(59) + ':' + "{0:0=2d}".format(59)
        user = self.pool.get('res.users').browse(cr, uid, uid)
        tz = pytz.timezone(user.tz) if user.tz else pytz.utc
        for activity_id in self.browse(cr, uid, ids, context=context):
            if activity_id.alarm_id:
                alarm_data = alarm_object.read(cr, uid, activity_id.alarm_id.id, context=context)
                interval = alarm_data['interval']
                duration = alarm_data['duration']

                if interval == 'hours':
                    delta = timedelta(hours=duration)
                if interval == 'minutes':
                    delta = timedelta(minutes=duration)

                remind_vals = self.handle_timedelta(cr, uid, delta, context=context)
                reminder_time = "{0:0=2d}".format(abs(remind_vals['hours'])) + ':' + "{0:0=2d}".format(remind_vals['minutes']) + ':' + "{0:0=2d}".format(remind_vals['seconds'])
                time_diff = datetime.strptime(default_time, tools.DEFAULT_SERVER_TIME_FORMAT) - datetime.strptime(reminder_time, tools.DEFAULT_SERVER_TIME_FORMAT)
                scheduled_time = datetime.strptime(activity_id.follow_up, tools.DEFAULT_SERVER_DATETIME_FORMAT)
                scheduled_time_date = (pytz.utc.localize(scheduled_time).astimezone(tz)).date()
                scheduled_time = pytz.utc.localize(scheduled_time).astimezone(tz)     # convert date in user's timezone
                scheduled_time = scheduled_time.strftime(tools.DEFAULT_SERVER_TIME_FORMAT)
                actual_reminder_time = datetime.strptime(str(scheduled_time), tools.DEFAULT_SERVER_TIME_FORMAT) - datetime.strptime(str(reminder_time), tools.DEFAULT_SERVER_TIME_FORMAT)
                actual_vals = self.handle_timedelta(cr, uid, actual_reminder_time, context=context)
                actual_time = "{0:0=2d}".format(abs(actual_vals['hours'])) + ':' + "{0:0=2d}".format(actual_vals['minutes'])
                if time_now2 == scheduled_time_date and actual_time == time_now:
                    self.do_mail(cr, uid, activity_id, template_id, context=context)

    def handle_timedelta(self, cr, uid, datetime_val, context=None):
        if context is None:
            context = {}
        if datetime_val:
            vals = {}
            vals['seconds'] = datetime_val.seconds
            vals['hours'] = vals['seconds'] // 3600
            vals['minutes'] = vals['seconds'] % 3600 // 60
            vals['seconds'] = vals['seconds'] % 60
            return vals
        return False

    def do_mail(self, cr, uid, id, template, context=None):
        if context is None:
            context = {}
        activity_id = id
        email_template = self.pool.get('email.template')
        res_partner_obj = self.pool.get('res.partner')
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'sale', template)[1]
        except ValueError:
            template_id = False
        if activity_id.user_id:
            group_obj = self.pool.get('res.groups')
            category_id = self.pool.get('ir.module.category').search(cr, uid, [('name','=','Sales')])
            manager_ids = group_obj.search(cr, uid, [('name','=', 'Manager'),('category_id','in',category_id)])
            user_ids = group_obj.browse(cr, uid, manager_ids, context=context)[0].users
            email_to = ''
            for user_id in user_ids:
                email_to = email_to and email_to + ',' + user_id.email or email_to + user_id.email
            email_id = res_partner_obj.browse(cr, uid, activity_id.user_id.partner_id.id, context=context).email
            email_to = email_to and email_to + ',' + email_id
            email_template.write(cr, uid, template_id, {'email_to': email_to, 'reply_to': email_to, 'auto_delete': False}, context=context)
            email_template.send_mail(cr, uid, template_id, activity_id.id, force_send=True)
        return True

    def run_scheduler(self, cr, uid, context=None):
        date_today = datetime.strptime(fields.date.context_today(self, cr, uid, context=context), tools.DEFAULT_SERVER_DATE_FORMAT)
        limit_date = (date_today + relativedelta(days=+15)).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        domain = ['&', ('is_sample', '=', True), ('follow_up', '<', limit_date)]
        self.scheduler_manage_activity(cr, uid, domain, context=context)
        return True


class sale_order_line(osv.osv):

    _inherit = "sale.order.line"

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        is_sample = self.pool.get('sale.order').browse(cr, uid, vals.get('order_id'), context).is_sample
        sale_config_obj = self.pool.get('sale.config.settings')
        fields = sale_config_obj.fields_get(cr, uid, context=context)
        config_res = sale_config_obj.default_get(cr, uid, fields, context=context)
        if config_res.has_key('group_convert_order_in_zero') and config_res['group_convert_order_in_zero'] == True and is_sample == True:
            vals['price_unit'] = 0
            vals['setup_charge'] = 0
            vals['run_charge'] = 0
            vals['up_charge'] = 0
            vals['ltm_charge'] = 0
            vals['pms_charge'] = 0
        return super(sale_order_line, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        sale_config_obj = self.pool.get('sale.config.settings')
        fields = sale_config_obj.fields_get(cr, uid, context=context)
        config_res = sale_config_obj.default_get(cr, uid, fields, context=context)
        sale_fields = self.fields_get(cr, uid, context=context).keys()
        is_sample = False
        if ids:
            current_record = self.browse(cr, uid, ids, context=context)[0]
            is_sample = current_record.order_id.is_sample
        if config_res.has_key('group_convert_order_in_zero') and config_res['group_convert_order_in_zero'] == True  and is_sample == True:
            if 'ltm_charge' in sale_fields:
                vals.update({'ltm_charge': 0})
            if 'run_charge' in sale_fields:
                vals.update({'run_charge': 0})
            if 'up_charge' in sale_fields:
                vals.update({'up_charge': 0})
            if 'setup_charge' in sale_fields:
                vals.update({'setup_charge': 0})
            if 'pms_charge' in sale_fields:
                vals.update({'pms_charge': 0})
            vals.update({'price_unit': 0})
        res = super(sale_order_line, self).write(cr, uid, ids, vals, context=context)
        return res

class procurement_order(osv.osv):
    _inherit = "procurement.order"

    _columns = {
        'is_sample': fields.boolean('Sample', select=True, readonly=True),
        "sample_type": fields.many2one('sample.type', 'Types', select=True),
        }

    @api.v7
    def make_po(self, cr, uid, ids, context=None):
        res = super(procurement_order, self).make_po(cr, uid, ids, context=context)
        purchase_order_obj = self.pool.get('purchase.order')
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.purchase_id:
                purchase_order_obj.write(cr, uid, [procurement.purchase_id.id], {'is_sample': procurement.is_sample, 'sample_type': procurement.sample_type.id}, context=context)
        return res

    def _run_move_create(self, cr, uid, procurement, context=None):
        res = super(procurement_order, self)._run_move_create(cr, uid, procurement, context)
        res.update({'is_sample': procurement.is_sample, 'sample_type': procurement.sample_type.id})
        return res


class purchase_order(osv.osv):
    _inherit = "purchase.order"

    _columns = {
        'is_sample': fields.boolean('Sample', select=True, readonly=True),
        "sample_type": fields.many2one('sample.type', 'Types', select=True),
        }

    def action_picking_create(self, cr, uid, ids, context=None):
        context = context.copy()
        for order in self.browse(cr, uid, ids, context=context):
            context.update({
                'is_sample': order.is_sample,
                'sample_type': order.sample_type.id
            })
        return super(purchase_order, self).action_picking_create(cr, uid, ids, context=context)

    def action_invoice_create(self, cr, uid, ids, context=None):
        account_invoice_obj = self.pool.get('account.invoice')
        res = super(purchase_order, self).action_invoice_create(cr, uid, ids, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            for invoice_rec in order.invoice_ids:
                account_invoice_obj.write(cr, uid, invoice_rec.id, {'is_sample': order.is_sample, 'sample_type': order.sample_type.id}, context=context)
        return res

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    _columns = {
        'is_sample': fields.boolean('Sample', select=True, readonly=True),
        "sample_type": fields.many2one('sample.type', 'Types', select=True),
        }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if context.get('is_sample',False) and context.get('sample_type',False):
            vals.update({
                'is_sample': context.get('is_sample'),
                'sample_type': context.get('sample_type')
            })
        res = super(stock_picking, self).create(cr, uid, vals, context=context)
        return res

class stock_move(osv.osv):
    _inherit = 'stock.move'

    _columns = {
        'is_sample': fields.boolean('Sample', select=True, readonly=True),
        "sample_type": fields.many2one('sample.type', 'Types', select=True),
        }

    def create(self, cr, uid, vals, context=None):
        if context.get('is_sample',False) and context.get('sample_type',False):
            vals.update({
                'is_sample': context.get('is_sample'),
                'sample_type': context.get('sample_type')
            })
        res = super(stock_move, self).create(cr, uid, vals, context=context)
        return res

    def _prepare_procurement_from_move(self, cr, uid, move, context=None):
        res = super(stock_move, self)._prepare_procurement_from_move(cr, uid, move, context)
        if move.is_sample or False:
            res.update({'is_sample': move.is_sample})
        if move.sample_type or None:
            res.update({'sample_type': move.sample_type.id})
        return res

    @api.cr_uid_ids_context
    def _picking_assign(self, cr, uid, move_ids, procurement_group, location_from, location_to, context=None):
        if context is None:context = {}
        pick_obj = self.pool.get("stock.picking")
        move = self.browse(cr, uid, move_ids, context=context)[0]
        picks = pick_obj.search(cr, uid, [
                ('group_id', '=', procurement_group),
                ('location_id', '=', location_from),
                ('location_dest_id', '=', location_to),
                ('state', 'in', ['draft', 'confirmed', 'waiting']),
                ('partner_id', '=', move.partner_id.id)], context=context)
        if picks:
            pick_obj.write(cr, uid, picks, {'is_sample': move.is_sample, 'sample_type': move.sample_type.id}, context=context)
#         move = self.browse(cr, uid, move_ids, context=context)[0]
#         context = context.copy()
#         print "COntext SALE SAMPLE : ",context
#         context.update()
#         print "Context....UPDATED :: ",context
        return super(stock_move, self)._picking_assign(cr, uid, move_ids, procurement_group, location_from, location_to, context=context)

#     def _picking_assign(self, cr, uid, move_ids, procurement_group, location_from, location_to, context=None):
#         if context is None:context = {}
#         move = self.browse(cr, uid, move_ids, context=context)[0]
#         context = context.copy()
#         context.update({'is_sample': move.is_sample, 'sample_type': move.sample_type.id})
#         res = super(stock_move, self)._picking_assign(cr, uid, move_ids, procurement_group, location_from, location_to, context=context)
#         return res


class account_invoice(osv.osv):

    _inherit = "account.invoice"

    _columns = {
        'is_sample': fields.boolean('Sample', select=True, readonly=True),
        "sample_type": fields.many2one('sample.type', 'Types', select=True),
        }
