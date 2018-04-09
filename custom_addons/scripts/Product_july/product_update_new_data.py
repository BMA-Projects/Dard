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

workbook = xlrd.open_workbook('DARD_Product_Data_All_Items_05_10_16.xls')
worksheet = workbook.sheet_by_name('Active Items')
num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = 1
missing_finish_sku = []
missing_row_sku = []

print " Updating Dard Product ... Thank you for your patience ..."

while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    
    row_product_sku = sock.execute(dbname, uid, pwd, 'product.product', 'search_read', [('old_sku', '=', row[2].value.strip()), ('purchase_ok', '=', True)], ['default_code'])
    if row_product_sku:
        print '\n row_product_sku-----------',row_product_sku
        finish_product_sku = 'DP-' + row_product_sku[0]['default_code']
        finish_product_id = sock.execute(dbname, uid, pwd, 'product.product', 'search', [('default_code', '=', finish_product_sku), ('sale_ok', '=', True)])
        #print '\n finish_product_id-----------',finish_product_id,row_product_sku[0]['default_code']
        row_product_vals = {
            'default_code': row[3].value.strip(),
            'description': row[6].value.strip(),
        }
        finish_product_vals = {
            'default_code': row[1].value.strip(),
            'description': row[6].value.strip(),
        }
        # Row product update
        sock.execute(dbname, uid, pwd, 'product.product', 'write', row_product_sku[0]['id'], row_product_vals)
        # Finish product update
        if finish_product_id:
            sock.execute(dbname, uid, pwd, 'product.product', 'write', finish_product_id[0], finish_product_vals)
        if not finish_product_id:
            missing_finish_sku.append(finish_product_sku)
    if not row_product_sku:
        missing_row_sku.append(row[2].value.strip())
        
print '\n missing_row_sku>>>>>>>>>>>>>>>>>',missing_row_sku
print '\n missing_finish_sku--------',missing_finish_sku

    

