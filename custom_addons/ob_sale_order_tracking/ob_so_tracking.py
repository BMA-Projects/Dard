# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models,fields,api,_
from datetime import datetime
from openerp.exceptions import Warning
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as dt

class so_tracking_stage(models.Model):
    _name = 'so.tracking.stage'
    _description = 'Sales Order Tracking stage'
    _order = 'sequence'

    name = fields.Char('Stage Name', required=True, size=64, translate=True)
    description = fields.Text('Description')
    user_allow_ids = fields.Many2many('res.users','res_user_rel','res_id','id',string='Users', copy=True)
    sequence = fields.Integer('Sequence', default=1)
    case_default = fields.Boolean('Default for New Tracking', default=False, help="If you check this field, this stage will be proposed by default on each new SO tracking.")
    fold = fields.Boolean('Folded by Default', default=False, help="This stage is not visible, for example in status bar or kanban view, when there are no records in that stage to display.")
    max_time_limit = fields.Integer(string="Max Time Limit", help="Specify the time limit or period")
    company_id = fields.Many2one("res.company", "Company", default=lambda self: self.env.user.company_id)
    time_selection = fields.Selection([('hours', 'Hours'), ('days','Days')], "Time Selection", default='hours', required=True)

    @api.onchange('case_default')
    def _onchange_case_default(self):
        if self.case_default:
            search_data = self.search([('case_default','=',True),('company_id','=',self.env.user.company_id.id)])
            if search_data:
                search_data.write({'case_default': False})

