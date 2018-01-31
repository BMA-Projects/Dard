#!/usr/bin/env python
# coding: utf-8
import xmlrpclib
import xlrd
import xlwt
from xlwt import Workbook


dbname = 'dard_import_new'
username = 'admin'
pwd = 'admin'

#sock_common = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/common')
#sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

sock_common = xmlrpclib.ServerProxy ('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')

uid = sock_common.login(dbname, username, pwd)

'''
work_book = xlwt.Workbook(encoding="utf-8")
prod_sheet = work_book.add_sheet("prod_sheet")
'''

workbook = xlrd.open_workbook('DARD Column QTY & LIST Pricing 032316.xls')
worksheet = workbook.sheet_by_name('ProductData')
num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = 1
pversion = 1
missing_sku_list = []
min_qty_row_list = [2, 4, 6, 8]

while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    print curr_row
    product_id = sock.execute(dbname, uid, pwd, 'product.template', 'search', [('name', '=', row[1].value.strip().title()),('sale_ok', '=', True)])
    if not product_id and row[1].value.strip() not in missing_sku_list:
        missing_sku_list.append(str(row[1].value.strip()))

    if product_id:
        for qty_row in min_qty_row_list:
            if row[qty_row].value and row[qty_row + 1].value:
                item_exists = sock.execute(dbname, uid, pwd, 'product.pricelist.item', 'search',
                    [('product_tmpl_id', '=', product_id[0]), ('price_version_id', '=', pversion), ('base', '=', 1), ('min_quantity', '=', int(row[qty_row].value))])
                    
                if item_exists:
                    sock.execute(dbname, uid, pwd, 'product.pricelist.item', 'write', item_exists, {'price_surcharge': row[qty_row + 1].value, 'sequence': 1})
                else:
                    pricelist_item_vals = {
                        'price_version_id': pversion,
                        'name': row[1].value.strip(),
                        'price_surcharge': row[qty_row + 1].value,
                        'base': 1,
                        'min_quantity': int(row[qty_row].value),
                        'sequence': 1,
                        'product_tmpl_id': product_id[0],
                        }
                        
                    new_pricelist_item = sock.execute(dbname, uid, pwd, 'product.pricelist.item', 'create', pricelist_item_vals)

print '----------missing sku----------',missing_sku_list
'''
i = 0
j = 0
for old_item_id in missing_sku_list:
    prod_sheet.write(i, j, old_item_id)
    i += 1
        
work_book.save('Dard Missing Product.xls')
print 'count---',count
'''



















                        
