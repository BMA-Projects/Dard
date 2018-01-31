#!/usr/bin/env python
# coding: utf-8
###############################################################################################################
# Script purpose is to Imports supplier in                 odoo                                               #
# NOTES:                                                                                                      #
###############################################################################################################

import datetime
import xmlrpclib
import xlrd

dbname = 'Dard_import'
username = 'admin'
pwd = 'admin'

sock_common = xmlrpclib.ServerProxy ('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

workbook = xlrd.open_workbook('vendors2016.xls')
worksheet = workbook.sheet_by_name('Report3.rpt')

num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = 0
company_id = 1  #

start_time = datetime.datetime.now()
print 'start_time:',start_time

#To create logs
# ftitles = "'field_vend_number ','field_name ','field_street ','field_street2 ','field_city ','field_state ','field_zip ','field_country ','field_phone ','field_ext ','field_phone2 ','field_ext2 ','field_fax ','field_email ','field_pay_term ','contact_list' "
# fname = 'Dard_Import_LOG_supplier ('+str(datetime.datetime.today())+')'
# with open(fname, 'a') as f:
#     f.write(ftitles)


#Payment Terms
pay_term = sock.execute(dbname, uid, pwd, 'account.payment.term', 'search', [])
payterm_data = sock.execute(dbname, uid, pwd, 'account.payment.term', 'read', pay_term, ['id','name'])

#Payment terms we're going to add in customer
pay_term_ids = [x['id'] for x in payterm_data]
pay_term_names = [x['name'] for x in payterm_data]
index = False


while curr_row <= 2934:
    curr_row += 1
    row = worksheet.row(curr_row)
    
    #Field Data Mapping
    field_vend_number = 'S'+row[0].value.strip() #appnding for Supplier!
    field_name = row[1].value.strip()
    field_street = row[3].value.strip() or ''
    field_street2 = row[4].value.strip() or ''
    field_city = row[5].value.strip()
    field_state = row[6].value.strip()
    field_zip = row[7].value.strip()
    field_country = row[8].value.strip()
    field_phone = row[9].value.strip() or ''
    field_ext = str(row[10].value) or ''
    field_phone2 = row[11].value.strip() or ''
    field_ext2 = str(row[12].value) or ''
    field_fax = row[13].value.strip() or ''
    field_email = row[92].value.strip() or ''
    field_payment_term = row[22].value.strip()
    contact = row[14].value.strip()
    comment = row[81].value.strip() or ''


    #create LOG entry
    # cols = str(field_vend_number )+','+str(field_name )+','+str(field_street )+','+str(field_street2 )+','+str(field_city )+','+str(field_state )+','+str(field_zip )+','+str(field_country )+','+str(field_phone )+','+str(field_ext )+','+str(field_phone2 )+','+str(field_ext2 )+','+str(field_fax )+','+str(field_email )+','+str(field_payment_term )+','+str(contact)
    # with open(fname, 'a') as f:
    #     f.write('\n'+cols)

    state_id = sock.execute(dbname, uid, pwd, 'res.country.state', 'search', [('code', '=',field_state)])
    state_id = state_id and state_id[0] or state_id #??

    country_id = sock.execute(dbname, uid, pwd, 'res.country', 'search', [('code', '=',field_country.upper())])
    country_id = country_id and country_id[0] or country_id #??

    supplier_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('cust_number', '=',field_vend_number),('company_id', '=', company_id)])
    if supplier_id:
        supplier_id = supplier_id[0]
        supplier_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('cust_number', '=',field_vend_number),('company_id', '=', company_id)])

    if field_payment_term:
        if field_payment_term in pay_term_names:
            index = pay_term_names.index(field_payment_term)

    if field_phone:
        if field_ext:
            field_ext=field_ext.replace('.0','')
            field_phone+='('+field_ext+')'

    if field_phone2:
        if field_ext2:
            field_ext=field_ext.replace('.0','')
            field_phone2+='('+field_ext2+')'

    if not supplier_id:
        create_new_supplier = {
            'name': field_name,
            'cust_number': field_vend_number,
            'street': field_street,
            'street2':field_street2,
            'state_id': state_id,
            'country_id': country_id,
            'city': field_city,
            'zip':field_zip,
            'phone': field_phone,
            'mobile':field_phone2,
            'fax': field_fax,
            'email': field_email,
            'supplier': True,
            'is_company': True,
            'customer': False,
            'company_id': company_id,# hardcoded Please set value
            'property_supplier_payment_term': pay_term_ids[index],
            'comment':comment
             }

        supplier_id = sock.execute(dbname, uid, pwd, 'res.partner', 'create', create_new_supplier)
    #can be used to update specific field
    # else:
        # result = sock.execute(dbname, uid, pwd, 'res.partner', 'write',supplier_id,{'state_id':state_id})
        # print result


    if contact:
        if contact == field_name: continue #not need to create contact if same as Parent
        contact_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('name', '=', contact), ('parent_id', '=', supplier_id)])
        if contact_id:
            contact_id = contact_id[0]
        #Because contact info. is not given, it is same as parent
        if not contact_id:
            contact_vals = {
                'name': contact,
                'parent_id': supplier_id,
                'use_parent_address': True,
                'phone': field_phone,
                'mobile':field_phone2,
                'fax': field_fax,
                'email': field_email,
                'supplier': True,
                'customer': False,
                'is_company': False,
                'company_id': company_id,
                'comment': comment
            }
            contact_id = sock.execute(dbname, uid, pwd, 'res.partner', 'create', contact_vals)
        # else:
            # contact_id = sock.execute(dbname, uid, pwd, 'res.partner', 'write',contact_id,{vals here!})
    index =None

    print 'Row number:',curr_row,'  of  2935                supp_id',supplier_id

print 'IMPORT COMPLETED '
end_time = datetime.datetime.now()
print 'Script Execution Time',end_time - start_time

