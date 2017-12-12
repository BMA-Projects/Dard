from openerp import models, fields, api, _
from openerp.addons.account.report.account_aged_partner_balance import aged_trial_report

class aged_trial_report_inherit(aged_trial_report):

    def __init__(self, cr, uid, name, context):
        super(aged_trial_report_inherit, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_ref':self._get_ref,
        })

    def _get_ref(self, form):
        if form['references'] == True:
            return True
        else:
            return False

    def _get_lines(self, form):
        res = []
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']
        self.cr.execute('SELECT DISTINCT res_partner.id AS id,\
            l.id AS aml_id,\
            l.currency_id AS c_id, \
            res_partner.name AS name, \
            am.name AS doc_number,\
            l.date_maturity AS due_date,\
            am.ref AS ref\
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
        self.cr.execute('SELECT am.name, SUM(l.debit-l.credit), SUM(l.amount_currency), l.currency_id AS c_id \
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
            GROUP BY am.name, l.currency_id ', (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids), self.date_from, self.date_from,))
    
        t = self.cr.fetchall()
        currency_obj = self.pool.get('res.currency')
        for i in t:
            if not i[3]:
                totals[i[0]] = i[1]
            if i[3]:
                base_currency = currency_obj.browse(self.cr, self.uid, i[3]).base
                if base_currency:
                    totals[i[0]] = i[1]
                else:
                    totals[i[0]] = i[2]
        
        # This dictionary will store the future or past of all partners
        future_past = {}
        if self.direction_selection == 'future':
            self.cr.execute('SELECT am.name, SUM(l.debit-l.credit), SUM(l.amount_currency), \
                l.currency_id AS c_id \
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
                GROUP BY am.name, l.currency_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids),self.date_from, self.date_from,))
            
            t = self.cr.fetchall()
            currency_obj = self.pool.get('res.currency')
            for i in t:
                if not i[3]:
                    future_past[i[0]] = i[1]
                if i[3]:
                    base_currency = currency_obj.browse(self.cr, self.uid, i[3]).base
                    if base_currency:
                        future_past[i[0]] = i[1]
                    else:
                        future_past[i[0]] = i[2]
        elif self.direction_selection == 'past': # Using elif so people could extend without this breaking

            self.cr.execute('SELECT am.name, SUM(l.debit-l.credit), SUM(l.amount_currency), \
                l.currency_id AS c_id \
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
                    GROUP BY am.name, l.currency_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids), self.date_from, self.date_from,))
            
            t = self.cr.fetchall()
            currency_obj = self.pool.get('res.currency')
            for i in t:
                if not i[3]:
                    future_past[i[0]] = i[1]
                if i[3]:
                    base_currency = currency_obj.browse(self.cr, self.uid, i[3]).base
                    if base_currency:
                        future_past[i[0]] = i[1]
                    else:
                        future_past[i[0]] = i[2]

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
            
            self.cr.execute('''SELECT am.name, SUM(l.debit-l.credit), l.reconcile_partial_id, SUM(l.amount_currency), l.currency_id AS c_id
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
                GROUP BY am.name, l.reconcile_partial_id, l.currency_id''', args_list)

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
                        currency_obj = self.pool.get('res.currency')
                        # partial reconcilation
                        limit_date = 'COALESCE(l.date_maturity,l.date) %s %%s' % ('<=' if self.direction_selection == 'past' else '>=',)
                        self.cr.execute('''SELECT SUM(l.debit-l.credit), SUM(l.amount_currency), l.currency_id AS c_id
                           FROM account_move_line AS l, account_move AS am
                           WHERE l.move_id = am.id AND am.state in %s
                           AND l.reconcile_partial_id = %s
                           AND ''' + limit_date + '''GROUP BY l.currency_id''', (tuple(move_state), partner_info[2], self.date_from))
                        unreconciled_amount = self.cr.fetchall()
                        if not unreconciled_amount[0][2]:
                            partners_amount[partner_info[0]] += unreconciled_amount[0][0]
                        else:
                            base_currency = currency_obj.browse(self.cr, self.uid, unreconciled_amount[0][2]).base
                            if base_currency:
                                partners_amount[partner_info[0]] += unreconciled_amount[0][0]
                            else:
                                partners_amount[partner_info[0]] += unreconciled_amount[0][1]
                else:
                    currency_obj = self.pool.get('res.currency')
                    if not partner_info[4]:
                        partners_amount[partner_info[0]] += partner_info[1]
                    else:
                        base_currency = currency_obj.browse(self.cr, self.uid, partner_info[4]).base
                        if base_currency:
                            partners_amount[partner_info[0]] += partner_info[1]
                        else:
                            partners_amount[partner_info[0]] += partner_info[3]
            history.append(partners_amount)

        for partner in partners:
            self.cr.execute('SELECT l.id, i.id ' \
                'FROM account_move_line l, account_invoice i ' \
                'WHERE l.move_id = i.move_id ' \
                'AND l.id IN %s',
                (tuple([partner['aml_id']]),))
            inv_res = self.cr.fetchall()
            values = {}
            ref1= ''

            if inv_res:
                invoice_obj = self.pool.get('account.invoice').browse(self.cr, self.uid, inv_res[0][1])
                if invoice_obj.origin:
                    so_obj = self.pool.get('sale.order')
                    po_obj = self.pool.get('purchase.order')
                    stock_obj = self.pool.get('stock.picking')
                    so_ids = so_obj.search(self.cr, self.uid, [('name', '=', invoice_obj.origin)])
                    purchase_ids = po_obj.search(self.cr, self.uid, [('name', '=', invoice_obj.origin)])

                    if ref1 == '':
                        if so_ids:
                            sale_rec = so_obj.browse(self.cr, self.uid, so_ids)
                            if sale_rec:
                                ref1 = sale_rec[0].client_po_ref

                    if ref1 == '':
                        if purchase_ids:
                            purchase_rec = po_obj.browse(self.cr, self.uid, purchase_ids)
                            if purchase_rec:
                                ref1 = purchase_rec[0].partner_ref

                    if ref1 == '':
                        picking_ids = stock_obj.search(self.cr, self.uid, [('name', '=', invoice_obj.origin)])
                        if picking_ids:
                            picking_rec = stock_obj.browse(self.cr, self.uid, picking_ids)
                            if picking_rec:
                                so_ids = so_obj.search(self.cr, self.uid, [('name', '=', picking_rec.origin)])
                                if so_ids:
                                    sale_rec = so_obj.browse(self.cr, self.uid, so_ids)
                                    if sale_rec:
                                        ref1 = sale_rec[0].client_po_ref

                    if ref1 == '':
                        picking_ids = stock_obj.search(self.cr, self.uid, [('name', '=', invoice_obj.origin)])
                        if picking_ids:
                            picking_rec = stock_obj.browse(self.cr, self.uid, picking_ids)
                            if picking_rec:
                                po_ids = po_obj.search(self.cr, self.uid, [('name', '=', picking_rec.origin)])
                                if po_ids:
                                    po_rec = po_obj.browse(self.cr, self.uid, po_ids)
                                    if po_rec:
                                        ref1 = po_rec[0].partner_ref

            values['ref1'] = ref1

            self.cr.execute('SELECT l.number FROM account_invoice l WHERE l.number = %s', (tuple([partner['doc_number']]),))
            doc_res = self.cr.fetchall()

            if len(doc_res):
                currency_obj = self.pool.get('res.currency').browse(self.cr, self.uid, partner['c_id'])
                currency_base_ids = self.pool.get('res.currency').search(self.cr, self.uid, ([('base','=',True)]))
                if not currency_obj.name:
                    if currency_base_ids:
                        currency_base_obj = self.pool.get('res.currency').browse(self.cr, self.uid, currency_base_ids[0])
                        values["currency_name"] = currency_base_obj.name
                    else:
                        values["currency_name"] = currency_obj.name
                else:
                    values["currency_name"] = currency_obj.name
                values.update({'doc_number':partner.get('doc_number'), 'due_date':partner.get('due_date'), 'ref':partner.get('ref')})

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
                sum_all = values['0']+values['1']+values['2']+values['3']+values['4']+values['direction']
                values['total'] = [sum_all]

                ## Add for total
                self.total_account[(i+1)] += sum_all
                values['name'] = partner['name']
                res.append(values)

        total = 0.0
        totals = {}
        for r in res:
            ttl = r['0'] + r['1'] + r['2'] + r['3'] + r['4'] + r['direction']
            r['total'] = ttl
            total += float(r['total'] or 0.0)
            for i in range(5)+['direction']:
                totals.setdefault(str(i), 0.0)
                totals[str(i)] += float(r[str(i)] or 0.0)
        return res


class report_agedpartnerbalance(models.AbstractModel):
    _name = 'report.partner.report_agedpartnerbalance'
    _inherit = 'report.abstract_report'
    _template = 'ob_partner_ageing_dard.report_agedpartnerbalance'
    _wrapped_report_class = aged_trial_report_inherit

