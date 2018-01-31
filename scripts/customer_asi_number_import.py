#!/usr/bin/env python
# coding: utf-8
import xmlrpclib
import xlrd
import xlwt

dbname = 'dard_import_new'
username = 'admin'
pwd = 'BrQa!G3m?B'

sock_common = xmlrpclib.ServerProxy ('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

workbook = xlrd.open_workbook('customer_and asi_numbers.xlsx')
worksheet = workbook.sheet_by_name('Report1.rpt')
num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1

curr_row = 0

while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    if row[2].value:
	partner_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('customer','=',True),('name', '=', str(row[1].value)),('cust_number', '=', 'C'+str(row[0].value))])
	print "---------partner_id-------",partner_id
        if partner_id:
            res = sock.execute(dbname, uid, pwd, 'res.partner', 'write', partner_id[0], {'asi_number':row[2].value})
            print "---------------res------------------->>>>",res,partner_id,row




