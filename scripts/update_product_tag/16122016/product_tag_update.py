import time,re
import xmlrpclib
import xlrd


dbname = 'dard_pilot_testing'
username = 'admin'
pwd = 'dard@123'

sock_common = xmlrpclib.ServerProxy ('http://localhost:8073/xmlrpc/common')
sock = xmlrpclib.ServerProxy('http://localhost:8073/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

stock_item_id = sock.execute(dbname, uid, pwd, 'tag.master', 'search', [('name', 'like', 'Stock Item')])
if not stock_item_id:
    stock_item_id = sock.execute(dbname, uid, pwd, 'tag.master', 'create', {'name':'Stock Item'})

outsourced_id = sock.execute(dbname, uid, pwd, 'tag.master', 'search', [('name', 'like', 'Outsourced')])
if not outsourced_id:
    outsourced_id = sock.execute(dbname, uid, pwd, 'tag.master', 'create', {'name':'Outsourced'})

workbook = xlrd.open_workbook('DARD_Product_Data_All_Items_05_10_16.xlsx')
worksheet = workbook.sheet_by_name('Active Items')
num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = 0
product_not_id = 0
product_not_id1 = 0

while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    product_id = sock.execute(dbname, uid, pwd, 'product.product', 'search', [('default_code', 'ilike', row[1].value.strip())])
    
    if product_id:
        if row[8].value == 'Stock Item' or row[8].value == 'Stocked Item':
            sock.execute(dbname, uid, pwd, 'product.product', 'write', product_id, {'route_ids': [(5, 0, 0)]})
            sock.execute(dbname, uid, pwd, 'product.product', 'write', product_id, {'tag_id': [(6,0, stock_item_id)], 'route_ids': [(6,0,[5,1])]})
        if row[8].value == 'Outsourced':
            sock.execute(dbname, uid, pwd, 'product.product', 'write', product_id, {'route_ids': [(5, 0, 0)]})
            sock.execute(dbname, uid, pwd, 'product.product', 'write', product_id, {'tag_id': [(6,0, outsourced_id)], 'route_ids': [(6,0,[6,1])]})

print "finishhh"
