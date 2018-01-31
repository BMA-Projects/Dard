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
pwd = 'admin'

sock_common = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')

#sock_common = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/common')
#sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

workbook = xlrd.open_workbook('DARD BOM Component Items 2016 032816.xls')
worksheet = workbook.sheet_by_name('BOM')
num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = 1
duplicate_list = []
component_cols = [3, 13, 23]

print " Updating Dard Supplier and Product Linking ... Please wait ... Thank you for your patience ..."

while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    for com_col in component_cols:
        print '>>>>>>>>>>>>>>>>>>>>>>>>>>',curr_row,com_col
        if row[com_col] and row[com_col + 3]:
            supplier_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('name', '=', row[com_col + 3].value.strip()), ('supplier', '=', True)])

            product_id = sock.execute(dbname, uid, pwd, 'product.template', 'search', [('default_code', '=', row[com_col].value.strip()), ('purchase_ok', '=', True)])
            
            if product_id and supplier_id:

                product_id = product_id[0]
                supplier_id = supplier_id[0]

                supplierinfo_id = sock.execute(dbname, uid, pwd, 'product.supplierinfo', 'search', [('product_tmpl_id', '=', product_id), ('name', '=', supplier_id)])

                if supplierinfo_id:
                    duplicate_list.append(supplierinfo_id)
                    continue
                if not supplierinfo_id:
                    supplierinfo_vals = {
                        'name': supplier_id,
                        #'product_name': row[2].value,
                        #'product_code': row[com_col + 4].value and row[com_col + 4].value.strip() or False,
                        'product_tmpl_id': product_id,
                        'min_qty': 1,
                        'delay' : 1,
                        'sequence': 1,
                    }
                    print '\n vals-----------------------------',supplierinfo_vals
                    supplier_info = sock.execute(dbname, uid, pwd, 'product.supplierinfo', 'create', supplierinfo_vals)
                    
                    
                    pricelist_partner_vals = {
                        'suppinfo_id': supplier_info,
                        'min_quantity': 1,
                        'price': row[com_col + 6].value or False,
                    }
                    pricelist_part_id = sock.execute(dbname, uid, pwd, 'pricelist.partnerinfo', 'create', pricelist_partner_vals)
                    

print "Supplier components price lists have been uploaded Successfully...!",duplicate_list

end_time = datetime.datetime.now()
print "End time is ::::>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", end_time

total_time = end_time - start_time
print "Total Time taken is >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>=========================", total_time

