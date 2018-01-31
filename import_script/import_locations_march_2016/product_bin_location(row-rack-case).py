#!/usr/bin/env python
# coding: utf-8
import xmlrpclib
import xlrd

dbname = 'Dard_import'
username = 'admin'
pwd = 'admin'


sock_common = xmlrpclib.ServerProxy ('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

workbook = xlrd.open_workbook('DARD Open Inventory 020516 (1).xls')
worksheet = workbook.sheet_by_name('bin_location_mapping')

curr_row = 2
missing_products=[]

print "Importing Bins..."

roww=[]
rack=[]
case=[]

while curr_row < 1069: #num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    # print row

    field_prod_name = row[10].value.strip()
    loc_row = str(row[11].value).strip().replace('.0','')
    loc_rack = str(row[12].value).strip().replace('.0','')
    loc_case = str(row[13].value).strip().replace('.0','')

    if loc_row == 'N/A' and loc_rack == 'N/A' and  loc_case == 'N/A':
        loc_row = row[1].value.strip()
        loc_rack = ' '
        loc_case = ' '


    product_id = sock.execute(dbname, uid, pwd, 'product.product', 'search', [('default_code', '=',field_prod_name),('purchase_ok', '=',True)])
    if product_id:
        product_id = product_id[0]

        inv_locations = sock.execute(dbname, uid, pwd, 'product.product', 'read', product_id, ['loc_row','loc_rack','loc_case'])

        prod_row = inv_locations['loc_row'] or ''
        prod_rack = inv_locations['loc_rack'] or ''
        prod_case = inv_locations['loc_case'] or ''


        #IF ROW RACK CASE ALREADY THERE APPEND USING /
        if prod_row and prod_rack and prod_case:
            loc_row = prod_row +'/'+loc_row
            loc_rack = prod_rack +'/'+loc_rack
            loc_case = prod_case +'/'+loc_case

        location_vals = {
            'loc_row': loc_row,
            'loc_rack': loc_rack,
            'loc_case': loc_case,
        }

        # uncomment to unset values
        #location_vals = {
        #    'loc_row': False,
        #    'loc_rack': False,
        #    'loc_case': False,
        #}

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
