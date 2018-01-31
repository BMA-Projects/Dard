#!/usr/bin/env python
# coding: utf-8
import datetime
import sys
import xmlrpclib
import xlrd
import xlwt


dbname = 'Dard_import'
username = 'admin'
pwd = 'admin'


sock_common = xmlrpclib.ServerProxy ('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

workbook = xlrd.open_workbook('DARD Open Inventory 020516 (1).xls')
worksheet = workbook.sheet_by_name('BIN LIST by ITEM_SAL.rpt')
# num_rows = worksheet.nrows - 1
# num_cells = worksheet.ncols - 1

log_sheet = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(':','-').replace(' ','(')+')'
log_lines = []
new_workbook = xlwt.Workbook()

# VALUES SIMILAR FOR ALL RECORDS!

location_id = None
inventory_id = sock.execute(dbname, uid, pwd, 'stock.inventory', 'search', [('name', '=', 'initial inventory-DARD')])
confirmed_inv_id = sock.execute(dbname, uid, pwd, 'stock.inventory', 'search', [('name', '=', 'initial inventory-DARD'), ('state', '=', 'confirm')])


#CHECK IF STOCK INVENTRY IS EXIST TO ADD LINES
if inventory_id and confirmed_inv_id:
    inventory_id = inventory_id[0] 
    location_id = sock.execute(dbname, uid, pwd, 'stock.inventory', 'read', inventory_id, ['location_id'])
    location_id = location_id['location_id'][0] # {'location_id': [12, 'WH/Stock'], 'id': 1}
    print "Uploading Inventory......."
elif inventory_id and not confirmed_inv_id:
    sys.exit("please set 'initial inventory-DARD' in 'confirm' state")
else:
    sys.exit("please create inventry Adjustment named 'initial inventory-DARD' and set in 'confirm' state")



curr_row = 2 # start row -1
while curr_row <1069:
    curr_row += 1
    row = worksheet.row(curr_row)

    #field mapping
    field_prod_name = row[7].value.strip()
    field_product_qty = row[2].value or 0
    field_uom = 1 # in this case uom is same for all products > 'unit(s)'
    # field_location_name = str(row[1].value) or ''         > Use default stock location no need to use given location
    # field_location_name = field_location_name.strip()

    if field_prod_name: field_prod_name = field_prod_name.upper()
    product_id = sock.execute(dbname, uid, pwd, 'product.product', 'search', [('default_code', '=',field_prod_name)])
    if product_id: product_id = product_id[0]

    product_inventory_id = sock.execute(dbname, uid, pwd, 'stock.inventory.line', 'search', [('product_id', '=', product_id),('product_qty', '=', field_product_qty)])
    if product_inventory_id: product_inventory_id = product_inventory_id[0]

    if product_id:
        inventory_line_val = {
            'inventory_id': inventory_id,
            'product_id': product_id,
            'location_id': location_id,
            'product_uom_id': field_uom,
            'product_qty': field_product_qty
        }

        # NO need to check if inventory line exist because multiple quantity line for same product is given in sheet.
        inventory_line_id = sock.execute(dbname,uid,pwd,'stock.inventory.line','create',inventory_line_val)
        print curr_row,"   inv line created! id : ",inventory_line_id,'   Product id:',product_id,'   product SKU:',field_prod_name,'\n'

        # if not product_inventory_id:
        #     inventory_line_id = sock.execute(dbname,uid,pwd,'stock.inventory.line','create',inventory_line_val)
        #     print "inventory line created id : ",product_id, inventory_line_val ,'>>',inventory_line_id
        # else:
        #     # commented write just because multiple qty line given for same sku and can not find perticular line uniquely
        #     # result = sock.execute(dbname,uid,pwd,'stock.inventory.line','write', product_inventory_id, inventory_line_val)
        #     #To unlink created inv line
        #     # result = sock.execute(dbname,uid,pwd,'stock.inventory.line','unlink', product_inventory_id)
        #     # print result
        #     print "inventory line exists id : ",product_inventory_id,'   Updated:',inventory_line_val
    else:
        if field_prod_name:
            log_lines.append(field_prod_name)

# To write log ony if needed!
if log_lines:
    sheet = new_workbook.add_sheet('missing Products')
    sheet.write(0, 0,'For following SKUs qty given but product not found')

    for l in range(0,len(log_lines)):
        sheet.write(l+1, 0, log_lines[l])

    new_workbook.save('Inventory LOG>'+log_sheet+'.xls')
    print 'Please check sheet named ',log_sheet,' for logs'
print "Inventory Uploaded Successfully...!!"


