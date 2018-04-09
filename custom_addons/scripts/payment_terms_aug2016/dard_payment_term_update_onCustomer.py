#!/usr/bin/env python
# coding: utf-8

###############################################################################################################
# Script purpose is to Imports Customer and its contact in Odoo                                               #
# update payment terms on customer                                                                            #
#                                                                                                             #
#                                                                                                             #
###############################################################################################################
from datetime import datetime
import xmlrpclib
import xlrd

#dbname = 'dard_qa'
#username = 'admin'
#pwd = 'a987654'

# url = 'http://localhost:8888'
# dbname = 'aug_12_dard_test_pay_terms_import'
# username = 'admin'
# pwd = 'admin'

url = 'https://dardbma071501.officebrain.com'
dbname = 'dard_import_new'
username = 'admin'
pwd = 'BrQa!G3m?B'

sock_common = xmlrpclib.ServerProxy (url+'/xmlrpc/common')
sock = xmlrpclib.ServerProxy(url+'/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

workbook = xlrd.open_workbook('customer_number_name_credit_limit_terms_8_11_16.xls')
worksheet = workbook.sheet_by_name('Sheet1')

num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = 0

#SEARCHING ALL PAYMENT TERMS IN ADVANCE
pay_term = sock.execute(dbname, uid, pwd, 'account.payment.term', 'search', [])
payterm_data = sock.execute(dbname, uid, pwd, 'account.payment.term', 'read', pay_term, ['id','name'])
pay_term_ids = [x['id'] for x in payterm_data]
pay_term_names = [x['name'] for x in payterm_data]
index = False
company_id = 1

missing_customers = []
customer_found=0

while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    
    #Field Data Mapping
    field_cust_number = str(row[0].value).strip()
    field_name = row[1].value.strip() #
    field_credit_limit = row[2].value or 0.0
    field_payment_term= row[3].value.strip() or ''

    #Extra data processing for Cust_number
    num_len =  len(field_cust_number)
    prefix_zeros = 13-num_len-1
    field_cust_number = 'C'+'0'*prefix_zeros + field_cust_number

    #must be number
    try: field_credit_limit = float(field_credit_limit)
    except:field_credit_limit = ''

    if field_payment_term:
        if field_payment_term in pay_term_names:
            index = pay_term_names.index(field_payment_term)

    customer_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('cust_number', '=',field_cust_number),('company_id', '=', company_id)])
    if not customer_id:
        customer_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('name', '=', field_name),('company_id', '=', company_id)])
    if customer_id:
        customer_id = customer_id[0]

    if not customer_id:
        missing_customers.append(field_cust_number)
    else:
        customer_found +=1
        vals = {
            'fix_credit_limit':field_credit_limit,
            'allow_credit':True,
            'property_payment_term':pay_term_ids[index],
        }
        result = sock.execute(dbname, uid, pwd, 'res.partner', 'write', customer_id, vals)
        print 'Row number:',curr_row,'  of  ',num_rows,'           customer_id', customer_id, '>>>>',result
        continue
    print 'Row number:',curr_row,'  of  ',num_rows
print '\n>> found',customer_found,'customers'
print '\nList of Customers not found in system,\n',missing_customers

log_file_name = 'missing_customers_'+str(datetime.today().date())+'.csv'
with open(log_file_name, 'w') as f:
    f.write('Total missing_customers:'+str(len(missing_customers))+ \
            '\nUpdated '+str(customer_found)+\
            '\n In Database: '+dbname+'\n\n'+\
            '\n'.join(missing_customers))

print 'IMPORT COMPLETED '
