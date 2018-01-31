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
###############################################################################################################
import datetime
import xmlrpclib
import xlrd

dbname = 'dard_import_new'
username = 'admin'
pwd = 'BrQa!G3m?B'

#sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')
#sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
sock_common = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

# workbook = xlrd.open_workbook('dard missing custoemrs.xls')
workbook = xlrd.open_workbook('dard missing custoemrs_may.xls')

worksheet = workbook.sheet_by_name('customer Data')

num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = 0
company_id = 1  #

# #SEARCHING ALL PAYMENT TERMS IN ADVANCE
# pay_term = sock.execute(dbname, uid, pwd, 'account.payment.term', 'search', [])
# payterm_data = sock.execute(dbname, uid, pwd, 'account.payment.term', 'read', pay_term, ['id','name'])
# pay_term_ids = [x['id'] for x in payterm_data]
# pay_term_names = [x['name'] for x in payterm_data]
# index = False

# missing_cust_numbers_raw = ['113146','113147','113144','113145','113142','113143','113140','113141','113064','113067','113066','113061','113060','113063','113062','113069','113068','113212','113213','113151','113150','113153','113152','113155','113156','113159','113158','79350','113091','113093','113094','113096','113097','113252','113099','113250','113251','113256','113254','113255','86040','113253','71994','76256','113124','113125','113126','113127','113120','113121','113123','36056','113083','113244','113081','113080','113087','113086','113243','113084','113089','113088','113249','113248','113235','43122','113221','113137','113136','113135','113134','113133','113132','113131','113139','113138','113230','113232','113233','113234','113246','113236','113237','113238','12772','113229','83425','113228','113102','113103','113106','113107','113104','113108','78570','113223','113222','113188','113227','113226','113225','113183','113180','113181','113186','113187','113184','113185','42892','113119','113118','113115','113114','113116','113111','113110','113113','113112','113056','113057','113219','113216','113217','113214','113215','113058','113059','113210','113211','113197','27180','113199','113198','36576','32220','113169','113160','113161','113162','113163','113164','113165','113166','113167','113209','113208','113201','113200','113203','113202','113204','113207','113206','56923','86093','113245','113179','113178','113173','113172','113171','113177','113247','113174','113072','113073','113070','113071','113076','113077','113074','113075','113241','113078','113079']
# missing_cust_numbers =[]
# for z in missing_cust_numbers_raw:
#     prefix_zeros = 12-len(z)
#     missing_cust_numbers.append('0'*prefix_zeros+z)

found_count = 0
customer_list = []
while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    #Field Data Mapping
    field_cust_number = str(row[0].value).replace('.0', '')
    # if field_cust_number not in missing_cust_numbers:
    #     continue
    # found_count+=1
    # print 'found missing customer\n > cust_number:',field_cust_number,'\t count>>',found_count
    # continue
    # number = 12-len(field_cust_number)
    # field_cust_number = 'C'+ '0' * number + field_cust_number
    field_cust_number = 'C'+ field_cust_number
    field_name = row[1].value.strip()
    field_street = row[4].value.strip() or ''
    field_street2 = row[5].value.strip() or ''
    field_city = row[6].value.strip()
    field_zip = row[7].value.strip()
    field_state = row[8].value.strip()
    field_country = row[9].value.strip()
    field_email = row[10].value.strip()
    field_fax = row[11].value.strip() or ''
    field_phone = row[12].value.strip() or ''
    field_website = row[13].value.strip() or ''
    field_phone2 = row[14].value or ''
    field_sale_prsn = row[15].value.strip() or False
    field_credit_limit = False #row[21].value
    # field_payment_term = row[34].value.strip()
    # contact_list =[row[9].value.strip(),row[10].value.strip()]
    contact_list =row[2].value.strip() or ''
    field_comment = row[16].value.strip() or False

    print 'field_cust_number::',field_cust_number

    #must be number
    try: field_credit_limit = float(field_credit_limit)
    except:field_credit_limit = ''

    # if field_phone:
    #     if field_ext1:
    #         field_phone+='('+field_ext1+')'

    # if field_phone2:
    #     if field_ext2:
    #         field_phone2+='('+field_ext2+')'

    # if field_payment_term:
    #     if field_payment_term in pay_term_names:
    #         index = pay_term_names.index(field_payment_term)

    sale_person = False
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

    customer_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('cust_number', '=',field_cust_number)])
    if customer_id:
        customer_id = customer_id[0]
        print 'existing > customer_id: ',customer_id
    # continue
    create_new_customer = {
        'name': field_name,
        'cust_number': field_cust_number,
        'street': field_street,
        'street2':field_street2,
        'state_id': state_id,
        'country_id': country_id,
        'city': field_city,
        'zip':field_zip,
        'phone': field_phone2,
        'mobile':field_phone,
        'fax': field_fax,
        'email': field_email,
        'user_id': sale_person,
        'supplier': False,
        'is_company': True,
        'customer': True,
        'allow_credit':True,
        'company_id': company_id,
        'comment':field_comment,
        # 'fix_credit_limit':field_credit_limit,
        # 'property_payment_term':pay_term_ids[index],
         }

    if not customer_id:
        customer_id = sock.execute(dbname, uid, pwd, 'res.partner', 'create', create_new_customer)
        print 'created customer'
        customer_list.append(customer_id)
        # sock.execute(dbname, uid, pwd, 'res.partner', 'write',customer_id, create_new_customer)
        # print 'updated customer'
    if len(contact_list):
        for contact in [contact_list]:
            if contact == field_name: continue #not need to create contact if same as Parent
            contact_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('name', '=', contact),('parent_id', '=', customer_id)])
            if contact_id:
                contact_id = contact_id[0]
                print 'found contact >>',contact_id
            #Because contact info. is not given it is same as parent
            contact_vals = {
                'name': contact,
                'parent_id': customer_id,
                'use_parent_address': True,
                'phone': field_phone2,
                'mobile':field_phone,
                'fax': field_fax,
                'email': field_email,
                'supplier': False,
                'customer': True,
                'is_company': False,
                'company_id': company_id,
            }

            if not contact_id:
                contact_id = sock.execute(dbname, uid, pwd, 'res.partner', 'create', contact_vals)
                print '>created contact'
            # else:
            #     contact_list.append(contact)
    print 'Row number:',curr_row,'  of  3           customer_id',customer_id,' Row>>',curr_row
    print '-'*80
    # break
# log_file_name = 'missing_customers_'+str(datetime.today().date())+'.csv'
# with open(log_file_name, 'w') as f:
#     f.write('Total missing_customers:'+str(len(customer_list))+ \
#             '\n In Database: '+dbname+'\n\n'+\
#             '\n'.join(customer_list))
print "customer_list----",customer_list
print "LENGTHHHHH",len(customer_list)
# print "customer_list----",conta_list
print 'IMPORT COMPLETED '
