#!/usr/bin/env python
# coding: utf-8

import xmlrpclib
import xlrd
import xlwt
import datetime

start_time = datetime.datetime.now()
print "\nstart time:::::::::", start_time

dbname = 'dard_import_new'
username = 'admin'
pwd = 'BrQa!G3m?B'

sock_common = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')

#sock_common = xmlrpclib.ServerProxy('http://localhost:8080/xmlrpc/common')
#sock = xmlrpclib.ServerProxy('http://localhost:8080/xmlrpc/object')

uid = sock_common.login(dbname, username, pwd)

workbook = xlrd.open_workbook('DARD Product Data All Items 032816.xls')
worksheet = workbook.sheet_by_name('Active Items')
num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = 1

print " Updating Dard Product ... Thank you for your patience ..."

while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    product_id = sock.execute(dbname, uid, pwd, 'product.product', 'search', [('default_code', '=', row[2].value.strip()), ('purchase_ok', '=', True)])
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>',product_id,row[2].value
    if product_id:
        sock.execute(dbname, uid, pwd, 'product.product', 'write', product_id, {'old_sku': row[1].value.strip()})
    

