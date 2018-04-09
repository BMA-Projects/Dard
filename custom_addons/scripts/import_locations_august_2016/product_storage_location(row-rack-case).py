#!/usr/bin/env python
# coding: utf-8
import xmlrpclib
import xlrd

dbname = 'dard_qa'
username = 'admin'
pwd = 'a987654'


sock_common = xmlrpclib.ServerProxy ('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

workbook = xlrd.open_workbook('Item Location with rack detail.xls')
worksheet = workbook.sheet_by_name('Original for Transfer')

curr_row = 0
missing_products=[]

print "Importing Bins..."

roww=[]
rack=[]
case=[]

while curr_row < 783: #num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    field_prod_name = row[0].value.strip()
    loc_row = str(row[3].value).strip().replace('.0','')
    loc_case = str(row[4].value).strip().replace('.0','')
    loc_rack = str(row[5].value).strip().replace('.0','')


    if loc_row == 'N/A' and loc_rack == 'N/A' and  loc_case == 'N/A':
        loc_row = row[1].value.strip()
        loc_rack = ' '
        loc_case = ' '


    product_id = sock.execute(dbname, uid, pwd, 'product.product', 'search', [('old_sku', '=',field_prod_name)])
    	
    if product_id:
        product_id = product_id[0]
        location_vals = {
            'variant_loc_row': loc_row,
            'variant_loc_rack': loc_rack,
            'variant_loc_case': loc_case,
        }

        result = sock.execute(dbname, uid, pwd, 'product.product', 'write', product_id, location_vals)
        print curr_row,'   product_id',product_id,'     sku',field_prod_name,'   result',result,'   vals > ',location_vals
        # print curr_row,'   product_id',product_id,'     sku',field_prod_name,'   result   vals > ',location_vals # just to print logs
    else:
        if field_prod_name:
            missing_products.append(field_prod_name)

print "row rack and case uploaded Successfully on products...!"
print 'missing_products:::',missing_products









'''
possible cases
==================================================
cases - 1
                    row     rack    case
002TBL  1059        17      4       C
002TBL  INSPECT     NA      NA      NA

result  > 
    row     17/INSPECT
    rack    4
    case    C
==================================================
cases - 2
                    row     rack    case
002TBL  INSPECT     NA      NA      NA
002TBL  1059        17      4       C

result  > 
    row     INSPECT/17
    rack    /4
    case    /C
==================================================
cases - 3
                    row     rack    case
002TBL  1059        17      4       C
002TBL  INSPECT     NA      NA      NA
002TBL  1059        17      4       C

result  > 
    row     17/INSPECT/17
    rack    4//4
    case    C//C

'''
