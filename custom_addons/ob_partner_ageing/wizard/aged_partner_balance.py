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
        'all_partner' : fields.boolean("All Partner"),
        # 'journal_ids': fields.many2many('account.journal','journal_account_age_inh_rel', 'jr_id', 'aa_id', string='Journals', required=True),
        'journal_ids': fields.many2many('account.journal', 'account_aged_trial_balance_inh_journal_rel', 'account_id', 'journal_id', 'Journals', required=True),
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        cur_rec = self.read(cr, uid, ids, ['all_partner'], context=context)[0]
        result = super(account_aged_trial_balance_inherited, self)._print_report(cr, uid, ids, data, context=context)
        # if 'all_partner' in cur_rec and cur_rec.get('all_partner',False):
        #     return result
        result.update({
            'report_file': u'ob_partner_ageing.report_agedpartnerbalance_inherited',
            'report_name': u'partner.report_agedpartnerbalance'
        })
        result.get("data",{}).get("form",{}).update({
            'partner_ids': context.get('active_ids',[]),
            'partner_filtered': True,
            'all_partner': cur_rec.get('all_partner',False)
        })
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

