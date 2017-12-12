# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class CommissionRule(models.Model):

    _name = "commission.rule"

    name = fields.Char('Name', size=64, required=True)
    type = fields.Selection((('percent_fixed', 'Fixed Commission Rate'),
                                  ('percent_product_category', 'Product Category Commission Rate'),
                                  ('percent_product', 'Product Commission Rate'),
                                  ('percent_amount', 'Commission Rate By Amount'),
                                  ('percent_accumulate', 'Commission Rate By Monthly Accumulated Amount')),
                                 'Type', required=True)
    fix_percent = fields.Float('Fix Percentage')
    rule_rates = fields.One2many('commission.rule.rate', 'commission_rule_id', 'Rates')
    rule_conditions = fields.One2many('commission.rule.condition', 'commission_rule_id', 'Conditions')
    active = fields.Boolean('Active', default=1)


class CommissionRuleRate(models.Model):

    _name = "commission.rule.rate"
    _order = 'id'

    commission_rule_id = fields.Many2one('commission.rule', 'Commission Rule')
    amount_over = fields.Float('Amount Over', required=True)
    amount_upto = fields.Float('Amount Up-To', required=True)
    percent_commission = fields.Float('Commission (%)', required=True)


class CommissionRuleCondition(models.Model):

    _name = "commission.rule.condition"
    _order = 'sequence'

    sequence = fields.Integer('Sequence', required=True)
    commission_rule_id = fields.Many2one('commission.rule', 'Commission Rule')
    sale_margin_over = fields.Float('Margin Over (%)', required=True)
    sale_margin_upto = fields.Float('Margin Up-To (%)', required=True)
    commission_coeff = fields.Float('Commission Coeff', required=True, default=1.0)
    accumulate_coeff = fields.Float('Accumulate Coeff', required=True, default=1.0)


class SaleTeam(models.Model):

    _name = "sale.team"

    name = fields.Char('Name', size=64, required=True)
    commission_rule_id = fields.Many2one('commission.rule', 'Commission Rule', required=True)
    users = fields.Many2many('res.users', 'sale_team_users_rel', 'tid', 'uid', 'Users')
    implied_ids = fields.Many2many('sale.team', 'sale_team_implied_rel', 'tid', 'hid', string='Inherits', help='Users of this group automatically inherit those groups')
    skip_invoice = fields.Boolean('Without validate Sale Invoice', help='Allow paying commission without validate invoice. This is the case for trainee')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the team must be unique !')
    ]