class so_tracking(models.Model):
    _name = 'so.tracking'
    _description = 'Sale Order Tracking'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _read_group_stage_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        stage_obj = self.pool.get('so.tracking.stage')
        stage_ids = stage_obj._search(cr, uid, [], context=context)
        result = stage_obj.name_get(cr, access_rights_uid, stage_ids, context=context)

        fold = {}
        for stage in stage_obj.browse(cr, access_rights_uid, stage_ids, context=context):
            fold[stage.id] = stage.fold or False
        return result, fold

    _group_by_full = {
        'stage_id': _read_group_stage_ids
    }

    name = fields.Char('Tracking No', size =64, required=True, readonly=True, default='/')
    stage_id = fields.Many2one('so.tracking.stage', 'SO tracking stage', track_visibility='onchange')
    time_selection = fields.Selection(related="stage_id.time_selection", string="Time selection")
    # sale_order_id = fields.Many2one('sale.order', string='sale order')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order',ondelete='cascade', select=True)
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    client_order_ref = fields.Char('Customer PO Number', size=64)
    user_id = fields.Many2one('res.users', 'Order Processor', readonly=True)
    date_order = fields.Date('Date', readonly=True)
    # confirm_date = fields.Date('Order Confirm On', readonly=True)##ob_sale
    invoiced = fields.Boolean(string='Paid', readonly=True, help="It indicates that an invoice has been paid.")
    shipped = fields.Boolean(string='Delivered', readonly=True, help="It indicates that the sales order has been delivered. This field is updated only after the scheduler(s) have been launched.")##sale_stock
    order_line = fields.One2many(string="Sale Order lIne", related='sale_order_id.order_line')
    amount_untaxed = fields.Float('Untaxed Amount')
    amount_tax = fields.Float('Taxes')
    amount_total = fields.Float('Total', help="The total amount.")
    color = fields.Integer('Color Index')
    update_time = fields.Datetime(string='Updated time')
    since = fields.Integer(string = 'Since', readonly=True)
    # rush_order = fields.Boolean('Is Rush Order ?', readonly=True)##ob_sale
    max_time_limit = fields.Integer(string="Max Time Limit", help="Specify the time limit or period from stage")
    company_id = fields.Many2one("res.company","Company",compute='_get_company_id',store=True)
    time_selection_related = fields.Selection(related='stage_id.time_selection', selection=[('hours', 'Hours'), ('days','Days')], string="Time Selectio", store=True)

    _order="since desc"

    @api.depends('sale_order_id.company_id')
    def _get_company_id(self):
        for rec in self:
            rec.company_id = rec.sale_order_id.company_id

    @api.one
    def unlink(self):
        sale_obj = self.env['sale.order']
        #Remove stage reference from SO when tracking is removed
        for tracking in self:
            if tracking.sale_order_id:
                sale_obj.write( {'so_tracking_stage_id': False})
        return super(so_tracking, self).unlink()

    @api.model
    def create(self, vals):
        sale_obj = self.env['sale.order']
        sale_vals = {}
        stage_id = False
        seq = self.env['ir.sequence'].get('so.tracking') or '/'
        vals['name'] = seq
        if vals.get('stage_id',False):
            vals.update({'update_time':datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        return super(so_tracking, self).create(vals)

    @api.v8
    def calculate_since_value(self, upd_time=False, time_selection=False):
        total_time = 0
        if time_selection and time_selection == 'hours':
            from_date = datetime.strptime(datetime.strftime(datetime.now(),dt), dt)
            time_diff =  from_date - datetime.strptime(upd_time, dt)
            total_time = time_diff.total_seconds()/3600
        elif time_selection and time_selection == 'days':
            from_date = datetime.strptime(datetime.strftime(datetime.now(),dt), dt)
            time_diff = from_date - datetime.strptime(upd_time, dt)
            dir(time_diff)
            total_time = time_diff.days
        return total_time

    @api.multi
    def read(self,fields, load='_classic_read'):
        res = super(so_tracking,self).read(fields,load=load)
        for data in self:
            vals = {}
            time_limit = data.stage_id.max_time_limit
            vals.update({'max_time_limit':time_limit})
            if data.update_time:
                t_time = self.calculate_since_value(upd_time=data.update_time, time_selection=data.stage_id and data.stage_id.time_selection or False)
                if not t_time:
                    t_time = 0
                if t_time >= time_limit and time_limit != 0:
                    vals.update({'color':2})
                else:
                    vals.update({'color':0})
                vals.update({
                    'since': t_time,
                })
                data.write(vals)
        return res

    @api.multi
    def write(self, vals):
        sale_id = False
        sale_vals = {}
        sale_obj = self.env['sale.order']
        for order_tracking in self:
            sale_id = order_tracking.sale_order_id and order_tracking.sale_order_id.id
            if sale_id and vals.get('stage_id', False):
                stage_id = vals.get('stage_id', False)
                if stage_id:
                    stage_comp_id = self.env['so.tracking.stage'].search([('id','=',stage_id)]).company_id.id
                    if stage_comp_id != self.company_id.id:
                        raise Warning(_("Not able to move to this stage as it is belong to different company."))

                upd_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.write({'update_time': upd_time, 'since': 0})
                if not self._context.get('stage_from_sale', False):
                    sale_vals.update({'so_tracking_stage_id': vals['stage_id']})
                    sale_obj.browse(sale_id).write(sale_vals)
        return super(so_tracking, self).write(vals)

    def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification', subtype=None, parent_id=False, attachments=None, context=None, \
            content_subtype='html', **kwargs):
        """ To post Tracking messages in related Sales Order
        """
        message_obj = self.pool.get('mail.message')
        sale_obj = self.pool.get('sale.order')
        values ={}
        if context is None:
            context = {}
        res = super(so_tracking, self).message_post(cr, uid, thread_id, body=body, subject=subject, type=type, subtype=subtype, parent_id=parent_id, \
            attachments=attachments, context=context, content_subtype=content_subtype, **kwargs)
        if res:
            data = message_obj.browse(cr, uid, res, context=context)
            so_track_data = self.browse(cr, uid, thread_id)
            values.update({
                'model': 'sale.order',
                'res_id': so_track_data.sale_order_id.id,
                'body' : data.body,
                'parent_id': False,
            })
            if values:
                message_obj.create(cr, uid, values, context=context )
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
