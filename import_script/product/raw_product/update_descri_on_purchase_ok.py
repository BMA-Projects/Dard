    #!/usr/bin/env python
# coding: utf-8

import xmlrpclib
import xlrd
import xlwt
import datetime
# 2014-11-06 16:21:13#2014-11-06 16:22:31 - 1.18

start_time = datetime.datetime.now()
print "\nstart time:::::::::", start_time

dbname = 'dard_pricelist'
username = 'admin'
pwd = 'admin'

# sock_common = xmlrpclib.ServerProxy ('https://dardbma071501.officebrain.com/xmlrpc/common')
# sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')

sock_common = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/common')
sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

workbook = xlrd.open_workbook('Product_Data_All_Items.xls')
worksheet = workbook.sheet_by_name('Sheet12')
num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = 1



############ For finish products ##########################
while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    product_ids = sock.execute(dbname, uid, pwd, 'product.template', 'search', [('name', '=', row[0].value.strip().title()),('sale_ok','=',False),
                                                                                ('is_variant','=',False),('purchase_ok','=',True)])
    print "::::::::::::::::::::::::::::::::::::::::::::::", product_ids,row[0].value
    if product_ids:
        for i in product_ids:
            product_vals = {
            'description': row[1].value or False,
                            }
        prod_execute = sock.execute(dbname, uid, pwd, 'product.template', 'write', i, product_vals)
        
end_time = datetime.datetime.now()
print "the end time is :::>>>", end_time

total_time = end_time - start_time
print "The Total time taken is as follows ::::::>>>>", total_time

print "Product required ids updated successfully ...!"