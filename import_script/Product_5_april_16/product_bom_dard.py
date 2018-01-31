#!/usr/bin/env python
# coding: utf-8
import xmlrpclib
import xlrd
import xlwt

dbname = 'dard_import_new'
username = 'admin'
pwd = 'admin'

#sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')
#sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

sock_common = xmlrpclib.ServerProxy ('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')

uid = sock_common.login(dbname, username, pwd)

workbook = xlrd.open_workbook('DARD BOM Component Items 2016 032816.xls')
worksheet = workbook.sheet_by_name('BOM')
num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = 1
count = 0
product_count = 0
Duplicate_product_list = []
count = 0
component_cols = [3, 13, 23]
work_book = xlwt.Workbook(encoding="utf-8")
prod_sheet = work_book.add_sheet("prod_sheet")

print "Product Import"

while curr_row < num_rows:
    curr_row += 1
    print "Current row", curr_row
    row = worksheet.row(curr_row)
    for com_col in component_cols:
        if row[com_col].value and row[com_col + 2].value:
            product_id = sock.execute(dbname, uid, pwd, 'product.template', 'search', [('default_code', '=', row[com_col].value.strip()),('purchase_ok','=', True)])
        
            if product_id:
                product_id = product_id[0]
                product_vals = {
                    'loc_rack' : int(row[com_col + 7].value) or False,
                    'loc_row' : int(row[com_col + 8].value) or False,
                    'loc_case' : row[com_col + 9].value or False,
                }
                new_product = sock.execute(dbname, uid, pwd, 'product.template', 'write', product_id, product_vals)
                
                # Uncomment this code incase product have more than one location
                '''
                product_data = sock.execute(dbname, uid, pwd, 'product.template', 'read', product_id, ['loc_rack', 'loc_row', 'loc_case'])
                if product_data['loc_rack'] and product_data['loc_row'] and product_data['loc_case']:
                    loc_rack = str(product_data['loc_rack']) + '/' + str(int(row[com_col + 7].value))
                    loc_row = str(product_data['loc_row']) + '/' + str(int(row[com_col + 8].value))
                    loc_case = str(product_data['loc_case']) + '/' + str(row[com_col + 9].value)
                    
                
                    product_vals = {
                        'sale_ok' : False,
                        'active': True,
                        'loc_rack' : loc_rack or False,
                        'loc_row' : loc_row or False,
                        'loc_case' : loc_case or False,
                    }
                    print 'product_vals----update>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',product_vals,product_id
                    new_product = sock.execute(dbname, uid, pwd, 'product.template', 'write', product_id, product_vals)
                '''

            if not product_id:
                product_vals = {
                    'name': row[com_col + 2].value.strip(),
                    'default_code': row[com_col].value.strip(),
                    'type': 'product',
                    'purchase_ok': True,
                    'sale_ok' : False,
                    'active': True,
                    'cost_method': 'average',
                    'valuation': 'real_time',
                    'route_ids': [(6, 0, [6])],
                    'loc_rack' : int(row[com_col + 7].value) or False,
                    'loc_row' : int(row[com_col + 8].value) or False,
                    'loc_case' : row[com_col + 9].value or False,
                }
                print 'product_vals---create-----',product_vals
                new_product = sock.execute(dbname, uid, pwd, 'product.template', 'create', product_vals)
                count += 1
print '\n count-------------',count
