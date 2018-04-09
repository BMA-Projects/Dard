from openerp.osv import osv, fields
import re
from openerp import tools, api, SUPERUSER_ID


class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def _credit_debit_get_for_report(self, cr, uid, ids, field_names, arg, from_date ,context=None):
        ctx = context.copy()
        ctx['all_fiscalyear'] = True
        query = self.pool.get('account.move.line')._query_get(cr, uid, context=ctx)
        cr.execute("""SELECT l.partner_id, a.type, SUM(l.debit-l.credit)
                      FROM account_move_line l
                      LEFT JOIN account_account a ON (l.account_id=a.id)
                      WHERE a.type IN ('receivable','payable')
                      AND l.partner_id IN %s
                      AND l.date < %s
                      AND l.reconcile_id IS NULL
                      AND """ + query + """
                      GROUP BY l.partner_id, a.type
                      """,
                   (tuple(ids), from_date, ))
        maps = {'receivable':'credit', 'payable':'debit' }
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0)
        for pid,type,val in cr.fetchall():
            if val is None: val=0
            res[pid][maps[type]] = (type=='receivable') and val or -val
        return res
