#!/usr/bin/env python
# coding: utf-8

###############################################################################################################
# Script purpose is to Imports Customer and its contact in Odoo                                               #
# NOTES:                                                                                                      #
# (IMPORTED FIELDS WHICH ARE CONFIRMED BY S.A                                                                 #
# 1) Add customer number only for cust_name                                                                   #
# 2) Add email for company and contacat                                                                       #
# 3) Do not create contact if name is same as cust_name                                                       #
# 4)                                                                                                          #
#                                                                                                             #
#                                                                                                             #
#                                                                                                             #
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

workbook = xlrd.open_workbook('customers2016.xls')
worksheet = workbook.sheet_by_name('Customers2016.rpt')

num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = 0
company_id = 1  #

#LOG FILE PREPARE
# fname = 'Dard_Import_LOG_Customer ('+str(datetime.datetime.today())+')'
# ftitles = "'cus_no','cus_name','addr_1','addr_2','city','state','zip','country','phone_no','phone_no_2','email_addr','fax_no','slspsn_no','cr_lmt','contact','contact_2'"
# with open(fname, 'a') as f: f.write(ftitles)

#SEARCHING ALL PAYMENT TERMS IN ADVANCE
pay_term = sock.execute(dbname, uid, pwd, 'account.payment.term', 'search', [])
payterm_data = sock.execute(dbname, uid, pwd, 'account.payment.term', 'read', pay_term, ['id','name'])
pay_term_ids = [x['id'] for x in payterm_data]
pay_term_names = [x['name'] for x in payterm_data]
index = False


while curr_row <= 29851:
    curr_row += 1
    row = worksheet.row(curr_row)
    
    #Field Data Mapping
    field_cust_number = 'C'+row[0].value.strip()
    field_name = row[1].value.strip()
    field_street = row[3].value.strip() or ''
    field_street2 = row[4].value.strip() or ''
    field_city = row[5].value.strip()
    field_state = row[6].value.strip()
    field_zip = row[7].value.strip()
    field_country = row[8].value.strip()
    field_phone = row[11].value.strip() or ''
    field_phone2 = row[12].value.strip() or ''
    field_ext1 = row[13].value.strip() or ''
    field_ext2 = row[14].value.strip() or ''
    field_email = row[95].value.strip()
    field_sale_prsn = row[17].value.strip() or False
    field_credit_limit = row[21].value
    field_fax = row[15].value.strip() or ''
    filed_email = row[15].value.strip() or ''
    field_payment_term = row[34].value.strip()
    contact_list =[row[9].value.strip(),row[10].value.strip()]
    contact_list =[x for x in contact_list if len(x)>0]

    #must be number
    try: field_credit_limit = float(field_credit_limit)
    except:field_credit_limit = ''

    if field_phone:
        if field_ext1:
            field_phone+='('+field_ext1+')'

    if field_phone2:
        if field_ext2:
            field_phone2+='('+field_ext2+')'

    if field_payment_term:
        if field_payment_term in pay_term_names:
            index = pay_term_names.index(field_payment_term)

    #write log
    # cols = str(field_cust_number)+','+str(field_name)+','+str(field_street)+','+str(field_street2)+','+str(field_city)+','+str(field_state)+','+str(field_zip)+','+str(field_country)+','+str(field_phone)+','+str(field_phone2)+','+str(field_email)+','+str(field_fax)+','+str(field_sale_prsn)+','+str(field_credit_limit)+','+str(contact_list)
    # with open(fname, 'a') as f:
    #     f.write('\n'+cols)


    if field_sale_prsn:
        sale_person = sock.execute(dbname, uid, pwd, 'res.users', 'search', [('name', '=', field_sale_prsn)])
        if sale_person:
            sale_person = sale_person[0]
        if not sale_person:
            sale_person_vals = {
                'name': field_sale_prsn,
                'login': field_sale_prsn,
                # 'company_id': company_id,
                # 'company_ids': [(6,0,[company_id])]
            }
            sale_person = sock.execute(dbname, uid, pwd, 'res.users', 'create', sale_person_vals)
        #     print "created sale_person ID : created",sale_person
        # print "sale_person ID",sale_person

    state_id = sock.execute(dbname, uid, pwd, 'res.country.state', 'search', [('code', '=',field_state)])
    state_id = state_id and state_id[0] or state_id #??

    country_id = sock.execute(dbname, uid, pwd, 'res.country', 'search', [('code', '=',field_country.upper())])
    country_id = country_id and country_id[0] or country_id #??

    customer_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('cust_number', '=',field_cust_number),('company_id', '=', company_id)])
    if customer_id:
        customer_id = customer_id[0]
    create_new_customer = {
	'name': field_name,
	'cust_number': field_cust_number,
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
	'fix_credit_limit':field_credit_limit,
	'user_id': sale_person,
	'supplier': False,
	'is_company': True,
	'customer': True,
	'allow_credit':True,
	'company_id': company_id,
	'property_payment_term':pay_term_ids[index],
    }
    if not customer_id:
        customer_id = sock.execute(dbname, uid, pwd, 'res.partner', 'create', create_new_customer)
    else:
        result = sock.execute(dbname, uid, pwd, 'res.partner', 'write',customer_id, create_new_customer)
    # else:
    #     sock.execute(dbname, uid, pwd, 'res.partner', 'write',customer_id, {'phone': field_phone, 'mobile':field_phone2, 'allow_credit':True,'fix_credit_limit':field_credit_limit,'property_payment_term':pay_term_ids[index]})
    #     print 'created customer :',customer_id
    # print 'existed customer :',customer_id




    if len(contact_list):
        for contact in contact_list:
            if contact == field_name: continue #not need to create contact if same as Parent
            contact_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('name', '=', contact), ('parent_id', '=', customer_id)])
            if contact_id:
                contact_id = contact_id[0]
            #Because contact info. is not given it is same as parent
	    contact_vals = {
		'name': contact,
		'parent_id': customer_id,
		'use_parent_address': True,
		'phone': field_phone,
		'mobile':field_phone2,
		'fax': field_fax,
		'email': field_email,
		'supplier': False,
		'customer': True,
		'is_company': False,
		'company_id': company_id,
	    }
            if not contact_id:
                contact_id = sock.execute(dbname, uid, pwd, 'res.partner', 'create', contact_vals)
	    else:
	        result = sock.execute(dbname, uid, pwd, 'res.partner', 'write',contact_id, contact_vals)
            #     print 'contact_created',contact_id
            # print 'existing_contact_id',contact_id

    print 'Row number:',curr_row,'  of  29852           customer_id',customer_id

print 'IMPORT COMPLETED '
