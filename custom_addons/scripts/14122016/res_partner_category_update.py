#!/usr/bin/env python
# coding: utf-8

import xmlrpclib
import xlrd

dbname = 'dard_pilot_testing'
username = 'admin'
pwd = 'dard@123'

sock_common = xmlrpclib.ServerProxy ('http://localhost:8073/xmlrpc/common')
sock = xmlrpclib.ServerProxy('http://localhost:8073/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

workbook = xlrd.open_workbook('Customer_List_5_31_16.xls')
worksheet = workbook.sheet_by_name('Customers')

num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = -1
eqp_id = sock.execute(dbname, uid, pwd, 'res.partner.category', 'search', [('name', '=', 'EQP')])
standard_id = sock.execute(dbname, uid, pwd, 'res.partner.category', 'search', [('name', '=', 'Standard')])

print "\nImporting customers...", num_rows
partner_not = []
while curr_row < num_rows:
    curr_row += 1
    print "CURT ROW", curr_row
    row = worksheet.row(curr_row)
    if row[0].value:
        partner_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('cust_number', 'ilike', row[0].value)])
        if partner_id:
            if row[17].value == 'Standard Pricing':
                res_partner = {'category_id': [(6,0, standard_id)]}
            elif row[17].value == 'End Quantity Pricing':
                res_partner = {'category_id': [(6,0, eqp_id)]}
            partner_id = sock.execute(dbname, uid, pwd, 'res.partner', 'write',partner_id, res_partner)
        else:
            partner_not.append(curr_row)

print "PARTNER NOT FOUND---->>>", partner_not

print "Contacts uploaded Successfully...!"


