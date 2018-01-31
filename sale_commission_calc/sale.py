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


class SaleOrderTeam(models.Model):

    _name = "sale.order.team"

    @api.onchange('sale_team_id')
    def onchange_sale_team_id(self):
        if self.sale_team_id:
            team = self.env['sale.team'].browse([self.sale_team_id.id])
            self.commission_rule_id = team.commission_rule_id.id

    sale_id = fields.Many2one('sale.order', 'Sale order', ondelete='cascade')
    sale_team_id = fields.Many2one('sale.team', 'Team', required=True)
    commission_rule_id = fields.Many2one('commission.rule', 'Applied Commission', required=True, readonly=True)


class SaleOrder(models.Model):

    _inherit = "sale.order"

    sale_team_ids = fields.One2many('sale.order.team', 'sale_id', 'Teams', states={'draft': [('readonly', False)]})

    def _get_sale_team_ids(self, cr, uid, ids, user_id):
        sale_team_ids = []
        if user_id:
            sale_order_team = self.pool.get('sale.order.team')
            if ids:
                sale_order_team.unlink(cr, uid, sale_order_team.search(cr, uid, [('sale_id', 'in', ids)]))
            cr.execute("""select a.tid team_id, b.tid as inherit_id  from sale_team_users_rel a
                            left outer join sale_team_implied_rel b on b.hid = a.tid
                            where uid = %s
                            """,
                            (user_id,))
            team_ids = []

            for team_id, inherit_id in cr.fetchall():
                if team_id not in team_ids:
                    team_ids.append(team_id)
                if inherit_id:
                    if inherit_id not in team_ids:
                        team_ids.append(inherit_id)

                    def _get_all_inherited_team(cr, uid, team_ids, inherit_id):
                        cr.execute("""select tid as interit_id from sale_team_implied_rel
                                    where hid = %s and tid != hid
                                    """,
                                    (inherit_id,))
                        for team_id in cr.fetchall():
                            if team_id[0] not in team_ids:
                                team_ids.append(team_id[0])
                            team_ids = _get_all_inherited_team(cr, uid, team_ids, team_id[0])
                        return team_ids

                    team_ids = _get_all_inherited_team(cr, uid, team_ids, inherit_id)

            teams = self.pool.get('sale.team').browse(cr, uid, team_ids)
            team_recs = []
            for team in teams:
                team_recs.append({'sale_team_id': team.id, 'commission_rule_id': team.commission_rule_id.id})
        return team_recs

    # @api.v8
    # def _get_sale_team_ids(self, t_ids, user_id):
    #     sale_team_ids = []
    #     print "\n\n\n\nself", self, self.id
    #     if user_id:
    #         sale_order_team = self.env['sale.order.team']
    #         # if self.id:
    #             # sale_order_team.unlink(sale_order_team.search([('sale_id', 'in', ids)]))
    #         # cr.execute("""select a.tid team_id, b.tid as inherit_id  from sale_team_users_rel a
    #         #                 left outer join sale_team_implied_rel b on b.hid = a.tid
    #         #                 where uid = %s
    #         #                 """,
    #         #                 (user_id,))
    #         team_ids = []
    #
    #         query = """ select a.tid team_id, b.tid as inherit_id  from sale_team_users_rel a
    #                         left outer join sale_team_implied_rel b on b.hid = a.tid
    #                         where uid = %s
    #                 """
    #         self._cr.execute(query, (user_id),)
    #
    #
    #         for team_id, inherit_id in self._cr.fetchall():
    #             if team_id not in team_ids:
    #                 team_ids.append(team_id)
    #             if inherit_id:
    #                 if inherit_id not in team_ids:
    #                     team_ids.append(inherit_id)
    #
    #                 @api.v8
    #                 def _get_all_inherited_team(self, team_ids, inherit_id):
    #
    #                     query2 = """ select tid as interit_id from sale_team_implied_rel
    #                                 where hid = %s and tid != hid
    #                             """
    #
    #                     self._cr.execute(query2, (inherit_id),)
    #
    #                     # cr.execute("""select tid as interit_id from sale_team_implied_rel
    #                     #             where hid = %s and tid != hid
    #                     #             """,
    #                     #             (inherit_id,))
    #
    #                     for team_id in self._cr.fetchall():
    #                         if team_id[0] not in team_ids:
    #                             team_ids.append(team_id[0])
    #                         team_ids = _get_all_inherited_team(team_ids, team_id[0])
    #                     return team_ids
    #
    #                 team_ids = _get_all_inherited_team(team_ids, inherit_id)
    #
    #         teams = self.env['sale.team'].browse(team_ids)
    #         team_recs = []
    #         for team in teams:
    #             team_recs.append({'sale_team_id': team.id, 'commission_rule_id': team.commission_rule_id.id})
    #     return team_recs


    # @api.onchange('user_id')
    # def onchange_user_id(self):
    #     res = {'value': {'sale_team_ids': False}}
    #     if self.user_id:
    #         sale_team_ids = self._get_sale_team_ids(cr, uid, ids, user_id)
    #         res['value']['sale_team_ids'] = sale_team_ids
    #     return res

    # @api.v8
    # def create_sale_team(self, t_ids):
    #     sale_order_team = self.env['sale.order.team']
    #     sale_teams = []
    #     for sale_rec in self:
    #         print "\n\n\ntetttttteeeestsstsststsstst"
    #         sale_team_ids = self._get_sale_team_ids(t_ids, sale_rec.user_id.id)
    #         for sale_value in sale_team_ids:
    #             sale_value.update({'sale_id': sale_rec.id})
    #             sale_team_id = sale_order_team.create(sale_value)
    #             sale_teams.append(sale_team_id)
    #     return sale_teams


    # @api.model
    # def create(self, vals,):
    #     new_id = super(sale_order, self).create(vals)
    #     self.create_sale_team(self._cr, self._uid, [new_id], self._context)
    #     return new_id

    def onchange_user_id(self, cr, uid, ids, user_id):
        res = {'value': {'sale_team_ids': False}}
        if user_id:
            sale_team_ids = self._get_sale_team_ids(cr, uid, ids, user_id)
            res['value']['sale_team_ids'] = sale_team_ids
        return res

    def create_sale_team(self, cr, uid, ids, context=None):
        sale_recs = self.browse(cr, uid, ids, context)
        sale_order_team = self.pool.get('sale.order.team')
        sale_teams = []
        for sale_rec in sale_recs:
            sale_team_ids = self._get_sale_team_ids(cr, uid, [sale_rec.id], sale_rec.user_id.id)
            for sale_value in sale_team_ids:
                sale_value.update({'sale_id': sale_rec.id})
                sale_team_id = sale_order_team.create(cr, uid, sale_value)
                sale_teams.append(sale_team_id)
        return sale_teams

    def create(self, cr, uid, vals, context=None):
        new_id = super(SaleOrder, self).create(cr, uid, vals, context=context)
        self.create_sale_team(cr, uid, [new_id], context)
        return new_id


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
