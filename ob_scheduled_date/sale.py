# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
import time
from datetime import datetime, timedelta, date, timedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta

class sale_order(models.Model):

    _inherit = 'sale.order'

    @api.onchange('ship_dt')
    @api.multi
    def onchange_ship_dt(self):
        new_date = self.date_order
        updated_date = datetime.strptime(new_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
        if self.ship_dt:
            if self.order_line:
                for line in self.order_line:
                    update_date = datetime.strptime(line.line_ship_dt, DEFAULT_SERVER_DATE_FORMAT).date()
                    delay = abs(updated_date-update_date).days
                    line.delay = delay
        elif not self.ship_dt:
            if self.order_line:
                for line in self.order_line:
                    line.delay=False


    @api.onchange('sc_date')
    @api.multi
    def onchange_sc_date(self):
        if self.sc_date:
            time=datetime.now().time()
            current_time=(time.strftime("%H:%M:%S"))
            self.planned_date=self.sc_date +' '+ current_time
            if self.order_line:
                for line in self.order_line:
                    line.line_sc_date = self.sc_date
                    line.line_planned_date = self.planned_date
        elif not self.sc_date:
            if self.order_line:
                for line in self.order_line:
                    line.line_planned_date = False
                    line.line_sc_date = False


    ship_dt = fields.Date('Ship Date', readonly=True, select=True, default=lambda *a: time.strftime('%Y-%m-%d'), states={'draft': [('readonly', False)],'sent': [('readonly', False)]})
    in_hand_date = fields.Date('In Hand Date', select=True, readonly=True, states={'draft': [('readonly', False)]}, help='In hand date should be after Ship Date')
    planned_date = fields.Datetime(string='Planned Date' )
    sc_date = fields.Date(string='Schedule Date', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    in_hand_date_visible = fields.Boolean(string='In Hand Date Required')

    def _get_date_planned(self, cr, uid, order, line, start_date, context=None):
        res = super(sale_order, self)._get_date_planned(cr, uid, order, line, start_date, context=context)
        if line.line_planned_date:
            routes = line.product_id.route_ids
            if routes.filtered(lambda r: r.name == 'Manufacture'):
                new_date = datetime.strptime(line.line_planned_date,DEFAULT_SERVER_DATETIME_FORMAT)
                procurement_date_planned = new_date + relativedelta(days=order.company_id.manufacturing_lead)
                date_planned = procurement_date_planned + relativedelta(days=line.product_id.produce_delay or 0.0)
                date_planned = (date_planned + timedelta(days=order.company_id.security_lead)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                date_planned = datetime.strptime(date_planned, '%Y-%m-%d %H:%M:%S')
                return date_planned
            elif routes.filtered(lambda r: r.name == "Buy"):
                new_date = datetime.strptime(line.line_planned_date,DEFAULT_SERVER_DATETIME_FORMAT)
                procurement_date_planned = new_date + relativedelta(days=order.company_id.po_lead)
                date_planned = (procurement_date_planned + timedelta(days=order.company_id.security_lead)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                date_planned = datetime.strptime(date_planned, '%Y-%m-%d %H:%M:%S')
                return date_planned
            else:
                return res
        else:
            return res

    def action_button_confirm(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            if not order.ship_dt:
                raise osv.except_osv(_('Warning'), _('Please enter the Ship Date'))
        return res

    def _get_ship_date(self, cr, uid, order, line, start_date, context=None):
        date_planned = datetime.strptime(start_date, DEFAULT_SERVER_DATETIME_FORMAT) 
        date_planned = (date_planned - timedelta(days=order.company_id.security_lead)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return date_planned

    def create(self, cr, uid, vals, context=None):
        updated_date = False
        if vals.has_key('in_hand_date_visible') and vals['in_hand_date_visible']:
            if vals.get('ship_dt', False):
                if isinstance(vals['ship_dt'], date):
                    ship_date_new = vals['ship_dt'].strftime('%Y-%m-%d')
                else:
                    ship_date_new = vals['ship_dt']
            if vals.get('ship_dt', False) and vals.get('in_hand_date', False) and vals.get('in_hand_date', False) < ship_date_new and vals.get('in_hand_date_visible', False) and vals['in_hand_date_visible']:
                raise osv.except_osv(_('Warning!'), _('In Hand Date should be after or equal to Ship Date'))
        if vals.has_key('ship_dt') and vals['ship_dt']:
            if vals.has_key('date_order') and vals['date_order']:
                date_order = vals['date_order']
                if len(date_order.split(' ')) <2:
                    date_order = vals['date_order'] + " " + str(datetime.now().time()).split('.')[0]
                date_order = datetime.strptime(date_order, DEFAULT_SERVER_DATETIME_FORMAT)
                date_order_new = date_order.date()
                ship_dt = datetime.strptime(str(vals['ship_dt']), DEFAULT_SERVER_DATE_FORMAT)
                ship_dt_new = ship_dt.date()
                if ship_dt_new < date_order_new :
                    raise osv.except_osv(_('Warning!'), _('Ship Date should be after or Equal to Order Date'))                 
        if vals.has_key('order_line') and vals.get('order_line') and vals.get('date_order'):
            new_date = vals.get('date_order')
            updated_date = datetime.strptime(new_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
            for line_rec in vals.get('order_line'):
                if line_rec[2] and line_rec[2].has_key('line_ship_dt') and line_rec[2].get('line_ship_dt'):
                    update_date = datetime.strptime(line_rec[2]['line_ship_dt'], DEFAULT_SERVER_DATE_FORMAT).date()
                    delay = updated_date and abs(updated_date-update_date).days or 0
                    line_rec[2].update({'delay':delay})

        if not vals.get('ship_dt'):
            vals['ship_dt'] = fields.date.today()

        order_id = super(sale_order, self).create(cr, uid, vals, context=context)
        order = self.browse(cr, uid, order_id, context=context)
        ship_date = []
        for line in order.order_line:
            if not line.line_ship_dt:
                line_ship_date = order.ship_dt
                update_date = datetime.strptime(line_ship_date ,'%Y-%m-%d').date()
                delay = updated_date and abs(updated_date-update_date).days or 0
                self.pool.get('sale.order.line').write(cr, uid, line.id, {'line_ship_dt': line_ship_date,'delay':delay}, context=context)

        return order_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(sale_order, self).write(cr, uid, ids, vals, context=context)
        if not ids:
            return res
        if ids and not isinstance(ids, (list)):
            ids = [ids]    
        current_rec = self.browse(cr, uid, ids[0], context=context)
        


        order_line_obj = self.pool.get('sale.order.line')
        for order in self.browse(cr, uid, ids, context=context):
            delay_list = []
            delay_dict = {}
            date_order = order.date_order or False
            new_ship_date = vals.get('ship_dt', False)

            if not new_ship_date and order:
                new_ship_date = order.ship_dt
            if new_ship_date and isinstance(new_ship_date, str):
                new_ship_date = new_ship_date +" "+ datetime.now().strftime('%H:%M:%S')
                if len(new_ship_date) > 10:
                    new_ship_date = new_ship_date.replace(new_ship_date[11:], datetime.now().strftime('%H:%M:%S'))
                    new_ship_date = datetime.strptime(new_ship_date, DEFAULT_SERVER_DATETIME_FORMAT)
                else:
                    new_ship_date = new_ship_date +" "+ datetime.now().strftime('%H:%M:%S')
                    new_ship_date = datetime.strptime(new_ship_date, DEFAULT_SERVER_DATETIME_FORMAT)

            #Convert date_order to datetime if it is of type 'str'
            if date_order and isinstance(date_order, str):
                if len(order.date_order) > 10:
                    date_order = datetime.strptime(order.date_order, DEFAULT_SERVER_DATETIME_FORMAT)
                else:
                    date_order = datetime.strptime(order.date_order, DEFAULT_SERVER_DATE_FORMAT)
            if vals.get('order_line') and vals.get('ship_dt'):
                for line in order.order_line:
                    if line.line_ship_dt:
                        linedate_new  = vals.get('ship_dt')# line.line_ship_dt
                        new_date = order.date_order
                        updated_date = datetime.strptime(new_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
                        update_date = datetime.strptime(linedate_new ,'%Y-%m-%d').date()
                        delay = abs(update_date -updated_date).days
                        order_line_obj.write(cr, uid, line.id, {'line_ship_dt': linedate_new,'delay': delay}, context=context)
                    if not line.line_ship_dt:
                        linedate_new  = order.ship_dt
                        new_date = order.date_order
                        updated_date = datetime.strptime(new_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
                        update_date = datetime.strptime(linedate_new ,'%Y-%m-%d').date()
                        delay = abs(update_date -updated_date).days
                        order_line_obj.write(cr, uid, line.id, {'line_ship_dt': linedate_new,'delay': delay}, context=context)
                    if line.id in delay_dict.keys():
                         delay_list.append(delay_dict.get(line.id))
                    else:
                        delay_list.append(line.delay)
                delay = delay_list and min(delay_list)
            if vals.get('ship_dt', False) and not context.get('from_create') and new_ship_date:
                if new_ship_date.date() < date_order.date():
                    raise osv.except_osv(_('Warning!'), _('Ship Date should be after or Equal to Order Date'))
                if current_rec.in_hand_date:
                    in_hand_date = datetime.strptime(current_rec.in_hand_date, DEFAULT_SERVER_DATE_FORMAT)
                    if vals.has_key('in_hand_date_visible') and vals['in_hand_date_visible']:
                        if (new_ship_date.date() > in_hand_date.date()):
                            raise osv.except_osv(_('Warning!'), _('In hand Date should be after or Equal to ship Date'))
            if current_rec.in_hand_date:
                in_hand_date = datetime.strptime(current_rec.in_hand_date, DEFAULT_SERVER_DATE_FORMAT)
                if vals.has_key('in_hand_date_visible') and vals['in_hand_date_visible']:
                    if (new_ship_date.date() > in_hand_date.date()):
                        raise osv.except_osv(_('Warning!'), _('In hand Date should be after or Equal to ship Date'))


                #Convert new_ship_date to datetime if it is of type 'str'
                if order.ship_dt and isinstance(order.ship_dt, str):
                    if len(order.ship_dt) > 10:
                        old_ship_date = datetime.strptime(order.ship_dt, DEFAULT_SERVER_DATETIME_FORMAT)
                    else:
                        old_ship_date = datetime.strptime(order.ship_dt, DEFAULT_SERVER_DATE_FORMAT)

            in_hand_date = vals.get('in_hand_date', False)


        if vals.get('in_hand_date', False):
            if len(vals.get('in_hand_date', False)) > 10:
                in_hand_date = datetime.strptime(vals.get('in_hand_date', False), DEFAULT_SERVER_DATETIME_FORMAT)
            else:
                in_hand_date = datetime.strptime(vals.get('in_hand_date', False), DEFAULT_SERVER_DATE_FORMAT)
            if current_rec.in_hand_date_visible or (vals.get('in_hand_date_visible', False) and vals['in_hand_date_visible']):
                if (new_ship_date and in_hand_date and in_hand_date.date() < new_ship_date.date()) or (current_rec.ship_dt and current_rec.ship_dt and current_rec.in_hand_date and current_rec.in_hand_date < current_rec.ship_dt):
                    raise osv.except_osv(_('Warning!'), _('In Hand Date should be after or equal to Ship Date'))
            #Check Ship date should be after order date
            if not context.get('by_pass', False):
                if new_ship_date and date_order and new_ship_date < date_order:
                    raise osv.except_osv(_('Warning!'), _('Ship Date should be after Order Date'))
        if vals.get('ship_dt', False) and not vals.get('in_hand_date', False):
            vals['in_hand_date'] = vals.get('ship_dt', False)
        if vals.get('ship_dt'):
            for line in order.order_line:
                linedate_new  = line.line_ship_dt
                new_date = order.date_order
                updated_date = datetime.strptime(new_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
                if linedate_new:
                    update_date = datetime.strptime(linedate_new,'%Y-%m-%d').date()
                else:
                    update_date = datetime.strptime(vals.get('ship_dt'),'%Y-%m-%d').date()
                delay = abs(update_date -updated_date).days
                if linedate_new:
                    order_line_obj.write(cr, uid, line.id, {'line_ship_dt': linedate_new,'delay':delay}, context=context)
                else:
                    order_line_obj.write(cr, uid, line.id, {'line_ship_dt': vals.get('ship_dt'), 'delay': delay},
                                         context=context)
        if not order.ship_dt:
            order.ship_dt = order.date_order
        return res


# Add SO In Hand Date to DO
class stock_move(models.Model):
    _inherit='stock.move'

    @api.cr_uid_ids_context
    def _picking_assign(self, cr, uid, move_ids, procurement_group, location_from, location_to, context=None):
        if not context: context = {}
        vals={}
        res = super(stock_move, self)._picking_assign(cr, uid, move_ids, procurement_group, location_from, location_to, context=context)
        group_rec = self.pool.get('procurement.group').browse(cr, uid, [procurement_group],context= context)
        if group_rec:
            sale_rec = self.pool.get('sale.order').search(cr, uid, [('name','=',group_rec.name)],context= context)
            if sale_rec:
                order_rec = self.pool.get('sale.order').browse(cr, uid, [sale_rec[0]],context= context)
                if order_rec:
                    picking_obj =self.pool.get('stock.picking')
                    recs = picking_obj.search(cr, uid, [('group_id','=',procurement_group)],context=context)
                    for rec in recs:
                        picking_rec = picking_obj.browse(cr, uid, [rec],context=context)
                        if picking_rec.min_date:
                            vals.update({'scheduled_date':picking_rec.min_date})
                        if order_rec.in_hand_date:
                            vals.update({'in_hand_date':order_rec.in_hand_date})
                        if order_rec.ship_dt:
                            vals.update({'ship_dt':order_rec.ship_dt})
                        if vals:
                            picking_obj.write(cr, uid, [rec], vals ,context=context)

        return res

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    
    line_ship_dt = fields.Date(string='Ship Date',default=fields.date.today())
    line_planned_date = fields.Datetime(string='Planned date')
    line_sc_date = fields.Date(string='Schedule Date')
    
    @api.onchange('line_sc_date')
    @api.multi
    def onchange_line_sc_date(self):
        if self.line_sc_date :
            time=datetime.now().time()
            current_time=(time.strftime("%H:%M:%S"))
            self.line_planned_date=self.line_sc_date +' '+ current_time
        elif not self.line_sc_date:
            self.line_planned_date = False

    @api.onchange('line_ship_dt')
    @api.multi
    def onchange_line_ship_dt(self):
        if self.line_ship_dt:
            new_date = self.order_id.date_order
            updated_date = datetime.strptime(new_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
            update_date = datetime.strptime(self.line_ship_dt, DEFAULT_SERVER_DATE_FORMAT).date()
            delay = abs(updated_date-update_date).days
            self.delay=delay
    
    @api.onchange('delay')
    @api.multi
    def onchange_line_delay(self):
        date_order = self.order_id.date_order
        updated_date = datetime.strptime(date_order, DEFAULT_SERVER_DATETIME_FORMAT).date()
        line_ship_date = updated_date + timedelta(days=self.delay)
        self.line_ship_dt = line_ship_date
               
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(sale_order_line, self).default_get(cr, uid, fields, context=context)
        if context.get('line_ship_dt'):
            res.update({'line_ship_dt': context.get('line_ship_dt')})
        return res



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
