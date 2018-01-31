import xmlrpclib
import xlrd
import xlwt
import datetime

start_time = datetime.datetime.now()
print "\n Start Time:::::::::", start_time

#dbname = 'adnart_live'
#username = 'admin'
#pwd = 'YjIfi09S'

dbname = 'Dard_import'
username = 'admin'
pwd = 'admin'

#sock_common = xmlrpclib.ServerProxy('http://localhost:8088/xmlrpc/common')
#sock = xmlrpclib.ServerProxy('http://localhost:8088/xmlrpc/object')

sock_common = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')

uid = sock_common.login(dbname, username, pwd)

#workbook = xlrd.open_workbook('/home/custom_addons/import_script/sales_journal/usd/cnij_sale_usd/CNIJ CustU 2015-12.xls')
workbook = xlrd.open_workbook('Aged Overdue Receivables Detail  (3).xls')

worksheet = workbook.sheet_by_name('Sheet2')
num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = 1

company_id = 1 #1 dard 3 CNIJ 7-FAN
account_id = 33 #8 Adnart 1982-CNIJ 2386-FAN
account_debit = 201 # 1951- Adnart 2350-CNIJ 2366-FAN


print "Importing Adnart Journal Customers... Please wait.. Thank you for your patience ... "

while curr_row < num_rows:
    print "ROW++>", curr_row
    curr_row += 1
    row = worksheet.row(curr_row)
    cust_id = row[1].value
    
    if cust_id:
        partner_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('name', '=', cust_id), ('company_id', '=', company_id), ('customer', '=', True)])

        period_id = sock.execute(dbname, uid, pwd, 'account.period', 'search', [('name', '=', '03/2016'), ('company_id', '=', company_id)])[0]
        if partner_id:
            partner_id = partner_id[0]
            print '\n data format------',datetime.datetime(*xlrd.xldate_as_tuple(row[4].value, workbook.datemode)).strftime('%m-%d-%Y')
            #print "row[5].value", row[5].value
            account_move_dict = {
                'journal_id': 1,#2-adnart 15-CNIIJ 76-FAN
                'period_id': period_id, 
                'company_id': company_id,
                'ref': int(row[2].value) if int(row[2].value) else '',
                'date': datetime.datetime(*xlrd.xldate_as_tuple(row[4].value, workbook.datemode)).strftime('%m/%d/%Y'),
            }
            
            #account_move_line_id_exist = sock.execute(dbname, uid, pwd, 'account.move.line', 'search', [('partner_id', '=', partner_id), ('company_id', '=', company_id)], 1)
            #print "account_move_id_exist",account_move_line_id_exist
            # if account_move_line_id_exist:
            #     account_move = sock.execute(dbname, uid, pwd, 'account.move.line', 'read', account_move_line_id_exist[0], ['move_id'])
            #     account_move_id = account_move['move_id'][0]
            # else:
            print "account_move_dict============================", account_move_dict
            account_move_id = sock.execute(dbname, uid, pwd, 'account.move', 'create', account_move_dict)
                    
            # if account_move_id:
            if row[5].value:
                date_maturity = datetime.datetime(*xlrd.xldate_as_tuple(row[5].value, workbook.datemode)).strftime('%m/%d/%Y'),
                account_move_line_dict = {
                    'name': int(row[2].value) if int(row[2].value) else '',
                    'partner_id': partner_id,
                    'account_id': account_id,
                    'date_maturity': date_maturity,
                    'currency_id':1,
                    'move_id': account_move_id,
                }
            else:
                account_move_line_dict = {
                    'name': int(row[2].value) if int(row[2].value) else '',
                    'partner_id': partner_id,
                    'account_id': account_id,
                    'date_maturity': date_maturity,
                    'currency_id':1,
                    'move_id': account_move_id,
                }

            
            debit = 0.0
            credit = 0.0
            invoice_done = False
            deposit_done = False
            if row[6].value > 0:
                invoice_done = True
                debit = row[6].value
                #account_move_line_dilogin?redirect=https%3A%2F%2Fdardbma071501.officebrain.com%ct['amount_currency'] = row[8].value*-1 if row[8].value<0 else row[8].value
                account_move_line_dict['debit'] = debit
            else:
                deposit_done = True
                credit = row[6].value * -1
                #account_move_line_dict['amount_currency'] = row[8].value if row[8].value<0 else row[8].value*-1
                account_move_line_dict['credit'] = credit
            #print "account_move_line_dict", account_move_line_dict
            


            debit1 = 0.0
            credit1 = 0.0

            if row[5].value:
                account_move_line_dict2 = {
                    'name': int(row[2].value) if int(row[2].value) else '',
                    'partner_id': partner_id,
                    'account_id': account_debit,
                    'date_maturity': datetime.datetime(*xlrd.xldate_as_tuple(row[5].value, workbook.datemode)).strftime('%m/%d/%Y'),
                    'currency_id':1,
                    'move_id': account_move_id,
                }
            else:
                account_move_line_dict2 = {
                    'name': int(row[2].value) if int(row[2].value) else '',
                    'partner_id': partner_id,
                    'account_id': account_debit,
                    'date_maturity': datetime.datetime(*xlrd.xldate_as_tuple(row[5].value, workbook.datemode)).strftime('%m/%d/%Y'),
                    'currency_id':1,
                    'move_id': account_move_id,
                }
            if row[6].value < 0:
                debit1 = row[6].value*-1
                #account_move_line_dict2['amount_currency'] = row[8].value*-1 if row[8].value<0 else row[8].value
                account_move_line_dict2['debit'] = debit1
            elif row[6].value > 0:
                credit1 = row[6].value
                #account_move_line_dict2['amount_currency'] = row[8].value if row[8].value<0 else row[8].value*-1
                account_move_line_dict2['credit'] = credit1
            
            #account_move_line_dict2['credit'] = row[7].value
            # print "account_move_line_dict", account_move_line_dict2
            print "account_move_line_dict", account_move_line_dict
            print "account_move_line_dict2", account_move_line_dict2
            
            if row[6].value > 0:
                account_line_id = sock.execute(dbname, uid, pwd, 'account.move.line', 'create', account_move_line_dict) 
            else:
                account_line_id2 = sock.execute(dbname, uid, pwd, 'account.move.line', 'create', account_move_line_dict2)   


            if row[6].value < 0:
                account_line_id = sock.execute(dbname, uid, pwd, 'account.move.line', 'create', account_move_line_dict) 
            else:
                account_line_id2 = sock.execute(dbname, uid, pwd, 'account.move.line', 'create', account_move_line_dict2) 
        else:
            print "\n\n\nPartner NOT FOUND:::::::::::::::", cust_id
print "-------------The Script has completed its execution-----------------"                
                
