from openerp import models, fields, api, _
from openerp.addons.account.report.account_aged_partner_balance import aged_trial_report

class aged_trial_report_inherit(aged_trial_report):

    def _get_lines(self, form):
        res = []
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']
        self.cr.execute('SELECT DISTINCT res_partner.id AS id,\
                    res_partner.name AS name, \
                    am.name AS doc_number,\
                    l.date_maturity AS due_date\
                FROM res_partner,account_move_line AS l, account_account, account_move am\
                WHERE (l.account_id=account_account.id) \
                    AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND account_account.active\
                    AND ((reconcile_id IS NULL)\
                       OR (reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                    AND (l.partner_id=res_partner.id)\
                    AND (l.date <= %s)\
                    AND ' + self.query + ' \
                ORDER BY res_partner.name', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, self.date_from,))
        partners = self.cr.dictfetchall()
        ## mise a 0 du total
        for i in range(7):
            self.total_account.append(0)
        # Build a string like (1,2,3) for easy use in SQL query
        selected_partner_ids = form.get("partner_ids",[])
        if not form['all_partner']:
            partners = [x for x in partners if x['id'] in selected_partner_ids]
        partner_ids = [x['id'] for x in partners]
        if not partner_ids:
            return []
        # This dictionary will store the debit-credit for all partners, using partner_id as key.

        totals = {}
        self.cr.execute('SELECT am.name, SUM(l.debit-l.credit) \
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id = account_account.id) AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND (l.partner_id IN %s)\
                    AND ((l.reconcile_id IS NULL)\
                    OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                    AND ' + self.query + '\
                    AND account_account.active\
                    AND (l.date <= %s)\
                    GROUP BY am.name ', (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids), self.date_from, self.date_from,))
        t = self.cr.fetchall()
        for i in t:
            totals[i[0]] = i[1]
        # This dictionary will store the future or past of all partners
        future_past = {}
        if self.direction_selection == 'future':
            self.cr.execute('SELECT am.name, SUM(l.debit-l.credit) \
                        FROM account_move_line AS l, account_account, account_move am \
                        WHERE (l.account_id=account_account.id) AND (l.move_id=am.id) \
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity, l.date) < %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND '+ self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s)\
                        GROUP BY am.name', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids),self.date_from, self.date_from,))
            t = self.cr.fetchall()
            for i in t:
                future_past[i[0]] = i[1]
        elif self.direction_selection == 'past': # Using elif so people could extend without this breaking
            self.cr.execute('SELECT am.name, SUM(l.debit-l.credit) \
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id=account_account.id) AND (l.move_id=am.id)\
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity,l.date) > %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND '+ self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s)\
                        GROUP BY am.name', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids), self.date_from, self.date_from,))
            t = self.cr.fetchall()
            for i in t:
                future_past[i[0]] = i[1]
        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids),self.date_from,)
            dates_query = '(COALESCE(l.date_maturity,l.date)'
            if form[str(i)]['start'] and form[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (form[str(i)]['start'], form[str(i)]['stop'])
            elif form[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (form[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (form[str(i)]['stop'],)
            args_list += (self.date_from,)
            self.cr.execute('''SELECT am.name, SUM(l.debit-l.credit), l.reconcile_partial_id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                        AND (am.state IN %s)
                        AND (account_account.type IN %s)
                        AND (l.partner_id IN %s)
                        AND ((l.reconcile_id IS NULL)
                          OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))
                        AND ''' + self.query + '''
                        AND account_account.active
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    GROUP BY am.name, l.reconcile_partial_id''', args_list)
            partners_partial = self.cr.fetchall()
            partners_amount = dict((i[0],0) for i in partners_partial)
            for partner_info in partners_partial:
                if partner_info[2]:
                    # in case of partial reconciliation, we want to keep the left amount in the oldest period
                    self.cr.execute('''SELECT MIN(COALESCE(date_maturity,date)) FROM account_move_line WHERE reconcile_partial_id = %s''', (partner_info[2],))
                    date = self.cr.fetchall()
                    partial = False
                    if 'BETWEEN' in dates_query:
                        partial = date and args_list[-3] <= date[0][0] <= args_list[-2]
                    elif '>=' in dates_query:
                        partial = date and date[0][0] >= form[str(i)]['start']
                    else:
                        partial = date and date[0][0] <= form[str(i)]['stop']
                    if partial:
                        # partial reconcilation
                        limit_date = 'COALESCE(l.date_maturity,l.date) %s %%s' % '<=' if self.direction_selection == 'past' else '>='
                        self.cr.execute('''SELECT SUM(l.debit-l.credit)
                                           FROM account_move_line AS l, account_move AS am
                                           WHERE l.move_id = am.id AND am.state in %s
                                           AND l.reconcile_partial_id = %s
                                           AND ''' + limit_date, (tuple(move_state), partner_info[2], self.date_from))
                        unreconciled_amount = self.cr.fetchall()
                        partners_amount[partner_info[0]] += unreconciled_amount[0][0]
                else:
                    partners_amount[partner_info[0]] += partner_info[1]
            history.append(partners_amount)

        for partner in partners:

            values = {}
            values.update({'doc_number':partner.get('doc_number'), 'due_date':partner.get('due_date')})
            ## If choise selection is in the future
            if self.direction_selection == 'future':
                # Query here is replaced by one query which gets the all the partners their 'before' value
                before = False
                if future_past.has_key(partner['doc_number']):
                    before = [ future_past[partner['doc_number']] ]
                self.total_account[6] = self.total_account[6] + (before and before[0] or 0.0)
                values['direction'] = before and before[0] or 0.0
            elif self.direction_selection == 'past': # Changed this so people could in the future create new direction_selections
                # Query here is replaced by one query which gets the all the partners their 'after' value
                after = False
                if future_past.has_key(partner['doc_number']): # Making sure this partner actually was found by the query
                    after = [ future_past[partner['doc_number']] ]

                self.total_account[6] = self.total_account[6] + (after and after[0] or 0.0)
                values['direction'] = after and after[0] or 0.0
            for i in range(5):
                during = False
                if history[i].has_key(partner['doc_number']):
                    during = [ history[i][partner['doc_number']] ]
                # Ajout du compteur
                self.total_account[(i)] = self.total_account[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
            total = False
            if totals.has_key( partner['doc_number'] ):
                total = [ totals[partner['doc_number']] ]
            values['total'] = total and total[0] or 0.0
            ## Add for total
            self.total_account[(i+1)] = self.total_account[(i+1)] + (total and total[0] or 0.0)
            values['name'] = partner['name']
            res.append(values)

        total = 0.0
        totals = {}
        for r in res:
            total += float(r['total'] or 0.0)
            for i in range(5)+['direction']:
                totals.setdefault(str(i), 0.0)
                totals[str(i)] += float(r[str(i)] or 0.0)
        return res


class report_agedpartnerbalance(models.AbstractModel):
    _name = 'report.partner.report_agedpartnerbalance'
    _inherit = 'report.abstract_report'
    _template = 'ob_partner_ageing.report_agedpartnerbalance'
    _wrapped_report_class = aged_trial_report_inherit

