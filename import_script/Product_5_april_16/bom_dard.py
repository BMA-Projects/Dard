#!/usr/bin/env python
# coding: utf-8

import xmlrpclib
import xlrd
import xlwt
import datetime# 2014-11-06 16:21:13#2014-11-06 16:22:31 - 1.18

start_time = datetime.datetime.now()
print "\n start time:::::::::", start_time

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
missing_product_list = []
missing_material_list = []

count = 0
component_list = [3, 13, 23]
print " Updating the Bill of Materials ... Please wait... Thank you for your patience ..."

while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    product_id = sock.execute(dbname, uid, pwd, 'product.product', 'search', [('default_code', '=', row[0].value),('sale_ok','=', True)])

    if product_id:
        product_id = product_id[0]
        product_data = sock.execute(dbname, uid, pwd, 'product.product', 'read', product_id, ['name', 'product_tmpl_id', 'default_code'])
        product_name = product_data['name']
        product_tmpl_id = product_data['product_tmpl_id'][0]
        default_code = product_data['default_code']

        bom_name = '[' + default_code + ']' + ' ' + product_name 
        mrp_bom_id = sock.execute(dbname, uid, pwd, 'mrp.bom', 'search', [('product_tmpl_id', '=', product_tmpl_id), ('product_qty', '=', 1), ('type', '=', 'normal'), ('product_id', '=', product_id)])
        if mrp_bom_id:
            bom_len = len(mrp_bom_id)
            bom_len = str(bom_len + 1)
            print bom_len
            bom_name = '[' + default_code + ']' + ' ' + product_name + '_' + bom_len
            print 'bom_name--------',bom_name
        bom_values = {
            'product_tmpl_id': product_tmpl_id,
            'name': bom_name,
            'product_id': product_id,
            'type': 'normal',
            'product_qty': 1,
        }
        mrp_bom_id = sock.execute(dbname, uid, pwd, 'mrp.bom', 'create', bom_values)
        
        for component_id in component_list:
            if row[component_id].value and row[component_id + 1].value:
                print '------------------value--------',component_id,row[component_id].value
                material_id = sock.execute(dbname, uid, pwd, 'product.product', 'search', [('default_code', '=', row[component_id].value.strip()), ('purchase_ok', '=', True)])
                print '\n material id------',material_id
                
                if material_id:
                    bom_line_id = sock.execute(dbname, uid, pwd, 'mrp.bom.line', 'search', [('bom_id', '=', mrp_bom_id), ('product_id', '=', material_id[0]), ('product_qty', '=', row[component_id + 1].value)])
                    if bom_line_id:
                        count += 1
                    if material_id and not bom_line_id:
                        mrp_bom_line_vals = {
                            'bom_id' : mrp_bom_id,
                            'product_id' : material_id[0],
                            'type' : 'normal',
                            'product_qty' : row[component_id + 1].value,
                            'product_efficiency' : 1.00,
                        }
                        bom_line_id = sock.execute(dbname, uid, pwd, 'mrp.bom.line', 'create', mrp_bom_line_vals)
                if not material_id:
                    missing_material_list.append(str(row[component_id].value))
    
    if not product_id:
        missing_product_list.append(str(row[0].value))
        
print "BOM uploaded Successfully...!",missing_material_list,count
print '\n missing_product_list--------------',missing_product_list


print "End Time is as follows ::: >>> ", datetime.datetime.now()

