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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_aged_trial_balance_inherited(osv.osv_memory):

    _inherit = 'account.aged.trial.balance'
    _name = 'account.aged.trial.balance.inherited'
    _description = 'Account Aged Trial balance Report inherited'

    _columns = {
        'all_partner' : fields.boolean("All Partner", default=False),
        'references' : fields.boolean("With References"),
        'journal_ids': fields.many2many('account.journal', 'account_aged_trial_balance_inh_journal_rel', 'account_id', 'journal_id', 'Journals', required=True),
        'first_period_length':fields.integer('First Period Length (Days)', required=True),
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        cur_rec = self.read(cr, uid, ids, ['period_length','date_from','all_partner','references','first_period_length','direction_selection'], context=context)[0]
        res={}
        result = super(account_aged_trial_balance_inherited, self)._print_report(cr, uid, ids, data, context=context)
        result.update({
            'report_file': u'ob_partner_ageing.report_agedpartnerbalance_inherited',
            'report_name': u'partner.report_agedpartnerbalance'

        })
        result.get("data",{}).get("form",{}).update({
            'partner_ids': context.get('active_ids',[]),
            'partner_filtered': True,
            'all_partner': cur_rec.get('all_partner',False),
            'references': cur_rec.get('references',False),
            'first_period_length':cur_rec.get('first_period_length',False),
            'direction_selection':cur_rec.get('direction_selection',False),
            'period_length':cur_rec.get('period_length',False),
        })
        first_period_length_data = cur_rec['first_period_length']
        if cur_rec['first_period_length'] <=0:
            raise osv.except_osv(_('User Error!'), _('You must set a First period length greater than 0.'))
        
        if cur_rec['direction_selection'] == 'past':
            start = datetime.strptime(cur_rec['date_from'], "%Y-%m-%d")
            for i in range(5)[::-1]:
                stop = start - relativedelta(days=cur_rec['first_period_length'])
                res[str(i)] = {
                    'name': (i==4 and (str(0) + '-' + str(cur_rec['first_period_length']))) or (i!=0 and (str((4-(i+1)) * cur_rec['period_length'] + cur_rec['first_period_length']) + '-' + str((4-i) * cur_rec['period_length'] + cur_rec['first_period_length']))) or ('+' + str(3 * cur_rec['period_length'] + cur_rec['first_period_length'])),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop - relativedelta(days=1)
        else:
            start = datetime.strptime(cur_rec['date_from'], "%Y-%m-%d")
            for i in range(5)[::-1]:
                stop = start - relativedelta(days=cur_rec['first_period_length'])
                res[str(i)] = {
                    'name': (i==4 and (str(0) + '-' + str(cur_rec['first_period_length']))) or (i!=0 and (str((4-(i+1)) * cur_rec['period_length'] + cur_rec['first_period_length']) + '-' + str((4-i) * cur_rec['period_length'] + cur_rec['first_period_length']))) or ('+' + str(3 * cur_rec['period_length'] + cur_rec['first_period_length'])),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop - relativedelta(days=1)
        result.get("data",{}).get("form",{}).update(res)
        return result
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
