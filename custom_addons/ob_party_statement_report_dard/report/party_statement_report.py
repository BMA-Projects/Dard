# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

import base64
import StringIO
import xlsxwriter
from openerp import models, fields, api
import datetime
import time
from gdata.data import REQUIRED_ATENDEE
from gdata.sites.data import Column
from openerp.exceptions import ValidationError
from stripe.resource import Invoice
# from openerp.addons.ob_party_statement_report.party_statement_report import party_report

class party_statement_report(models.TransientModel):
    _inherit = 'party.statement.report'

    group_by_partner = fields.Selection([('customer', 'Customer'), ('supplier', 'Supplier')], required=True, default='customer')

    @api.multi
    def generate_report(self):
         check_data_available = []
         domain = [
                   ('state','in',['open']),
                   # ('date_invoice','>=',self.from_date),('date_invoice','<=',self.to_date)
                  ]
         voucher_domain = [('invoice_id.state','in',['open']),
                           ('state','in',['posted']),
                           ('date','>=',self.from_date),('date','<=',self.to_date)
                           ]

         self._onchage_date_chane()
         # apply domain for customer and supplier
         customers = self.customer_ids
         customer_ids = self.customer_ids.ids
         all_child_ids = {}
         exist_ids = self.customer_ids.ids
         if self.customer_ids:
             parent_customer = [customer for customer in self.customer_ids if customer.is_company]
             for customer in parent_customer:
                 for cust_id in customer.child_ids.ids:
                     customer_ids.append(cust_id)
                     all_child_ids.update({cust_id:customer.id})

         else:
             customers = self.env['res.partner'].search([('customer','=',True)])
             customer_ids = customers.ids
             exist_ids = customers.ids
             parent_customer = [customer for customer in customers if customer.is_company]
             for customer in parent_customer:
                 for cust_id in customer.child_ids.ids:
                     customer_ids.append(cust_id)
                     all_child_ids.update({cust_id:customer.id})

         self.company_id and domain.append(('company_id','=',self.company_id.id))
         self.company_id and voucher_domain.append(('company_id','=',self.company_id.id))
         if self.group_by_partner == 'customer':
             customers and domain.append(('partner_id','in',customer_ids))
             customers and voucher_domain.append(('partner_id','in',customer_ids))
         if self.group_by_partner == 'supplier':
             self.supplier_ids and domain.append(('partner_id','in',self.supplier_ids.ids))
             self.supplier_ids and voucher_domain.append(('partner_id','in',self.supplier_ids.ids))
         header_row = []
         payment_header = []

         # Create header list for pdf and xls reports
         if self.group_by_detail == 'detail':
             #table header data
            header_row = ['Reference','Tran. Date', 'Document Type', 'Description',
                           'Debit amount', 'Credit amount', 'amt', 'Balance', 'code', 'customer name', 'sales Person Name']
            payment_header = ['payment_no', 'payment_date', 'payment Type','ref','Debit amount', 'Credit amount','amt', 'Balance']

         account_invoice = self.env['account.invoice']
         account_voucher = self.env['account.voucher']

         head_caption = 'Party Statement Report'
         head_caption2 =  'From Date: '

         all_types = []
         if self.group_by_partner == 'customer':
             all_types = ['out_invoice', 'out_refund', 'sale']

         group_by_data = {}
         group_by_name = {}
         # Add new domains as per conditions
         for types in all_types:
             if types in ['out_invoice','in_invoice']:
                 if self.group_by_partner == 'customer':
                     if ('type','=','out_refund') in domain:
                         domain.remove(('type','=','out_refund'))
                     domain.append(('type','=','out_invoice'))

             if types in ['out_refund','in_refund']:
                 if self.group_by_partner == 'customer':
                     if ('type','=','out_invoice') in domain:
                         domain.remove(('type','=','out_invoice'))
                     domain.append(('type','=','out_refund'))
             if types in ['sale'] and self.group_by_partner == 'customer':
                 voucher_domain.append(('type', '=', 'sale'))
                 voucher_domain.append(('partner_id', '!=', False))
             if types in ['purchase'] and self.group_by_partner == 'supplier':
                 voucher_domain.append(('type', '=', 'purchase'))
                 voucher_domain.append(('partner_id', '!=', False))


             account_invoice_obj = False
             account_voucher_obj = False
             # fetch group by data from database
             if types in ['out_invoice','in_invoice', 'out_refund','in_refund']:
                 account_invoice_obj = account_invoice.sudo().search(domain)
                 if account_invoice_obj:
                     check_data_available.append(account_invoice_obj)
             # fetch group by data from database
             if types in ['sale', 'purchase']:
                 account_voucher_obj = account_voucher.sudo().search(voucher_domain)
                 if account_voucher_obj:
                    check_data_available.append(account_voucher_obj)

            # Fetch data using queries and create group wise.
             if account_invoice_obj:
                 if self.group_by_partner == 'customer':
                     self.sudo()._cr.execute("""select ai.partner_id,ai.id,ai.type
                                          from account_invoice as ai
                                          where ai.id in %s order by ai.date_invoice """,(tuple(account_invoice_obj.ids),))
                     group_name = {'group_by':'partner_id','group_name':"self.env['res.partner'].sudo().browse(group_data[0]).name"}
                     if self.group_by_detail == 'detail':
                         head_caption = "For Customer - Party Statement Detail Report"
                     else:
                         head_caption = "For Customer - Party Statement Summary Report"

                 row=4

             # Fetch data using queries and create group wise.
             if account_voucher_obj:
                if self.group_by_partner == 'customer':
                    self.sudo()._cr.execute("""select ai.partner_id,ai.id,ai.type
                                         from account_voucher as ai
                                         where ai.id in %s order by ai.date """,(tuple(account_voucher_obj.ids),))
                    group_name = {'group_by':'partner_id','group_name':"self.env['res.partner'].sudo().browse(group_data[0]).name"}
                    if self.group_by_detail == 'detail':
                        head_caption = "For Customer - Party Statement Detail Report"
                    else:
                        head_caption = "For Customer - Party Statement Summary Report"

             #prepare dict by group name
             if self.group_by_partner:
                 data = self._cr.dictfetchall()
                 if data:
                     for record in data:
                         if record[group_name['group_by']] in all_child_ids:
                             if group_by_data.has_key(all_child_ids[record[group_name['group_by']]]):
                                 group_by_data[all_child_ids[record[group_name['group_by']]]].append({record['type']:record['id']})
                             else:
                                 group_by_data.update({all_child_ids[record[group_name['group_by']]]:[{record['type']:record['id']}]})
    
                         if record[group_name['group_by']] in exist_ids:
                             if group_by_data.has_key(record[group_name['group_by']]):
                                 group_by_data[record[group_name['group_by']]].append({record['type']:record['id']})
                             else:
                                 group_by_data.update({record[group_name['group_by']]:[{record['type']:record['id']}]})

         if not self.sales_person:
             for group_data in group_by_data.iteritems():
                group_by_name.update({str(eval(group_name['group_name'])):(group_data[0],group_data[1])})
         group_by_sales = [{}]
         invoice_data = {'table_header':header_row, 'payment_header': payment_header ,'from_date':self.from_date,'to_date':self.to_date,'company_id':self.company_id and self.company_id.id ,'head_caption':head_caption, 'head_caption2': head_caption2, 'currunt_company': self.company_id.name, 'currunt_company_logo': self.company_id.logo }

         # Make XLS file formating and make header
         if not self._context.has_key('pdf_report'):
             output =  StringIO.StringIO()
             workbook = xlsxwriter.Workbook(output, {'in_memory': True})
             worksheet = workbook.add_worksheet()
             bold = workbook.add_format({'bold': True})
             bold.set_font_color('Blue')
             amount_format = workbook.add_format({'num_format': '0.00','align': 'right'})
             amount_bold_format = workbook.add_format({'num_format': '0.00','bold': True})
             amount_bold_format_right = workbook.add_format({'num_format': '0.00','bold': True,'align': 'right'})
             bold_format_right = workbook.add_format({'bold': True,'align': 'right'})
             header_bold = workbook.add_format({'bold': True})
             merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'left','valign': 'vcenter','fg_color': 'yellow' })
             merge_format_opening = workbook.add_format({'bold': 1,'align': 'right','valign': 'vcenter' })
             merge_format_salesperson = workbook.add_format({'bold': 1,'align': 'center','valign': 'vcenter','fg_color': 'yellow' })
             back_color = 'A1:K2'
             worksheet.merge_range(back_color, head_caption + '  ' + 'From Date: ' + datetime.datetime.strptime(self.from_date, '%Y-%m-%d').strftime('%m/%d/%Y')  + " To : " + datetime.datetime.strptime(self.to_date, '%Y-%m-%d').strftime('%m/%d/%Y') , merge_format)

         def get_number(number):
            if number:
                split_number = list(number.rpartition('/'))
                if len(split_number) == 3:
                    return split_number and split_number[2]
            return number

         # Function use for make a group wise dictionary and pass in reports (use in both qweb and xls)
         def write_invoice(invoice_browse_objs, row, group_name=False):
            total_credited_amount = 0
            total_debited_amount = 0
            total_amount = 0
            pdf_data = []
            cr_or_dr = ''
            opening_bal = 0
            list_for_remove_duplication = []
            payment_customer_id = False
            partner_opening_id = False
            check_type = False
            cust_name = ''
            code_name = ''
            sales_per = ''
            current_month = 0.0
            one_to_fourty_four = 0.0
            fourty_five_to_sixty = 0.0
            sixty_one_to_ninty = 0.0
            above_ninty = 0.0

            def get_so_do_reference(invoice):
                if invoice.origin:
                    origin = str(invoice.origin)
                    if origin.startswith('WH'):
                        picking_id = self.env['stock.picking'].search([('name','=', str(invoice.origin))])
                        if picking_id.sale_id:
                            name = picking_id.sale_id.client_po_ref + '/' + picking_id.sale_id.name or ''
                        else:
                            group_name = picking_id.group_id and picking_id.group_id.name or ''
                            sale_id = self.env['sale.order'].search([('name','=', group_name)])
                            name = sale_id and sale_id.client_po_ref + '/' + sale_id.name or ''
                        return name
                    if origin.startswith('SO'):
                        sale_id = self.env['sale.order'].search([('name','=', origin)])
                        name = sale_id and sale_id.client_po_ref + '/' + sale_id.name or ''
                        return name
                return ''
            for invoices in invoice_browse_objs:
                row_data = {}
                if str(invoices.keys()[0]) in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']:
                    invoice = account_invoice.sudo().browse(invoices.values()[0])
                    # ('state','in',['open']),
                    # ('date_invoice','>=',self.from_date),('date_invoice','<=',self.to_date),
                    amount = 0
                    if invoice.date_invoice >= self.from_date and  invoice.date_invoice <= self.to_date:
                        row_data = {
                            'Reference': get_number(invoice.number) or invoice.number or '',
                            'code': invoice.partner_id.cust_number or False,
                            'customer name': invoice.partner_id and invoice.partner_id.name or '', #Customer Name
                            'Tran. Date': (invoice.date_invoice and datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').strftime('%m/%d/%Y'))  or '', #Invoice Date
                            'sales Person Name': invoice.partner_id.user_id and invoice.partner_id.user_id.name or False, #Sales Person Name
                            'Description': invoice and invoice.origin and get_so_do_reference(invoice) or '',
                            'Balance': '',
                        }
                    else:
                        row_data = {
                            'Reference': '',
                            'code': False,
                            'customer name': '', #Customer Name
                            'Tran. Date': '', #Invoice Date
                            'sales Person Name': False, #Sales Person Name
                            'Description': '',
                            'Balance': '',
                            'Debit amount': 0.0,
                            'Credit amount': 0.0,
                            'Document Type': '',
                        }
                    partner_opening_id = invoice.partner_id and invoice.partner_id.id
                    payment_customer_id = invoice.partner_id and invoice.partner_id.id
                    if self.group_by_partner == 'customer' and invoice.type == 'out_invoice':
                        if invoice.date_invoice >= self.from_date and  invoice.date_invoice <= self.to_date:
                            total_debited_amount += invoice.amount_total
                            row_data.update({'Debit amount': invoice.amount_total or 0.0,'Credit amount': 0.0, 'Document Type': 'I', 'Testing': 'Yes'})
                        if invoice.partner_id.property_payment_term or invoice.payment_term:
                            if invoice.state == 'open':
                                if invoice.due_days <= 30 :
                                    current_month += invoice.residual
                                if invoice.due_days >= 31 and invoice.due_days <= 44:
                                    one_to_fourty_four += invoice.residual
                                if invoice.due_days >= 45 and invoice.due_days <= 60:
                                    fourty_five_to_sixty += invoice.residual
                                if invoice.due_days >= 61 and invoice.due_days <= 90:
                                    sixty_one_to_ninty += invoice.residual
                                if invoice.due_days >= 91:
                                    above_ninty += invoice.residual
                    if self.group_by_partner == 'customer' and invoice.type == 'out_refund':
                        if invoice.date_invoice >= self.from_date and  invoice.date_invoice <= self.to_date:
                            row_data.update({'Debit amount': 0.0,'Credit amount': invoice.amount_total or 0.0, 'Document Type': 'P'})
                            total_credited_amount += invoice.amount_total
                    row += 1
                    sales_per = invoice.partner_id.user_id and invoice.partner_id.user_id.name or 'None', #Sales Person Name
                    code_name = invoice.partner_id and invoice.partner_id.cust_number or  invoice.partner_id.search_contect or ''
                    cust_name = invoice.partner_id.name or ''
                    
                    if invoice.payment_ids:
                        all_payment_list = []
                        for payment in invoice.payment_ids:
                            if payment.date >= self.from_date and  payment.date <= self.to_date:
                                total = 0
                                if payment and payment.move_id and payment.move_id.line_id:
                                    for move in payment.move_id.line_id:
                                        if self.group_by_partner == 'customer':
                                            total += move.debit
                                if payment.move_id and payment.move_id.name not in list_for_remove_duplication:
                                    list_for_remove_duplication.append(payment.move_id.name)
                                    row_data_payment = {
                                                        'payment_no': payment.move_id.name or '',
                                                        'payment_date': (payment.move_id.date and datetime.datetime.strptime(payment.move_id.date, '%Y-%m-%d').strftime('%m/%d/%Y'))  or '', #Invoice Date,
                                                        'Balance': '',
                                                        'ref': payment.move_id.ref,
                                                        }
                                    if self.group_by_partner == 'customer' and invoice.type == 'out_invoice':
                                        row_data_payment.update({'Debit amount':  0.0,'Credit amount': total,'payment Type': 'P'})
                                        total_credited_amount += total
                                    if self.group_by_partner == 'customer' and invoice.type == 'out_refund':
                                        row_data_payment.update({'Debit amount':  total,'Credit amount': 0.0,'payment Type': 'P'})
                                        total_debited_amount += total
                                    all_payment_list.append(row_data_payment)
                        row_data.update({'payment_dict': all_payment_list})
                if str(invoices.keys()[0]) in ['sale', 'purchase']:
                    invoice = account_voucher.sudo().browse(invoices.values() and invoices.values()[0])
                    payment_customer_id = invoice.partner_id and invoice.partner_id.id
                    partner_opening_id = invoice.partner_id and invoice.partner_id.id
                    check_type = str(invoices.keys()[0])
                    row_data = {
                        'Reference': get_number(invoice.number) or invoice.number or '',
                        'code': invoice.partner_id.cust_number or False,
                        'customer name': invoice.partner_id and invoice.partner_id.name or '', #Customer Name
                        'Tran. Date': (invoice.date and datetime.datetime.strptime(invoice.date, '%Y-%m-%d').strftime('%m/%d/%Y'))  or '', #Invoice Date
                        'sales Person Name': invoice.partner_id.user_id and invoice.partner_id.user_id.name or False,
                        'Description': invoice.reference or '',
                        'Balance': '',
                     }
                    if self.group_by_partner == 'customer' and invoice.type == 'sale':
                        if invoice.date_invoice >= self.from_date and  invoice.date_invoice <= self.to_date:
                            row_data.update({'Debit amount': invoice.amount or 0.0,'Credit amount': 0.0, 'Document Type': 'Sale Receipt'})
                            total_debited_amount += invoice.amount
                    sales_per = invoice.partner_id.user_id and invoice.partner_id.user_id.name or 'None', #Sales Person Name
                    code_name = invoice.partner_id and invoice.partner_id.cust_number or  invoice.partner_id.search_contect or ''
                    cust_name = invoice.partner_id.name or ''
                pdf_data.append(row_data)
            if partner_opening_id:
                partner_id_curr = self.env['res.partner'].sudo().browse(group_by_name[group_key][0])
                opening_balance_new = partner_id_curr.with_context({'type':['out_invoice','out_refund']})._get_opening_balance(self.from_date, self.to_date)
                debit_amount = partner_id_curr.with_context({'type':['out_invoice','out_refund']})._get_debit_balance(self.from_date, self.to_date)
                credit_amount = partner_id_curr.with_context({'type':['out_invoice','out_refund']})._get_credit_balance(self.from_date, self.to_date)
                if self.group_by_partner == 'customer':
                    if opening_balance_new >= 0:
                    # if opening_balance_new > 0:
                        if self.group_by_detail == 'detail':
                            opening_bal = [{'Debit amount': "%.2f" % opening_balance_new,'Credit amount': "%.2f" % 0.00, 'Document Type': 'Opening Balance', 'amt':"%.2f" % 0.00, 'Balance': '',
                                              'Reference': '', 'code': '', 'customer name': '', 'Tran. Date': '', 'sales Person Name': '', 'Description': ''}]
                            opening_bal[0]['amt'] =  opening_balance_new
                        total_amount = (total_debited_amount + opening_balance_new) - total_credited_amount
                        total_debited_amount =  (total_debited_amount+ opening_balance_new)
                    else:
                        if self.group_by_detail == 'detail':
                            opening_bal = [{'Debit amount':"%.2f" % 0.0, 'Credit amount': "%.2f" % (opening_balance_new * 1), 'Document Type': 'Opening Balance', 'amt':"%.2f" % 0.00, 'Balance': '',
                                              'Reference': '', 'code': '', 'customer name': '', 'Tran. Date': '', 'sales Person Name': '', 'Description': ''}]
                            opening_bal[0]['amt'] =  opening_balance_new
                        total_amount = total_debited_amount - (total_credited_amount + opening_balance_new)
                        total_credited_amount = (total_credited_amount + opening_balance_new)
            if total_amount > 0:
                cr_or_dr = "Dr."
            if total_amount < 0:
                total_amount = total_amount
                cr_or_dr = "Cr."
            amt_open = total_debited_amount - total_credited_amount
            aged_total = {'current_month':current_month, 'one_to_fourty_four':one_to_fourty_four, 'fourty_five_to_sixty':fourty_five_to_sixty, 'sixty_one_to_ninty':sixty_one_to_ninty, 'above_ninty':above_ninty}
            if self.group_by_detail == 'detail':
                final_amount_list = [{'Debit amount': total_debited_amount or 0.0,'Credit amount': total_credited_amount or 0.0, 'Document Type': '',  'Balance': total_amount,
                                      'Reference': '', 'code': '', 'customer name': '', 'Tran. Date': '', 'sales Person Name': '', 'Description': '', 'aged_total':aged_total}]

            return pdf_data, code_name, sales_per, final_amount_list, opening_bal,cr_or_dr, aged_total, partner_opening_id


# ----------------------------------------------------------------------------------------------------------------------------------------------

         if not self.sales_person:
             # Create Group by and call every groups data from above function and print report.
             group_keys = group_by_name.keys()
             sales_keys_name = 'Nothing'
             row = 0
             group_keys.sort()
             invoice_data.update({'all_invoice_data':[]})
             count = 0
             partner_opening_id = False
             curruncy = self.company_id.currency_id.symbol
             for group_key in group_keys:
               child_invoice_browse_objs = []
               for customer_obj in self.customer_ids:
                   inv_type = group_by_name[group_key][1] and group_by_name[group_key][1][0] and group_by_name[group_key][1][0].keys() and group_by_name[group_key][1][0].keys()[0] or False
                   if customer_obj.is_company and group_key == customer_obj.name and inv_type:
                       child_invoice_id = self.env['account.invoice'].sudo().search(
                        [
                        ('partner_id', 'in', customer_obj.child_ids and customer_obj.child_ids.ids or []),
                        ('type', '=', inv_type),
                        ('state', '=', 'open'),
                        ])
                       for child_inv in child_invoice_id:
                           child_invoice_browse_objs.append({inv_type:child_inv and child_inv.id})
               invoice_browse_objs = group_by_name[group_key][1]
               if child_invoice_browse_objs:
                   invoice_browse_objs.extend(child_invoice_browse_objs)
               invoice_browse_objs = [i for n, i in enumerate(invoice_browse_objs) if i not in invoice_browse_objs[n + 1:]]
               pdf_report_data, code_name, sales_per, final_amount_list, opening_bal,cr_or_dr, aged_total, partner_opening_id = write_invoice(invoice_browse_objs, row, group_key)
               partner_id_curr = self.env['res.partner'].sudo().browse(group_by_name[group_key][0])

               opening_balance_new = partner_id_curr._get_opening_balance(self.from_date, self.to_date)
               # opening_balance = partner_id_curr._credit_debit_get_for_report(['debit', 'credit'], {}, self.from_date)
               if self.group_by_detail == 'detail':
                   invoice_data.update({'is_summery': False})
                   invoice_data['all_invoice_data'].append({'group_name':group_key,'group_invoice_lines': pdf_report_data,
                                                            'code_name': code_name,  'sales_per': sales_per and sales_per[0],
                                                            'partner': self.group_by_partner, 'final_amount_list': final_amount_list, 'is_summery': False, 'opening_balance': opening_bal, 'curruncy': curruncy,'cr_or_dr':cr_or_dr, 'sales_keys_name': sales_keys_name, 'group_by_salesper': False})
               amt = 0
               inv_amt = 0
               pay_amt = 0
               amt_type = False
               if partner_opening_id and opening_balance_new:
                   amt = opening_balance_new
               for invoice_line in pdf_report_data:
                   if amt > 0:
                       amt += invoice_line.get('Debit amount', 0)
                       amt -= invoice_line.get('Credit amount', 0)
                       invoice_line['amt'] = amt
                       payment_dict_list = invoice_line.get('payment_dict', [])
                       inv_amt = amt
                       for payment in payment_dict_list:
                           amt -= payment.get('Credit amount', 0)
                           amt += payment.get('Debit amount', 0)
                           payment['amt'] = amt
                           pay_amt += payment.get('Credit amount', 0)
                           pay_amt += payment.get('Debit amount', 0)
                           if inv_amt > pay_amt:
                               payment['p_amt_type'] = 'Dr.'
                           else:
                               payment['p_amt_type'] = 'Cr.'
                       if inv_amt > pay_amt:
                           invoice_line['i_amt_type'] = 'Dr.'
                       else:
                           invoice_line['i_amt_type'] = 'Cr.'
                   else:
                       amt += invoice_line.get('Debit amount', 0)
                       amt -= invoice_line.get('Credit amount', 0)
                       invoice_line['amt'] = amt
                       payment_dict_list = invoice_line.get('payment_dict', [])
                       inv_amt = amt
                       for payment in payment_dict_list:
                           amt -= payment.get('Credit amount', 0)
                           amt += payment.get('Debit amount', 0)
                           payment['amt'] = amt
                           pay_amt += payment.get('Credit amount', 0)
                           pay_amt += payment.get('Debit amount', 0)
                           if inv_amt > pay_amt:
                               payment['p_amt_type'] = 'Dr.'
                           else:
                               payment['p_amt_type'] = 'Cr.'
                       if inv_amt > pay_amt:
                           invoice_line['i_amt_type'] = 'Dr.'
                       else:
                           invoice_line['i_amt_type'] = 'Cr.' 
                   
               count += 1
             if self._context.has_key('pdf_report'):
                 if self._context.has_key('cron_send') and self._context.has_key('cron_send'):
                    if not check_data_available:
                        return False
                 if not check_data_available:
                     raise ValidationError("No records found for selected options.")
                 return self.env['report'].get_action(self,'ob_party_statement_report.account_party_statement_report_template',data=invoice_data)
             else:
                 count = 0
                 # Create XLS report
                 if not check_data_available and not self._context.has_key('cron_send') and not self._context.has_key('cron_send'):
                     raise ValidationError("No records found for selected options.")
                 row = 2
                 for group_key in group_keys:
                   invoice_browse_objs = group_by_name[group_key][1]
                   invoice_browse_objs_new = []
                   check_exist = []
                   for obj in invoice_browse_objs:
                        if obj.get('out_invoice') not in check_exist:
                            check_exist.append(obj.get('out_invoice'))
                            invoice_browse_objs_new.append(obj)

                   pdf_report_data, code_name, sales_per, final_amount_list, opening_bal,cr_or_dr, aged_total, partner_opening_id = write_invoice(invoice_browse_objs_new, row, group_key)
                   amt = 0.00
                   partner_id_curr = self.env['res.partner'].sudo().browse(group_by_name[group_key][0])
                   opening_balance_new = partner_id_curr._get_opening_balance(self.from_date, self.to_date)
                   if partner_opening_id and opening_balance_new:
                       amt = opening_balance_new
                   for invoice_line in pdf_report_data:
                       if amt > 0:
                           amt += invoice_line.get('Debit amount', 0)
                           amt -= invoice_line.get('Credit amount', 0)
                           invoice_line['amt'] = amt
                           payment_dict_list = invoice_line.get('payment_dict', [])
                           inv_amt = amt
                           for payment in payment_dict_list:
                               amt -= payment.get('Credit amount', 0)
                               amt += payment.get('Debit amount', 0)
                               payment['amt'] = amt
                               pay_amt += payment.get('Credit amount', 0)
                               pay_amt += payment.get('Debit amount', 0)
                               if inv_amt > pay_amt:
                                   payment['p_amt_type'] = 'Dr.'
                               else:
                                   payment['p_amt_type'] = 'Cr.'
                           if inv_amt > pay_amt:
                               invoice_line['i_amt_type'] = 'Dr.'
                           else:
                               invoice_line['i_amt_type'] = 'Cr.'
                       else:
                           amt += invoice_line.get('Debit amount', 0)
                           amt -= invoice_line.get('Credit amount', 0)
                           invoice_line['amt'] = amt
                           payment_dict_list = invoice_line.get('payment_dict', [])
                           inv_amt = amt
                           for payment in payment_dict_list:
                               amt -= payment.get('Credit amount', 0)
                               amt += payment.get('Debit amount', 0)
                               payment['amt'] = amt
                               pay_amt += payment.get('Credit amount', 0)
                               pay_amt += payment.get('Debit amount', 0)
                               if inv_amt > pay_amt:
                                   payment['p_amt_type'] = 'Dr.'
                               else:
                                   payment['p_amt_type'] = 'Cr.'
                           if inv_amt > pay_amt:
                               invoice_line['i_amt_type'] = 'Dr.'
                           else:
                               invoice_line['i_amt_type'] = 'Cr.'
                   # if partner_opening_id and opening_balance_new:
                   #     amt = opening_balance_new 
                   # for invoice_line in pdf_report_data:
                   #     if amt > 0:
                   #         amt += invoice_line.get('Debit amount', 0)
                   #         amt -= invoice_line.get('Credit amount', 0)
                   #         invoice_line['amt'] = amt
                   #         payment_dict_list = invoice_line.get('payment_dict', [])
                   #         for payment in payment_dict_list:
                   #             amt -= payment.get('Credit amount', 0)
                   #             amt += payment.get('Debit amount', 0)
                   #             payment['amt'] = amt
                   #     else:
                   #         amt -= invoice_line.get('Debit amount', 0)
                   #         amt += invoice_line.get('Credit amount', 0)
                   #         invoice_line['amt'] = amt
                   #         payment_dict_list = invoice_line.get('payment_dict', [])
                   #         for payment in payment_dict_list:
                   #             amt += payment.get('Credit amount', 0)
                   #             amt -= payment.get('Debit amount', 0)
                   #             payment['amt'] = amt


                   count += 1
                   if self.group_by_detail == 'detail':
                       row += 2
                       worksheet.write(row,1, 'Account Number:' + code_name, header_bold)
                       if self.group_by_partner == 'customer':
                           worksheet.write(row,2, 'Customer Name:' + group_key, header_bold)
                           worksheet.write(row,3, 'Sales Person Name:' + str(sales_per[0]), header_bold)
                       else:
                           worksheet.write(row,2, 'Supplier Name:' + group_key, header_bold)
                       row += 2
                       detail_header = ['Reference','Tran.Date', 'Document Type', 'Description',
                                   'Dr.Amt.in' + '('+ curruncy +')', 'Cr.Amt.in' +  '('+ curruncy +')','AMT','Balance', 'code', 'customer name', 'sales Person Name']
                       [worksheet.write(row, header_cell, detail_header[header_cell] == 'AMT' and 'Balance' or detail_header[header_cell],header_bold) for header_cell in range(0,len(detail_header)) if detail_header[header_cell] not in ['code', 'customer name', 'sales Person Name', 'Balance']]
                   if self.group_by_detail == 'detail':
                       row +=1
                       for opening in opening_bal:
                           row += 1
                           for index3,col3 in enumerate(header_row):
                               if col3 not in ['code', 'customer name', 'sales Person Name', 'Balance','Document Type']:
                                   worksheet.set_column(row, 0, 25)
                                   if col3 == 'Tran. Date':
                                       if not opening[col3]:
                                           date_opening = datetime.datetime.strptime(self.from_date, '%Y-%m-%d').strftime('%m/%d/%Y')
                                           date_formate = workbook.add_format({'align': 'left'})
                                           worksheet.write(row,index3, date_opening, date_formate)
                                   else: 
                                       worksheet.write(row,index3, opening[col3], merge_format_opening)
                               if col3 in ['Document Type']:
                                   worksheet.set_column(row, 0, 25)
                                   worksheet.write(row,index3, opening[col3])
                       for data in pdf_report_data:
                           if data.get('customer name'):
                               row += 1
                               for index,col in enumerate(header_row):
                                   if col not in ['code', 'customer name', 'sales Person Name']:
                                       if col in ['Debit amount', 'Credit amount','amt', 'Balance']:
                                           worksheet.set_column(row, 0, 25)
                                           if col == 'amt':
                                               amt_type = data.get('i_amt_type')
                                               if data[col] < 0:
                                                    worksheet.write(row,index, str(abs(data[col])) + amt_type, amount_format)
                                               if data[col] > 0:
                                                    worksheet.write(row,index, str(abs(data[col])) + amt_type, amount_format)
                                           else: 
                                                worksheet.write(row,index, data[col],amount_format)
                                       else:
                                           worksheet.set_column(row, 0, 25)
                                           worksheet.write(row,index, data[col])

                           if data.get('payment_dict', False):
                               for payment in data.get('payment_dict'):
                                   row += 1
                                   for index1,col1 in enumerate(payment_header):
                                       if col1 in ['Debit amount', 'Credit amount', 'amt', 'Balance']:
                                           worksheet.set_column(row, 0, 25)
                                           if col1 == 'amt':
                                               amt_type = payment.get('p_amt_type')
                                               if payment[col1] < 0:
                                                    worksheet.write(row,index1, str(abs(payment[col1])) + amt_type, amount_format)
                                               if payment[col1] > 0:
                                                    worksheet.write(row,index1, str(abs(payment[col1])) + amt_type, amount_format)
                                           else: 
                                                worksheet.write(row,index1, payment[col1],amount_format)
                                       else:
                                           worksheet.set_column(row, 0, 25)
                                           worksheet.write(row,index1, payment[col1])

                       for final_line in final_amount_list:
                           row += 1
                           for index2,col2 in enumerate(header_row):
                               if col2 not in ['code', 'customer name', 'sales Person Name', 'amt', 'Balance']:
                                   worksheet.set_column(row, 0, 25)
                                   worksheet.write(row,index2, final_line[col2], amount_bold_format)
                               if col2 in ['Balance']:
                                   row += 1
                                   worksheet.set_column(row, 0, 25)
                                   bal = "Closing Balance: " +curruncy + ' ' + "%.2f" % final_line[col2] + ' '  + cr_or_dr
                                   worksheet.write(row,6, bal, amount_bold_format_right)
                       if aged_total:
                           row += 1
                           val = {'Aged Total', 'Current', '1-44 Days', '45-60 Days', '61-90 Days', 'Over 90 Days'}
                           worksheet.write(row,0, 'Aged Total', amount_bold_format_right)
                           worksheet.write(row,1, 'Current', amount_bold_format_right)
                           worksheet.write(row,2, '1-44 Days', amount_bold_format_right)
                           worksheet.write(row,3, '45-60 Days', amount_bold_format_right)
                           worksheet.write(row,4, '61-90 Days', amount_bold_format_right)
                           worksheet.write(row,5, 'Over 90 Days', amount_bold_format_right)
                           row += 1
                           worksheet.write(row,0, '')
                           worksheet.write(row,1, aged_total.get('current_month'))
                           worksheet.write(row,2, aged_total.get('one_to_fourty_four'))
                           worksheet.write(row,3, aged_total.get('fourty_five_to_sixty'))
                           worksheet.write(row,4, aged_total.get('sixty_one_to_ninty'))
                           worksheet.write(row,5, aged_total.get('above_ninty'))

                 workbook.close()
                 output.seek(0)
                 result = base64.b64encode(output.read())
                 attachment_obj = self.env['ir.attachment']
                 attachment_id = attachment_obj.sudo().create({'name': 'party_statement_report.xlsx', 'datas_fname': 'party_statement_report.xlsx', 'datas': result})
                 download_url = '/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=' + str(attachment_id.id)
                 base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                 return {
                     "type": "ir.actions.act_url",
                     "url": str(base_url) + str(download_url),
                     "target": "self",
                 }

    @api.model
    def send_party_statement_report(self):
        #from_date = str(datetime.datetime.today().month)+"-"+str(1)+"-"+str(datetime.datetime.today().year)
        #to_date = datetime.datetime.today().strftime('%m-%d-%Y')
    	#from_date = str(datetime.datetime.today().month-7)+"-"+str(1)+"-"+str(datetime.datetime.today().year)
    	#any_day= datetime.date(2017, 9, 1)
    	#next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    	#to_date = next_month - datetime.timedelta(days=next_month.day)
    	#to_date = to_date.strftime('%m-%d-%Y')
        
        # from march to current month's 7th date
        from_date = datetime.date(2017, 3, 1).strftime('%m-%d-%Y')
        now_date = datetime.datetime.now()
        month = now_date.month
        year = now_date.year
        to_date = datetime.date(year, month, 7).strftime('%m-%d-%Y')
        
        customer_objs = self.env['res.partner'].search([('customer','=',True)])
        for customer in customer_objs:
            values = {'from_date':from_date, 'to_date':to_date, 'company_id': self.env.user.company_id.id,
            'customer_ids':[(4, customer.id)]}
            party_statement_report = self.env['party.statement.report'].create(values)
            datas = party_statement_report.with_context({'pdf_report':True, 'cron_send':True}).generate_report()
            if not datas:
                continue
            template = self.env.ref('ob_party_statement_report_dard.email_template_party_statement_report')
            self.env['email.template'].browse(template.id).with_context({'datas':datas.get('data')}).send_mail(customer.id)
