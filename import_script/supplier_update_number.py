#!/usr/bin/env python
# coding: utf-8

import xmlrpclib
import xlrd

dbname = 'dard_import_new'
username = 'admin'
pwd = 'BrQa!G3m?B'

sock_common = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

workbook = xlrd.open_workbook('/home/custom_addons/import_script/Vendors_List_5_12_16.xls')
worksheet = workbook.sheet_by_name('Vendor')

num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = -1

parent_id = 0
user_id = 0    
title_id = ''
state_id = 0
country_id = 0
a = 1
b = 1
print "Importing Vendors..."
while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    
    if row[1].value:
        print "row[1].value==>>", row[1].value
        partner_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search',
                                  [('name', '=', row[1].value), ('supplier', '=', True), ('cust_number', '=', False), ('parent_id', '=', False), ('id', '!=', 1)])

        if partner_id:
           cust_number = 'S' + row[0].value
           exist_number = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('cust_number', '=', cust_number)])
           if not exist_number:
               print "partner_id=====>UPDATED", a, ":", partner_id
               res_partner = {
                   'cust_number': cust_number,
               }
               partner = sock.execute(dbname, uid, pwd, 'res.partner', 'write', partner_id, res_partner)
               a+=1
           else:
               print "Vendor Number already Used ---->>NOT UPDATED", b, ":", exist_number
               b+=1

print "Contacts uploaded Successfully...!"