class CommissionWorksheet(models.Model):

    _name = 'commission.worksheet'

    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _get_period_v7(self, cr, uid, context=None):
        if context is None:
            context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        ctx = dict(context, account_period_prefer_normal=True)
        periods = self.pool.get('account.period').find(cr, uid, context=ctx)
        return periods and periods[0] or False

    @api.multi
    def _get_period(self):
        a = self.pool['commission.worksheet']._get_period_v7(self._cr, self._uid, self._context)
        return a

    name = fields.Char('Name', size=64, required=True, default='/')
    sale_team_id = fields.Many2one('sale.team', 'Team', required=True)
    period_id = fields.Many2one('account.period', 'Period', required=True, default=lambda self: self.env['commission.worksheet']._get_period())
    worksheet_lines = fields.One2many('commission.worksheet.line', 'commission_worksheet_id', 'Calculation Lines', ondelete='cascade')
    state = fields.Selection([('draft', 'Draft'),
                               ('confirmed', 'Confirmed')], 'Status', required=True, readonly=True, default='draft',
            help='* The \'Draft\' status is set when the work sheet in draft status. \
                \n* The \'Confirmed\' status is set when the work sheet is confirmed by related parties.')

    _sql_constraints = [
        ('sale_team_id', 'period_id', 'Duplicate Sale Team / Period')
    ]


    @api.model
    def create(self, vals):
        if vals.get('period_id', False) and vals.get('sale_team_id', False):
            rec = self.search([('period_id', '=', vals.get('period_id')), ('sale_team_id', '=', vals.get('sale_team_id'))])
            if rec:
                raise Warning('You can not create duplicate Commission WorkSheet')
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('commission.worksheet') or '/'
        return super(CommissionWorksheet, self).create(vals)

    @api.v8
    def _get_match_rule_condition(self, rule, order):
        rule_condition_obj = self.env['commission.rule.condition']
        percent_margin = order.amount_untaxed and (order.margin / order.amount_untaxed) * 100 or 0.0
        rule_condition_ids = rule_condition_obj.search([('commission_rule_id', '=', rule.id),
                                            ('sale_margin_over', '<', percent_margin),
                                            ('sale_margin_upto', '>=', percent_margin)])
        if not rule_condition_ids:
            return False
        elif len(rule_condition_ids) > 1:
            raise Warning(('More than 1 Rule Condition match %s! There seems to be problem with Rule %s.') % (order.name, rule.name))
        elif len(rule_condition_ids) == 1:
            return rule_condition_ids[0]


    @api.one
    def _calculate_commission(self, rule, worksheet, orders):
        if rule.type == 'percent_fixed':
            self._calculate_percent_fixed(rule, worksheet, orders)
        if rule.type == 'percent_product_category':
            self._calculate_percent_product_category(rule, worksheet, orders)
        if rule.type == 'percent_product':
            self._calculate_percent_product(rule, worksheet, orders)
        if rule.type == 'percent_amount':
            self._calculate_percent_amount(rule, worksheet, orders)
        if rule.type == 'percent_accumulate':
            self._calculate_percent_accumulate(rule, worksheet, orders)
        return True

    @api.v8
    def _prepare_worksheet_line(self, worksheet, order, accumulated_amt, commission_amt):
        res = {
            'commission_worksheet_id': worksheet.id,
            'order_id': order.id,
            'order_date': order.date_order,
            'order_amt': order.amount_untaxed,
            'margin': order.margin,
            'percent_margin': order.amount_untaxed and (order.margin / order.amount_untaxed) * 100 or 0.0,
            'accumulated_amt': accumulated_amt,
            'commission_amt': commission_amt,
        }
        return res

    @api.one
    def _calculate_percent_fixed(self, rule, worksheet, orders):
        commission_rate = rule.fix_percent / 100
        accumulated_amt = 0.0
        worksheet_line_obj = self.env['commission.worksheet.line']
        for order in orders:
            accumulated_amt += order.amount_untaxed
            # For each order, find its match rule line
            commission_amt = 0.0
            if commission_rate:
                commission_amt = order.amount_untaxed * commission_rate
            res = self._prepare_worksheet_line(worksheet, order, accumulated_amt, commission_amt)
            worksheet_line_obj.create(res)
        return True

    @api.one
    def _calculate_percent_product_category(self, rule, worksheet, orders):
        commission_rate = 0.0
        accumulated_amt = 0.0
        worksheet_line_obj = self.env['commission.worksheet.line']
        for order in orders:
            accumulated_amt += order.amount_untaxed
            # For each product line
            commission_amt = 0.0
            for line in order.order_line:
                percent_commission = line.product_id.categ_id.percent_commission
                commission_rate = percent_commission and percent_commission / 100 or 0.0
                if commission_rate:
                    commission_amt += line.price_subtotal * commission_rate
            res = self._prepare_worksheet_line(worksheet, order, accumulated_amt, commission_amt)
            worksheet_line_obj.create(res)
        return True

    @api.one
    def _calculate_percent_product(self, rule, worksheet, orders):
        commission_rate = 0.0
        accumulated_amt = 0.0
        worksheet_line_obj = self.env['commission.worksheet.line']
        for order in orders:
            accumulated_amt += order.amount_untaxed
            # For each product line
            commission_amt = 0.0
            for line in order.order_line:
                percent_commission = line.product_id.percent_commission
                commission_rate = percent_commission and percent_commission / 100 or 0.0
                if commission_rate:
                    commission_amt += line.price_subtotal * commission_rate
            res = self._prepare_worksheet_line(worksheet, order, accumulated_amt, commission_amt)
            worksheet_line_obj.create(res)
        return True

    @api.one
    def _calculate_percent_amount(self, rule, worksheet, orders):
        worksheet_line_obj = self.env['commission.worksheet.line']
        accumulated_amt = 0.0
        for order in orders:
            accumulated_amt += order.amount_untaxed
            # For each order, find its match rule line
            commission_amt = 0.0
            ranges = rule.rule_rates
            for range in ranges:
                commission_rate = range.percent_commission / 100
                if order.amount_untaxed <= range.amount_upto:
                    commission_amt = order.amount_untaxed * commission_rate
                    break
            res = self._prepare_worksheet_line(worksheet, order, accumulated_amt, commission_amt)
            worksheet_line_obj.create(res)
        return True

    @api.one
    def _calculate_percent_accumulate(self, rule, worksheet, orders):
        rule_condition_obj = self.env['commission.rule.condition']
        worksheet_line_obj = self.env['commission.worksheet.line']
        accumulated_amt = 0.0
        for order in orders:
            # For each order, find its match rule line
            amount_to_accumulate = 0.0
            commission_amt = 0.0
            rule_condition_id = self._get_match_rule_condition(rule, order)
            if rule_condition_id:
                rule_condition = rule_condition_obj.browse(rule_condition_id.id)
                amount_to_accumulate = order.amount_untaxed * rule_condition.accumulate_coeff
                accumulated_amt += order.amount_untaxed
                amount_from = accumulated_amt - amount_to_accumulate
                ranges = rule.rule_rates
                for range in ranges:
                    commission_rate = range.percent_commission / 100
                    # Case 1: In Range, get commission and quit.
                    if amount_from <= range.amount_upto and accumulated_amt <= range.amount_upto:
                        commission_amt = amount_to_accumulate * commission_rate
                        break
                    # Case 2: Over Range, only get commission for this range first and postpone to next range.
                    elif amount_from <= range.amount_upto and accumulated_amt > range.amount_upto:
                        commission_amt += (range.amount_upto - amount_from) * commission_rate
                        amount_from = range.amount_upto
            res = self._prepare_worksheet_line(worksheet, order, accumulated_amt, commission_amt)
            worksheet_line_obj.create(res)
        return True

    @api.one
    def action_confirm(self):
        self.state = 'confirmed'

    @api.one
    def action_calculate(self):
        period_obj = self.env['account.period']
        worksheet_line_obj = self.env['commission.worksheet.line']
        order_obj = self.env['sale.order']

        # For each work sheet, reset the calculation
        for worksheet in self:
            sale_team_id = worksheet.sale_team_id.id
            period_id = worksheet.period_id.id
            if not sale_team_id or not period_id:
                continue
            rule = worksheet.sale_team_id.commission_rule_id
            date_start = period_obj.browse(period_id).date_start
            date_stop = period_obj.browse(period_id).date_stop
            # Delete old lines
            line_ids = worksheet_line_obj.search([('commission_worksheet_id', '=', worksheet.id)])
            if line_ids:
                line_ids.unlink()
            # Search for matched Completed Sales Order for this work sheet
            query = """ select o.id from sale_order o \
                                join sale_order_team t on o.id = t.sale_id \
                                where o.state in ('progress','manual','done') \
                                and date_order >= %s and date_order <= %s \
                                and t.sale_team_id = %s order by o.id
                    """
            self._cr.execute(query, (date_start, date_stop, sale_team_id))
            order_ids = map(lambda x: x[0], self._cr.fetchall())
            orders = order_obj.browse(order_ids)
            self._calculate_commission(rule, worksheet, orders)
        return True


class CommissionWorksheetLine(models.Model):

    _name = "commission.worksheet.line"
    _order = 'id'

    commission_worksheet_id = fields.Many2one('commission.worksheet', 'Commission Worksheet')
    order_id = fields.Many2one('sale.order', 'Order Number')
    order_date = fields.Date('Order Date')
    order_amt = fields.Float('Order Amount', readonly=True)
    margin = fields.Float('Margin', readonly=True)
    percent_margin = fields.Float('% Margin', readonly=True)
    accumulated_amt = fields.Float('Accumulated Amount', readonly=True)
    commission_amt = fields.Float('Commission Amount')

    # @api.multi
    # def unlink(self):
    #     print "uuuuuuuuuuuuuuuuuu---->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    #     line_ids = self.search([('id', 'in', self.ids)])
    #     if line_ids and len(line_ids) > 0:
    #         wlines = self.browse(line_ids)
    #         order_ids = [wline.order_id.name for wline in wlines]
    #         raise Warning("You can't delete this Commission Worksheet, because commission has been issued for Sales Order No. %s" % (",".join(order_ids)))
    #     else:
    #         return super(CommissionWorksheetLine, self).unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
