    #!/usr/bin/env python
# coding: utf-8

import xmlrpclib
import xlrd
import xlwt
import datetime
# 2014-11-06 16:21:13#2014-11-06 16:22:31 - 1.18

start_time = datetime.datetime.now()
print "\nstart time:::::::::", start_time

dbname = 'final_dard_product'
username = 'admin'
pwd = 'a'

# sock_common = xmlrpclib.ServerProxy ('https://dardbma071501.officebrain.com/xmlrpc/common')
# sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')

sock_common = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/common')
sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

workbook = xlrd.open_workbook('Product_Data_All_Items.xls')
worksheet = workbook.sheet_by_name('Sheet2')
num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = 1

cost_price_id = 1640 # this id is of ir_property model where name of this field is "fields_id"

while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    product_ids = sock.execute(dbname, uid, pwd, 'product.product', 'search', [('default_code', '=', row[3].value.strip())])
    print "::::::::::::::::::::::::::::::::::::::::::::::", product_ids

    product_price_history_vals = {
    'value_float': row[2].value
    }

    ir_property_id = sock.execute(dbname, uid, pwd, 'ir.property', 'search', [('fields_id', '=', cost_price_id), ('res_id', '=', 'product.template,'+ str(product_ids)),
                                                                              ('name', '=', 'standard_price')])  
    if not ir_property_id:
        product_price_history_vals = {
        'name': 'standard_price',
        'type': 'float',
        'fields_id': cost_price_id,
        'company_id': 1,
        'res_id':'product.template,' +str(product_ids),
        'value_float': row[2].value or False,
        }
        prod_execute = sock.execute(dbname, uid, pwd, 'ir.property', 'create', product_price_history_vals)
        print "prod_execute-------", prod_execute
    else:
        prod_execute = sock.execute(dbname, uid, pwd, 'ir.property', 'write', ir_property_id, product_price_history_vals)


    
end_time = datetime.datetime.now()
print "the end time is :::>>>", end_time

total_time = end_time - start_time
print "The Total time taken is as follows ::::::>>>>", total_time

print "Product required ids updated successfully ...!"