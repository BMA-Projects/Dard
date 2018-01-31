# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

import openerp.addons.decimal_precision as dp
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import tools
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
import pytz
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import netsvc

#Added new module 'ob_sale_sample'
class sale_sample_type(osv.osv):

    _name = 'sale.sample.type'

    _columns = {
        "name": fields.char("Name", size=64),
        "desc": fields.char("Description", size=128),
        "active": fields.boolean("Active"),
    }

    _defaults = {
        "active": True,
    }

sale_sample_type()


class sale_order(osv.osv):

    _inherit = 'sale.order'

    _columns = {
        'sample_line_id': fields.one2many('sample.order.line', 'order_id', 'Sample Order Lines'),
        }

sale_order()


class sample_order_line(osv.osv):

    _name = 'sample.order.line'

    _columns = {
        "name": fields.char("Name", size=64),
        "sample_type": fields.many2one('sample.type', 'Types', select=True),
        'order_id': fields.many2one('sale.order', 'Order Reference', ondelete='cascade', select=True, readonly=True),
        'product_id': fields.many2one('product.product', 'Product'),
        'product_qty': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS')),
        'send_date': fields.date('Send Date'),
        'follow_up': fields.datetime('Follow Up', help="Follow up data should be greater then current date."),
        'alarm_id': fields.many2one('calendar.alarm', 'Reminder', help="Set an alarm at this time, before TODO call occurs" ),
#        'is_notify': fields.boolean('is notify ? '),
    }

    # _default = {
    #             'is_notify': False
    #         }

    def _check_follow_up(self, cr, uid, ids, context=None):
        obj_sample = self.browse(cr, uid, ids[0], context=context)
        cur_date = datetime.now()
        if obj_sample.follow_up:
            follow_up_date = datetime.strptime(obj_sample.follow_up, DEFAULT_SERVER_DATETIME_FORMAT)
            if follow_up_date < cur_date:
                return False
            else:
                return True
        return True


    _constraints = [
        (_check_follow_up, 'Error!\nThe follow up date of sales order must greater then current date.', ['follow_up'])
    ]


    def scheduler_manage_activity(self, cr, uid, domain=[], model_name=False, context=None):
        #This method is called by a cron task
        if context is None:
            context = {}
            
        time_now = (fields.datetime.context_timestamp(cr, uid, datetime.now(), context=context).strftime('%H:%M'))
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
               
                #===============================================================
                # occurs = alarm_data['trigger_occurs']
                # duration = (occurs == 'after' and alarm_data['trigger_duration']) \
                #                                 or -(alarm_data['trigger_duration'])
                #===============================================================
                
                duration = alarm_data['duration']
                if interval == 'hours':
                    delta = timedelta(hours=duration)
                if interval == 'minutes':
                    delta = timedelta(minutes=duration)
                remind_vals = self.handle_timedelta(cr, uid, delta, context=context)
                reminder_time = "{0:0=2d}".format(abs(remind_vals['hours'])) + ':' + "{0:0=2d}".format(remind_vals['minutes']) + ':' + "{0:0=2d}".format(remind_vals['seconds'])
                time_diff = datetime.strptime(default_time, tools.DEFAULT_SERVER_TIME_FORMAT) - datetime.strptime(reminder_time, tools.DEFAULT_SERVER_TIME_FORMAT)

                scheduled_time = datetime.strptime(activity_id.follow_up, tools.DEFAULT_SERVER_DATETIME_FORMAT)
                scheduled_time = pytz.utc.localize(scheduled_time).astimezone(tz)     # convert date in user's timezone
                scheduled_time = scheduled_time.strftime(tools.DEFAULT_SERVER_TIME_FORMAT)
                actual_reminder_time = datetime.strptime(str(scheduled_time), tools.DEFAULT_SERVER_TIME_FORMAT) - datetime.strptime(str(time_diff), tools.DEFAULT_SERVER_TIME_FORMAT)
                actual_vals = self.handle_timedelta(cr, uid, actual_reminder_time, context=context)
                actual_time = "{0:0=2d}".format(abs(actual_vals['hours'])) + ':' + "{0:0=2d}".format(actual_vals['minutes'])
                if actual_time == time_now:
                    self.do_mail(cr, uid, [activity_id.id], template_id, 'sample.order.line', context=context)

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

    def do_mail(self, cr, uid, id, template, model, context=None):
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
        for sample in self.browse(cr, uid, id, context=context):
            sale_uid = sample.order_id.user_id
            if sale_uid:
                group_obj = self.pool.get('res.groups')
                category_id = self.pool.get('ir.module.category').search(cr, uid, [('name','=','Sales')])
                manager_ids = group_obj.search(cr, uid, [('name','=', 'Manager'),('category_id','in',category_id)])
                user_ids = group_obj.browse(cr, uid, manager_ids, context=context)[0].users

                emails = []
                for user_id in user_ids:
                    if user_id.email:
                        emails.append(user_id.email)
                email_to = ''
                for email in emails:
                    email_to = email_to and email_to + ',' + email or email_to + email

                # email_to = ''
                # for user_id in user_ids:
                #     email_to = email_to and email_to + ',' + user_id.email or email_to + user_id.email

                email_id = res_partner_obj.browse(cr, uid, sale_uid.partner_id.id, context=context).email
                email_to = email_to and email_to + ',' + email_id
                email_template.write(cr, uid, template_id, {'email_to': email_to, 'reply_to': email_to, 'auto_delete': False}, context=context)
                email_template.send_mail(cr, uid, template_id, sample.id, force_send=True)
#                self.write(cr, uid, sample.id, {'is_notify': True}, context=context)
        return True

    def run_scheduler(self, cr, uid, context=None):
        date_today = datetime.strptime(fields.date.context_today(self, cr, uid, context=context), tools.DEFAULT_SERVER_DATE_FORMAT)
        limit_date = (date_today + relativedelta(days=+15)).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
#        domain = ['&', ('is_notify', '=', False), ('follow_up', '<', limit_date)]
        domain = [('follow_up', '<', limit_date)]
        self.scheduler_manage_activity(cr, uid, domain=domain, model_name='sample.order.line', context=context)
        return True
