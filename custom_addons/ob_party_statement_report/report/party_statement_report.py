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

class party_statement_report(models.TransientModel):
    _name = 'party.statement.report'

    @api.onchange('from_date','to_date')
    def _onchage_date_chane(self):
        if self.to_date < self.from_date:
            raise ValidationError("To Date must be greater then From Date")

    @api.model
    def _get_all_company(self):
        user_id = self.env['res.users'].browse([self._uid])
        if user_id.company_ids:
            return [('id','in',user_id.company_ids.ids)]
        return [('id','in',[])]

    @api.model
    def _domain_customer(self):
        domain = [('customer','=',True)]
        if self.company_id:domain.append(('company_id','=',self.company_id.id))
        return domain

    @api.model
    def _domain_supplier(self):
        domain = [('supplier','=',True)]
        if self.company_id:domain.append(('company_id','=',self.company_id.id))
        return domain

    @api.onchange('group_by_partner')
    def _onchage_group_by_partner(self):
        self.sales_person = False

    @api.onchange('company_id')
    def _onchage_company_id(self):
        partner_domain = [('company_id','=',self.company_id.id)]
        if self.company_id :
            self.customer_ids = False
            self.supplier_ids = False
        return {'domain': {
                           'customer_ids': self._domain_customer(),
                           'supplier_ids': self._domain_supplier(),
                           }}


    from_date = fields.Date(string='From Date', required=True, default=time.strftime('%Y-%m-01'))
    to_date = fields.Date(string='To Date', required=True, default=time.strftime('%Y-%m-%d'))
    company_id = fields.Many2one('res.company', string="Company", domain=_get_all_company, default=lambda self: self.env.user.company_id, required=True)
    group_by_partner = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Supplier'),
        ], required=True)
    group_by_detail = fields.Selection([
        ('detail', 'Detail'),
        ('summary', 'Summary'),
        ], required=True,default='detail')
    sales_person = fields.Boolean('Sales Person Wise')
    customer_ids = fields.Many2many('res.partner', 'res_customer_party', 'party_id', 'partner_id',string='Customer',domain=_domain_customer)
    supplier_ids = fields.Many2many('res.partner', 'res_supplier_party', 'party_id', 'partner_id',string='Supplier',domain=_domain_supplier)


    @api.multi
    def generate_report(self):
         check_data_available = []
         domain = [
                   ('state','in',['open','paid']),
                   ('date_invoice','>=',self.from_date),('date_invoice','<=',self.to_date)
                  ]
         voucher_domain = [
                           ('state','in',['posted']),
                           ('date','>=',self.from_date),('date','<=',self.to_date)
                           ]

         self._onchage_date_chane()
         # apply domain for customer and supplier
         self.company_id and domain.append(('company_id','=',self.company_id.id))
         self.company_id and voucher_domain.append(('company_id','=',self.company_id.id))
         if self.group_by_partner == 'customer':
             self.customer_ids and domain.append(('partner_id','in',self.customer_ids.ids))
             self.customer_ids and voucher_domain.append(('partner_id','in',self.customer_ids.ids))
         if self.group_by_partner == 'supplier':
             self.supplier_ids and domain.append(('partner_id','in',self.supplier_ids.ids))
             self.supplier_ids and voucher_domain.append(('partner_id','in',self.supplier_ids.ids))
         header_row = []
         payment_header = []

         # Create header list for pdf and xls reports
         if self.group_by_detail == 'detail':
             #table header data
             header_row = ['Tran. No.','Tran. Date', 'Tran. Type', 'Ref. No.', 'Due Date',
                           'Debit amount', 'Credit amount','Balance', 'code', 'customer name', 'sales Person Name']
             payment_header = ['payment_no', 'payment_date', 'payment Type','ref','Due Date','Debit amount', 'Credit amount','Balance']

         if self.group_by_detail == 'summary' and self.group_by_partner == 'customer':
             #table header data
             if not self.sales_person:
                 header_row = ['Sr. No.','Customer Code', 'Customer Name', 'Sales person.',
                               'Debit amount', 'Credit amount','Balance', 'code']
             if self.sales_person:
                 header_row = ['Sr. No.','Customer Code', 'Customer Name',
                               'Debit amount', 'Credit amount','Balance', 'code']

         if self.group_by_detail == 'summary' and self.group_by_partner == 'supplier':
             #table header data
             header_row = ['Sr. No.','Supplier Code', 'Supplier Name', 'Debit amount',
                           'Credit amount','Balance', 'code']

         account_invoice = self.env['account.invoice']
         account_voucher = self.env['account.voucher']

         head_caption = 'Party Statement Report'
         head_caption2 =  'From Date: '

         all_types = []
         if self.group_by_partner == 'customer':
             all_types = ['out_invoice', 'out_refund', 'sale']

         if self.group_by_partner == 'supplier':
             all_types = ['in_invoice', 'in_refund', 'purchase']
         group_by_data = {}
         group_by_name = {}
         # Add new domains as per conditions
         for types in all_types:
             if types in ['out_invoice','in_invoice']:
                 if self.group_by_partner == 'customer':
                     if ('type','=','out_refund') in domain:
                         domain.remove(('type','=','out_refund'))
                     domain.append(('type','=','out_invoice'))
                 if self.group_by_partner == 'supplier':
                     if ('type','=','in_refund') in domain:
                         domain.remove(('type','=','in_refund'))
                     domain.append(('type','=','in_invoice'))

             if types in ['out_refund','in_refund']:
                 if self.group_by_partner == 'customer':
                     if ('type','=','out_invoice') in domain:
                         domain.remove(('type','=','out_invoice'))
                     domain.append(('type','=','out_refund'))
                 if self.group_by_partner == 'supplier':
                     if ('type','=','in_invoice') in domain:
                         domain.remove(('type','=','in_invoice'))
                     domain.append(('type','=','in_refund'))
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

                 if self.group_by_partner == 'supplier':
                     self.sudo()._cr.execute("""select ai.partner_id,ai.id,ai.type
                                          from account_invoice as ai
                                          where ai.id in %s order by ai.date_invoice """,(tuple(account_invoice_obj.ids),))
                     group_name = {'group_by':'partner_id','group_name':"self.env['res.partner'].sudo().browse(group_data[0]).name"}
                     if self.group_by_detail == 'detail':
                         head_caption = "For Supplier - Party Statement Detail Report"
                     else:
                         head_caption = "For Supplier - Party Statement Summary Report"

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
                if self.group_by_partner == 'supplier':
                    self.sudo()._cr.execute("""select ai.partner_id,ai.id,ai.type
                                         from account_voucher as ai
                                         where ai.id in %s order by ai.date """,(tuple(account_voucher_obj.ids),))
                    group_name = {'group_by':'partner_id','group_name':"self.env['res.partner'].sudo().browse(group_data[0]).name"}
                    if self.group_by_detail == 'detail':
                        head_caption = "For Supplier - Party Statement Detail Report"
                    else:
                        head_caption = "For Supplier - Party Statement Summary Report"


             #prepare dict by group name
             if self.group_by_partner:
                 data = self._cr.dictfetchall()
                 if data:
                     for record in data:
                         if group_by_data.has_key(record[group_name['group_by']]):
                             group_by_data[record[group_name['group_by']]].append({record['type']:record['id']})
                         else:
                             group_by_data.update({record[group_name['group_by']]:[{record['type']:record['id']}]})
         if not self.sales_person:
             for group_data in group_by_data.iteritems():
                 group_by_name.update({str(eval(group_name['group_name'])):group_data[1]})
         group_by_sales = [{}]
         if self.sales_person:
             for group_data in group_by_data.iteritems():
                 res_partner = self.env['res.partner'].sudo().browse(group_data[0])
                 sales_person = res_partner.user_id and res_partner.user_id.id or False
                 for sale_per in group_by_sales:
                     if isinstance(sale_per, dict) and not sale_per.get(sales_person):
                         sale_per[sales_person] = [{str(eval(group_name['group_name'])):group_data[1]}]
                     else:
                         sale_per.get(sales_person).append({str(eval(group_name['group_name'])):group_data[1]})
                 group_by_name.update({str(eval(group_name['group_name'])):group_data[1]})
         invoice_data = {'table_header':header_row, 'payment_header': payment_header ,'from_date':self.from_date,'to_date':self.to_date,'company_id':self.company_id and self.company_id.id ,'head_caption':head_caption, 'head_caption2': head_caption2, 'currunt_company': self.company_id.name, 'currunt_company_logo': self.company_id.logo }

         # Make XLS file formating and make header
         if not self._context.has_key('pdf_report'):
             output =  StringIO.StringIO()
             workbook = xlsxwriter.Workbook(output, {'in_memory': True})
             worksheet = workbook.add_worksheet()
             bold = workbook.add_format({'bold': True})
             bold.set_font_color('Blue')
             amount_format = workbook.add_format({'num_format': '0.00'})
             amount_bold_format = workbook.add_format({'num_format': '0.00','bold': True})
             amount_bold_format_right = workbook.add_format({'num_format': '0.00','bold': True,'align': 'right'})
             bold_format_right = workbook.add_format({'bold': True,'align': 'right'})
             header_bold = workbook.add_format({'bold': True})
             merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'left','valign': 'vcenter','fg_color': 'yellow' })
             merge_format_opening = workbook.add_format({'bold': 1,'align': 'right','valign': 'vcenter' })
             merge_format_salesperson = workbook.add_format({'bold': 1,'align': 'center','valign': 'vcenter','fg_color': 'yellow' })
             back_color = 'A1:K2'
             worksheet.merge_range(back_color, head_caption + '  ' + 'From Date: ' + datetime.datetime.strptime(self.from_date, '%Y-%m-%d').strftime('%m/%d/%Y')  + " To : " + datetime.datetime.strptime(self.to_date, '%Y-%m-%d').strftime('%m/%d/%Y') , merge_format)

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
            for invoices in invoice_browse_objs:
                row_data = {}
                if str(invoices.keys()[0]) in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']:
                    invoice = account_invoice.sudo().browse(invoices.values()[0])
                    amount = 0
                    row_data = {
                        'Tran. No.': invoice.number or '',
                        'code': invoice.partner_id.cust_number or False,
                        'customer name': invoice.partner_id and invoice.partner_id.name or '', #Customer Name
                        'Tran. Date': (invoice.date_invoice and datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').strftime('%m/%d/%Y'))  or '', #Invoice Date
                        'sales Person Name': invoice.partner_id.user_id and invoice.partner_id.user_id.name or False, #Sales Person Name
                        'Ref. No.': invoice.origin or '',
                        'Balance': '',
                        'Due Date': (invoice.date_due and datetime.datetime.strptime(invoice.date_due, '%Y-%m-%d').strftime('%m/%d/%Y'))  or '', #Invoice Due Date
                     }
                    partner_opening_id = invoice.partner_id and invoice.partner_id.id
                    payment_customer_id = invoice.partner_id and invoice.partner_id.id
                    if self.group_by_partner == 'customer' and invoice.type == 'out_invoice':
                        total_debited_amount += invoice.amount_total
                        row_data.update({'Debit amount': invoice.amount_total or 0.0,'Credit amount': 0.0, 'Tran. Type': 'Invoice'})
                    if self.group_by_partner == 'customer' and invoice.type == 'out_refund':
                        row_data.update({'Debit amount': 0.0,'Credit amount': invoice.amount_total or 0.0, 'Tran. Type': 'Refund'})
                        total_credited_amount += invoice.amount_total
                    if self.group_by_partner == 'supplier' and invoice.type == 'in_invoice':
                        row_data.update({'Debit amount': 0.0,'Credit amount': invoice.amount_total or 0.0, 'Tran. Type': 'Invoice'})
                        total_credited_amount += invoice.amount_total
                    if self.group_by_partner == 'supplier' and invoice.type == 'in_refund':
                        row_data.update({'Debit amount': invoice.amount_total or 0.0,'Credit amount': 0.0, 'Tran. Type': 'Refund'})
                        total_debited_amount += invoice.amount_total
                    row += 1
                    sales_per = invoice.partner_id.user_id and invoice.partner_id.user_id.name or 'None', #Sales Person Name
                    code_name = invoice.partner_id.cust_number or ''
                    cust_name = invoice.partner_id.name or ''
                    if invoice.payment_ids:
                        all_payment_list = []
                        for payment in invoice.payment_ids:
                            total = 0
                            if payment and payment.move_id and payment.move_id.line_id:
                                for move in payment.move_id.line_id:
                                    if self.group_by_partner == 'customer':
                                        total += move.debit
                                    if self.group_by_partner == 'supplier':
                                        total += move.credit
                            if payment.move_id and payment.move_id.name not in list_for_remove_duplication:
                                list_for_remove_duplication.append(payment.move_id.name)
                                row_data_payment = {
                                                    'payment_no': payment.move_id.name or '',
                                                    'payment_date': (payment.move_id.date and datetime.datetime.strptime(payment.move_id.date, '%Y-%m-%d').strftime('%m/%d/%Y'))  or '', #Invoice Date,
                                                    'Balance': '',
                                                    'ref': payment.move_id.ref,
                                                    'Due Date': '',
                                                    }
                                if self.group_by_partner == 'customer' and invoice.type == 'out_invoice':
                                    row_data_payment.update({'Debit amount':  0.0,'Credit amount': total,'payment Type': 'Receipt'})
                                    total_credited_amount += total
                                if self.group_by_partner == 'customer' and invoice.type == 'out_refund':
                                    row_data_payment.update({'Debit amount':  total,'Credit amount': 0.0,'payment Type': 'Receipt'})
                                    total_debited_amount += total
                                if self.group_by_partner == 'supplier' and invoice.type == 'in_invoice':
                                    row_data_payment.update({'Debit amount':  total,'Credit amount': 0.0,'payment Type': 'Payment'})
                                    total_debited_amount += total
                                if self.group_by_partner == 'supplier' and invoice.type == 'in_refund':
                                    row_data_payment.update({'Debit amount':  0.0,'Credit amount': total,'payment Type': 'Payment'})
                                    total_credited_amount += total
                                all_payment_list.append(row_data_payment)
                        row_data.update({'payment_dict': all_payment_list})
                if str(invoices.keys()[0]) in ['sale', 'purchase']:
                    invoice = account_voucher.sudo().browse(invoices.values() and invoices.values()[0])
                    payment_customer_id = invoice.partner_id and invoice.partner_id.id
                    partner_opening_id = invoice.partner_id and invoice.partner_id.id
                    check_type = str(invoices.keys()[0])
                    row_data = {
                        'Tran. No.': invoice.number or '',
                        'code': invoice.partner_id.cust_number or False,
                        'customer name': invoice.partner_id and invoice.partner_id.name or '', #Customer Name
                        'Tran. Date': (invoice.date and datetime.datetime.strptime(invoice.date, '%Y-%m-%d').strftime('%m/%d/%Y'))  or '', #Invoice Date
                        'sales Person Name': invoice.partner_id.user_id and invoice.partner_id.user_id.name or False,
                        'Ref. No.': invoice.reference or '',
                        'Balance': '',
                        'Due Date': (invoice.date_due and datetime.datetime.strptime(invoice.date_due, '%Y-%m-%d').strftime('%m/%d/%Y'))  or '', #Invoice Due Date
                     }
                    if self.group_by_partner == 'customer' and invoice.type == 'sale':
                        row_data.update({'Debit amount': invoice.amount or 0.0,'Credit amount': 0.0, 'Tran. Type': 'Sale Receipt'})
                        total_debited_amount += invoice.amount
                    if self.group_by_partner == 'supplier' and invoice.type == 'purchase':
                        row_data.update({'Debit amount': 0.0,'Credit amount': invoice.amount or 0.0, 'Tran. Type': 'Purchase Receipt'})
                        total_credited_amount += invoice.amount
                    sales_per = invoice.partner_id.user_id and invoice.partner_id.user_id.name or 'None', #Sales Person Name
                    code_name = invoice.partner_id.cust_number or ''
                    cust_name = invoice.partner_id.name or ''
                pdf_data.append(row_data)
                column_has_amount = []
            if payment_customer_id:
                if self.group_by_partner == 'customer':
                    all_payment_line_data = self.env['account.voucher.line'].sudo().search([('partner_id', '=', payment_customer_id),('type', '=', 'dr'), ('voucher_id.type', '=', 'receipt'),('create_date','>=',self.from_date),('create_date','<=',self.to_date),('company_id','=',self.company_id.id)])
                if self.group_by_partner == 'supplier':
                    all_payment_line_data = []
                if all_payment_line_data:
                    check_data_available.append(all_payment_line_data)
                move_line_ids = [a.move_line_id.id for a in all_payment_line_data]
                move_line_ids = list(set(move_line_ids))
                final_line_ids = []
                for line in all_payment_line_data:
                    if line.move_line_id.id in move_line_ids:
                        final_line_ids.append(line)
                        move_line_ids.remove(line.move_line_id.id)
                if self.group_by_partner == 'customer':
                    all_payment_data_main = self.env['account.voucher'].sudo().search([('partner_id', '=', payment_customer_id),('type', '=', 'receipt'),('amount', '!=', 0), ('state', 'in', ['posted']),('date','>=',self.from_date),('date','<=',self.to_date),('company_id','=',self.company_id.id)])
                    all_payment_data_main_zero = self.env['account.voucher'].sudo().search([('partner_id', '=', payment_customer_id),('type', '=', 'receipt'),('amount', '=', 0), ('state', 'in', ['posted']),('date','>=',self.from_date),('date','<=',self.to_date),('company_id','=',self.company_id.id)])
                if self.group_by_partner == 'supplier':
                    all_payment_data_main = self.env['account.voucher'].sudo().search([('partner_id', '=', payment_customer_id),('type', '=', 'payment'),('amount', '!=', 0), ('state', 'in', ['posted']),('date','>=',self.from_date),('date','<=',self.to_date),('company_id','=',self.company_id.id)])
                    all_payment_data_main_zero = self.env['account.voucher'].sudo().search([('partner_id', '=', payment_customer_id),('type', '=', 'payment'),('amount', '=', 0), ('state', 'in', ['posted']),('date','>=',self.from_date),('date','<=',self.to_date),('company_id','=',self.company_id.id)])
                if all_payment_data_main:
                    check_data_available.append(all_payment_data_main)
                all_payment_data_main_number_zero = [name.number for name in all_payment_data_main_zero]
                for lines in final_line_ids:
                    if lines.move_line_id.name != "/" and lines.move_line_id.name not in list_for_remove_duplication and lines.move_line_id.name not in all_payment_data_main_number_zero:
                        if lines.move_line_id.name:
                            list_for_remove_duplication.append(lines.move_line_id.name)
                        row_data_for_line = {
                            'payment_no': lines.move_line_id.name or '',
                            'payment_date': (lines.date_original and datetime.datetime.strptime(lines.date_original, '%Y-%m-%d').strftime('%m/%d/%Y'))  or '', #Invoice Date
                            'ref':  lines.move_line_id.ref or '',
                            'Balance': '',
                            'Due Date': '',
                         }
                        if self.group_by_partner == 'customer':
                            row_data_for_line.update({'Debit amount': 0.0,'Credit amount': lines.amount_original or 0.0, 'payment Type': 'Receipt'})
                            total_credited_amount += lines.amount_original
                        if self.group_by_partner == 'supplier':
                            row_data_for_line.update({'Debit amount': lines.amount_original or 0.0,'Credit amount': 0.0, 'payment Type': 'Payment'})
                            total_debited_amount += lines.amount_original
                        if pdf_data:
                            if isinstance(row_data.get('payment_dict'), list):
                                row_data.get('payment_dict').append(row_data_for_line)
                            else:
                                row_data.update({'payment_dict': [row_data_for_line]})
                for main in all_payment_data_main:
                    if main.number and main.number not in list_for_remove_duplication:
                        row_data_for_main = {
                            'payment_no': main.number or '',
                            'payment_date': (main.date and datetime.datetime.strptime(main.date, '%Y-%m-%d').strftime('%m/%d/%Y'))  or '', #Invoice Date
                            'ref':  main.reference or '',
                            'Balance': '',
                            'Due Date': '',
                         }
                        if self.group_by_partner == 'customer':
                            row_data_for_main.update({'Debit amount': 0.0,'Credit amount': main.amount or 0.0, 'payment Type': 'Receipt'})
                            total_credited_amount += main.amount
                        if self.group_by_partner == 'supplier':
                            row_data_for_main.update({'Debit amount': main.amount or 0.0,'Credit amount': 0.0, 'payment Type': 'Payment'})
                            total_debited_amount += main.amount

                        if pdf_data:
                            if isinstance(row_data.get('payment_dict'), list):
                                row_data.get('payment_dict').append(row_data_for_main)
                            else:
                                row_data.update({'payment_dict': [row_data_for_main]})
            if partner_opening_id:
                all_jouranal_entry = self.env['account.move.line'].sudo().search([('partner_id','=',partner_opening_id), ('move_id.state', '=', 'posted'),('move_id.date','>=',self.from_date),('move_id.date','<=',self.to_date),('move_id.company_id','=',self.company_id.id)])
                all_ref_data = []
                for data in pdf_data:
                    all_ref_data.append(data.get('Tran. No.'))
                    if 'payment_dict' in data.keys():
                        for pay in data.get('payment_dict'):
                            all_ref_data.append(pay.get('ref'))
                for all in all_jouranal_entry:
                    account_ids = all.partner_id.property_account_receivable if self.group_by_partner == 'customer' else all.partner_id.property_account_payable
                    if all.ref not in all_ref_data and all.account_id == account_ids:
                        row_data_for_journal = {
                            'payment_no': all.move_id.name or '',
                            'payment_date': (all.move_id.date and datetime.datetime.strptime(all.move_id.date, '%Y-%m-%d').strftime('%m/%d/%Y'))  or '', #Invoice Date
                            'ref':  all.name or '',
                            'Balance': '',
                            'Due Date': '',
                            'Debit amount': all.debit or 0.0,
                            'Credit amount': all.credit or 0.0,
                            'payment Type': 'Journal Entry'

                         }
                        total_debited_amount += all.debit or 0
                        total_credited_amount += all.credit or 0

                        if pdf_data:
                            if isinstance(row_data.get('payment_dict'), list):
                                row_data.get('payment_dict').append(row_data_for_journal)
                            else:
                                row_data.update({'payment_dict': [row_data_for_journal]})
            if partner_opening_id:
                partner_id_curr = self.env['res.partner'].sudo().browse(partner_opening_id)
                opening_balance = partner_id_curr._credit_debit_get_for_report(['debit', 'credit'], {}, self.from_date)
                if self.group_by_partner == 'customer':
                    if opening_balance.values()[0]['credit'] >= 0:
                        if self.group_by_detail == 'detail':
                            opening_bal = [{'Debit amount': "%.2f" % opening_balance.values()[0]['credit'],'Credit amount': '', 'Tran. Type': 'Opening Balance', 'Balance': '',
                                              'Tran. No.': '', 'code': '', 'customer name': '', 'Tran. Date': '', 'sales Person Name': '', 'Ref. No.': '', 'Due Date': ''}]
                        total_amount = (total_debited_amount+ opening_balance.values()[0]['credit']) - total_credited_amount
                        total_debited_amount =  (total_debited_amount+ opening_balance.values()[0]['credit'])
                    else:
                        if self.group_by_detail == 'detail':
                            opening_bal = [{'Debit amount': '','Credit amount': "%.2f" % (opening_balance.values()[0]['credit'] * -1), 'Tran. Type': 'Opening Balance', 'Balance': '',
                                              'Tran. No.': '', 'code': '', 'customer name': '', 'Tran. Date': '', 'sales Person Name': '', 'Ref. No.': '', 'Due Date': ''}]
                        total_amount = total_debited_amount - (total_credited_amount + opening_balance.values()[0]['credit'])
                        total_credited_amount = (total_credited_amount + opening_balance.values()[0]['credit'])
                if self.group_by_partner == 'supplier':
                    if opening_balance.values()[0]['credit'] >= 0:
                        if self.group_by_detail == 'detail':
                            opening_bal = [{'Debit amount': '','Credit amount': "%.2f" % opening_balance.values()[0]['debit'], 'Tran. Type': 'Opening Balance', 'Balance': '',
                                              'Tran. No.': '', 'code': '', 'customer name': '', 'Tran. Date': '', 'sales Person Name': '', 'Ref. No.': '', 'Due Date': ''}]
                        total_amount = total_debited_amount - (total_credited_amount + opening_balance.values()[0]['debit'])
                        total_credited_amount = (total_credited_amount + opening_balance.values()[0]['debit'])
                    else:
                        if self.group_by_detail == 'detail':
                            opening_bal = [{'Debit amount': "%.2f" % (opening_balance.values()[0]['debit'] * -1),'Credit amount': '', 'Tran. Type': 'Opening Balance', 'Balance': '',
                                              'Tran. No.': '', 'code': '', 'customer name': '', 'Tran. Date': '', 'sales Person Name': '', 'Ref. No.': '', 'Due Date': ''}]
                        total_amount = (total_debited_amount+ opening_balance.values()[0]['credit']) - total_credited_amount
                        total_debited_amount = (total_debited_amount+ opening_balance.values()[0]['debit'])

            if total_amount > 0:
                cr_or_dr = "Dr."
            if total_amount < 0:
                total_amount = total_amount * -1
                cr_or_dr = "Cr."
            if self.group_by_detail == 'detail':
                final_amount_list = [{'Debit amount': total_debited_amount or 0.0,'Credit amount': total_credited_amount or 0.0, 'Tran. Type': '', 'Balance': total_amount,
                                      'Tran. No.': '', 'code': '', 'customer name': '', 'Tran. Date': '', 'sales Person Name': '', 'Ref. No.': '', 'Due Date': ''}]
            if self.group_by_detail == 'summary' and self.group_by_partner == 'customer':
                final_amount_list = [{'Sr. No.': '', 'Customer Code': code_name, 'Customer Name': cust_name, 'Sales person.': sales_per and sales_per[0] or '',
                                  'Debit amount': total_debited_amount, 'Balance': total_amount,'Credit amount': total_credited_amount or 0.0}]
            if self.group_by_detail == 'summary' and self.group_by_partner == 'supplier':
                final_amount_list = [{'Sr. No.': '', 'Supplier Code': code_name, 'Supplier Name': cust_name,
                            'Debit amount': total_debited_amount, 'Balance': total_amount,'Credit amount': total_credited_amount or 0.0}]

            #if self._context.has_key('pdf_report'):
            return pdf_data, code_name, sales_per, final_amount_list, opening_bal,cr_or_dr


# ----------------------------------------------------------------------------------------------------------------------------------------------

         if self.sales_person:
             invoice_data.update({'all_invoice_data':[]})
             # Create Group by and call every groups data from above function and print report.
             count = 0
             for key, value in group_by_sales[0].iteritems():
                 sales_key_count = 0
                 sales_keys_name = self.env['res.users'].sudo().browse(key).name
                 for final in value:
                     sales_key_count += 1
                     row = 0
                     curruncy = self.company_id.currency_id.symbol
                     if sales_keys_name == False:
                         sales_keys_name = 'None'
                     if sales_key_count != 1:
                         sales_keys_name = 'Nothing'
                     invoice_browse_objs = final.values()[0]
                     pdf_report_data, code_name, sales_per, final_amount_list, opening_bal,cr_or_dr = write_invoice(invoice_browse_objs, row, final.keys())
                     if self.group_by_detail == 'detail':
                         invoice_data.update({'is_summery': False})
                         invoice_data['all_invoice_data'].append({'group_name':final.keys()[0],'group_invoice_lines': pdf_report_data,
                                                                  'code_name': code_name,  'sales_per': sales_per and sales_per[0],
                                                                  'partner': self.group_by_partner, 'final_amount_list': final_amount_list, 'is_summery': False, 'opening_balance': opening_bal, 'curruncy': curruncy,'cr_or_dr':cr_or_dr, 'sales_keys_name': sales_keys_name, 'group_by_salesper': self.sales_person})
                     if self.group_by_detail == 'summary':
                         count += 1
                         invoice_data.update({'is_summery': True, 'curruncy': curruncy})
                         final_amount_list[0]['Sr. No.'] = count
                         invoice_data['all_invoice_data'].append({'group_name':final.keys()[0],'group_invoice_lines': '',
                                                                      'code_name': code_name,  'sales_per': sales_per and sales_per[0],
                                                                      'partner': self.group_by_partner, 'final_amount_list': final_amount_list, 'is_summery': True, 'opening_balance': opening_bal, 'curruncy': curruncy,'cr_or_dr':cr_or_dr, 'sales_keys_name': sales_keys_name, 'group_by_salesper': self.sales_person})
             if self._context.has_key('pdf_report'):
                 if not check_data_available:
                     raise ValidationError("No records found for selected options.")
                 return self.env['report'].get_action(self,'ob_party_statement_report.account_party_statement_report_template',data=invoice_data)
             else:
                 count = 0
                 # Create XLS report
                 if not check_data_available:
                     raise ValidationError("No records found for selected options.")
                 row = 2
                 if self.group_by_detail == 'summary':
                     if self.group_by_partner == 'customer':
                         summary_header = ['Sr. No.','Cust. Code', 'Cust. Name',
                                        'Dr. Amt. in ' + '('+ curruncy +')', 'Cr. Amt. in ' +  '('+ curruncy +')', 'Balance in ' + '('+ curruncy +')', 'code']
                     if self.group_by_partner == 'supplier':
                         #table header data
                         summary_header = ['Sr. No.','Supp. Code', 'Supp. Name',
                                           'Dr. Amt. in ' + '('+ curruncy +')', 'Cr. Amt. in ' +  '('+ curruncy +')', 'Balance in ' + '('+ curruncy +')', 'code']
                     row += 2
                     [worksheet.write(row, header_cell, summary_header[header_cell],header_bold) for header_cell in range(0,len(summary_header)) if summary_header[header_cell] not in ['code', 'customer name', 'sales Person Name']]
                 for key, value in group_by_sales[0].iteritems():
                     sales_key_count = 0
                     sales_keys_name = self.env['res.users'].sudo().browse(key).name
                     for final in value:
                       sales_key_count += 1
                       curruncy = self.company_id.currency_id.symbol
                       if sales_keys_name == False:
                            sales_keys_name = 'None'
                       if sales_key_count != 1:
                          sales_keys_name = 'Nothing'
                       invoice_browse_objs = final.values()[0]
                       pdf_report_data, code_name, sales_per, final_amount_list, opening_bal,cr_or_dr = write_invoice(invoice_browse_objs, row, final.keys())
                       count += 1
                       if self.group_by_detail == 'detail':
                           row += 2
                           if sales_keys_name != 'Nothing':
                               row += 1
                               back_row = 'A'+str(row) +":" +'G'+str(row)
                               worksheet.merge_range(str(back_row), 'Sales Person Name: ' + sales_keys_name, merge_format_salesperson)
                               row +=1
                           worksheet.write(row,1, 'Code:' + code_name, header_bold)
                           if self.group_by_partner == 'customer':
                               worksheet.write(row,2, 'Customer Name:' + final.keys()[0], header_bold)
                           else:
                               worksheet.write(row,2, 'Supplier Name:' + final.keys()[0], header_bold)
                           row += 2
                           detail_header = ['Tran. No.','Tran. Date', 'Tran. Type', 'Ref. No.', 'Due Date',
                                   'Dr. Amt. in ' + '('+ curruncy +')', 'Cr. Amt. in ' +  '('+ curruncy +')','Balance', 'code', 'customer name', 'sales Person Name']
                           [worksheet.write(row, header_cell, detail_header[header_cell],header_bold) for header_cell in range(0,len(detail_header)) if detail_header[header_cell] not in ['code', 'customer name', 'sales Person Name', 'Balance']]
                       if self.group_by_detail == 'detail':
                           row +=1
        #                    back_row = 'F'+str(row) +":" +'G'+str(row)
        #                    worksheet.merge_range(str(back_row), 'Opening Balance:  ' + opening_bal, merge_format_opening)
                           for opening in opening_bal:
                               row += 1
                               for index3,col3 in enumerate(header_row):
                                   if col3 not in ['code', 'customer name', 'sales Person Name', 'Balance','Tran. Type']:
                                       worksheet.set_column(row, 0, 25)
                                       worksheet.write(row,index3, opening[col3], merge_format_opening)
                                   if col3 in ['Tran. Type']:
                                       worksheet.set_column(row, 0, 25)
                                       worksheet.write(row,index3, opening[col3])
                           for data in pdf_report_data:
                               row += 1
                               for index,col in enumerate(header_row):
                                   if col not in ['code', 'customer name', 'sales Person Name']:
                                       if col in ['Debit amount', 'Credit amount','Balance']:
                                           worksheet.set_column(row, 0, 25)
                                           worksheet.write(row,index, data[col],amount_format)
                                       else:
                                           worksheet.set_column(row, 0, 25)
                                           worksheet.write(row,index, data[col])
                               if data.get('payment_dict', False):
                                   for payment in data.get('payment_dict'):
                                       row += 1
                                       for index1,col1 in enumerate(payment_header):
                                           if col1 in ['Debit amount', 'Credit amount','Balance']:
                                               worksheet.set_column(row, 0, 25)
                                               worksheet.write(row,index1, payment[col1],amount_format)
                                           else:
                                               worksheet.set_column(row, 0, 25)
                                               worksheet.write(row,index1, payment[col1])

                           for final_line in final_amount_list:
                               row += 1
                               for index2,col2 in enumerate(header_row):
                                   if col2 not in ['code', 'customer name', 'sales Person Name', 'Balance']:
                                       worksheet.set_column(row, 0, 25)
                                       worksheet.write(row,index2, final_line[col2], amount_bold_format)
                                   if col2 in ['Balance']:
                                       row += 1
                                       worksheet.set_column(row, 0, 25)
                                       bal = "Closing Balance: " +curruncy + ' ' + "%.2f" % final_line[col2] + ' ' + cr_or_dr
                                       worksheet.write(row,6, bal, amount_bold_format_right)
                       if self.group_by_detail == 'summary':
                           final_amount_list[0]['Sr. No.'] = count
                           if sales_keys_name != 'Nothing':
                               row +=3
                               back_row = 'A'+str(row) +":" +'F'+str(row)
                               worksheet.merge_range(str(back_row), 'Sales Person Name: ' + sales_keys_name, merge_format_salesperson)
                           for final_line in final_amount_list:
                               row += 1
                               for index2,col2 in enumerate(header_row):
                                   if col2 in ['Sr. No.', 'Sales person.']:
                                       worksheet.set_column(row, 0, 25)
                                       worksheet.write(row,index2, final_line[col2])
                                   if col2 in ['Balance']:
                                       worksheet.set_column(row, 0, 25)
                                       bal1 = "%.2f" % final_line[col2] + ' ' + cr_or_dr
                                       worksheet.write(row,index2, bal1, bold_format_right)
                                   if col2 not in ['code', 'customer name', 'sales Person Name', 'Sr. No.', 'Sales person.','Balance']:
                                       worksheet.set_column(row, 0, 25)
                                       worksheet.write(row,index2, final_line[col2], amount_format)
                 workbook.close()
                 output.seek(0)
                 result = base64.b64encode(output.read())
                 attachment_obj = self.env['ir.attachment']
                 attachment_id = attachment_obj.create({'name': 'party_statement_report.xlsx', 'datas_fname': 'party_statement_report.xlsx', 'datas': result})
                 download_url = '/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=' + str(attachment_id.id)
                 base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                 return {
                     "type": "ir.actions.act_url",
                     "url": str(base_url) + str(download_url),
                     "target": "self",
                 }


         if not self.sales_person:
             # Create Group by and call every groups data from above function and print report.
             group_keys = group_by_name.keys()
             sales_keys_name = 'Nothing'
             row = 0
             group_keys.sort()
             invoice_data.update({'all_invoice_data':[]})
             count = 0
             curruncy = self.company_id.currency_id.symbol
             for group_key in group_keys:
               invoice_browse_objs = group_by_name[group_key]
               pdf_report_data, code_name, sales_per, final_amount_list, opening_bal,cr_or_dr = write_invoice(invoice_browse_objs, row, group_key)
               if self.group_by_detail == 'detail':
                   invoice_data.update({'is_summery': False})
                   invoice_data['all_invoice_data'].append({'group_name':group_key,'group_invoice_lines': pdf_report_data,
                                                            'code_name': code_name,  'sales_per': sales_per and sales_per[0],
                                                            'partner': self.group_by_partner, 'final_amount_list': final_amount_list, 'is_summery': False, 'opening_balance': opening_bal, 'curruncy': curruncy,'cr_or_dr':cr_or_dr, 'sales_keys_name': sales_keys_name, 'group_by_salesper': False})
               if self.group_by_detail == 'summary':
                   count += 1
                   invoice_data.update({'is_summery': True, 'curruncy': curruncy})
                   final_amount_list[0]['Sr. No.'] = count
                   invoice_data['all_invoice_data'].append({'group_name':group_key,'group_invoice_lines': '',
                                                                'code_name': code_name,  'sales_per': sales_per and sales_per[0],
                                                                'partner': self.group_by_partner, 'final_amount_list': final_amount_list, 'is_summery': True, 'opening_balance': opening_bal, 'curruncy': curruncy,'cr_or_dr':cr_or_dr, 'sales_keys_name': sales_keys_name, 'group_by_salesper': False})
             if self._context.has_key('pdf_report'):
                 if not check_data_available:
                     raise ValidationError("No records found for selected options.")
                 return self.env['report'].get_action(self,'ob_party_statement_report.account_party_statement_report_template',data=invoice_data)
             else:
                 count = 0
                 # Create XLS report
                 if not check_data_available:
                     raise ValidationError("No records found for selected options.")
                 row = 2
                 if self.group_by_detail == 'summary':
                     if self.group_by_partner == 'customer':
                         summary_header = ['Sr. No.','Cust. Code', 'Cust. Name', 'Sales person',
                                       'Dr. Amt. in ' + '('+ curruncy +')', 'Cr. Amt. in ' +  '('+ curruncy +')', 'Balance in ' + '('+ curruncy +')', 'code']
                     if self.group_by_partner == 'supplier':
                         #table header data
                         summary_header = ['Sr. No.','Supp. Code', 'Supp. Name',
                                           'Dr. Amt. in ' + '('+ curruncy +')', 'Cr. Amt. in ' +  '('+ curruncy +')', 'Balance in ' + '('+ curruncy +')', 'code']
                     row += 2
                     [worksheet.write(row, header_cell, summary_header[header_cell],header_bold) for header_cell in range(0,len(summary_header)) if summary_header[header_cell] not in ['code', 'customer name', 'sales Person Name']]
                 for group_key in group_keys:
                   invoice_browse_objs = group_by_name[group_key]
                   pdf_report_data, code_name, sales_per, final_amount_list, opening_bal,cr_or_dr = write_invoice(invoice_browse_objs, row, group_key)
                   count += 1
                   if self.group_by_detail == 'detail':
                       row += 2
                       worksheet.write(row,1, 'Code:' + code_name, header_bold)
                       if self.group_by_partner == 'customer':
                           worksheet.write(row,2, 'Customer Name:' + group_key, header_bold)
                           worksheet.write(row,3, 'Sales Person Name:' + str(sales_per[0]), header_bold)
                       else:
                           worksheet.write(row,2, 'Supplier Name:' + group_key, header_bold)
                       row += 2
                       detail_header = ['Tran. No.','Tran. Date', 'Tran. Type', 'Ref. No.', 'Due Date',
                                   'Dr. Amt. in ' + '('+ curruncy +')', 'Cr. Amt. in ' +  '('+ curruncy +')','Balance', 'code', 'customer name', 'sales Person Name']
                       [worksheet.write(row, header_cell, detail_header[header_cell],header_bold) for header_cell in range(0,len(detail_header)) if detail_header[header_cell] not in ['code', 'customer name', 'sales Person Name', 'Balance']]
                   if self.group_by_detail == 'detail':
                       row +=1
    #                    back_row = 'F'+str(row) +":" +'G'+str(row)
    #                    worksheet.merge_range(str(back_row), 'Opening Balance:  ' + opening_bal, merge_format_opening)
                       for opening in opening_bal:
                           row += 1
                           for index3,col3 in enumerate(header_row):
                               if col3 not in ['code', 'customer name', 'sales Person Name', 'Balance','Tran. Type']:
                                   worksheet.set_column(row, 0, 25)
                                   worksheet.write(row,index3, opening[col3], merge_format_opening)
                               if col3 in ['Tran. Type']:
                                   worksheet.set_column(row, 0, 25)
                                   worksheet.write(row,index3, opening[col3])
                       for data in pdf_report_data:
                           row += 1
                           for index,col in enumerate(header_row):
                               if col not in ['code', 'customer name', 'sales Person Name']:
                                   if col in ['Debit amount', 'Credit amount','Balance']:
                                       worksheet.set_column(row, 0, 25)
                                       worksheet.write(row,index, data[col],amount_format)
                                   else:
                                       worksheet.set_column(row, 0, 25)
                                       worksheet.write(row,index, data[col])
                           if data.get('payment_dict', False):
                               for payment in data.get('payment_dict'):
                                   row += 1
                                   for index1,col1 in enumerate(payment_header):
                                       if col1 in ['Debit amount', 'Credit amount','Balance']:
                                           worksheet.set_column(row, 0, 25)
                                           worksheet.write(row,index1, payment[col1],amount_format)
                                       else:
                                           worksheet.set_column(row, 0, 25)
                                           worksheet.write(row,index1, payment[col1])

                       for final_line in final_amount_list:
                           row += 1
                           for index2,col2 in enumerate(header_row):
                               if col2 not in ['code', 'customer name', 'sales Person Name', 'Balance']:
                                   worksheet.set_column(row, 0, 25)
                                   worksheet.write(row,index2, final_line[col2], amount_bold_format)
                               if col2 in ['Balance']:
                                   row += 1
                                   worksheet.set_column(row, 0, 25)
                                   bal = "Closing Balance: " +curruncy + ' ' + "%.2f" % final_line[col2] + ' '  + cr_or_dr
                                   worksheet.write(row,6, bal, amount_bold_format_right)
                   if self.group_by_detail == 'summary':
                       final_amount_list[0]['Sr. No.'] = count
                       for final_line in final_amount_list:
                           row += 1
                           for index2,col2 in enumerate(header_row):
                               if col2 in ['Sr. No.', 'Sales person.']:
                                   worksheet.set_column(row, 0, 25)
                                   worksheet.write(row,index2, final_line[col2])
                               if col2 in ['Balance']:
                                   worksheet.set_column(row, 0, 25)
                                   bal1 = "%.2f" % final_line[col2] + ' ' + cr_or_dr
                                   worksheet.write(row,index2, bal1, bold_format_right)
                               if col2 not in ['code', 'customer name', 'sales Person Name', 'Sr. No.', 'Sales person.','Balance']:
                                   worksheet.set_column(row, 0, 25)
                                   worksheet.write(row,index2, final_line[col2], amount_format)
                 workbook.close()
                 output.seek(0)
                 result = base64.b64encode(output.read())
                 attachment_obj = self.env['ir.attachment']
                 attachment_id = attachment_obj.create({'name': 'party_statement_report.xlsx', 'datas_fname': 'party_statement_report.xlsx', 'datas': result})
                 download_url = '/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=' + str(attachment_id.id)
                 base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                 return {
                     "type": "ir.actions.act_url",
                     "url": str(base_url) + str(download_url),
                     "target": "self",
                 }
