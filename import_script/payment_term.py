import datetime
import xmlrpclib
import xlrd

dbname = 'Dard_import'
username = 'admin'
pwd = 'admin'

sock_common = xmlrpclib.ServerProxy ('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

customer_supplier_payment_terms = ['A', 'AB', '210', 'CC', '30', 'CLA', 'AL', '60', 'AT', '7', 'AV', '45', 'NET', '110','WT', '24', '25', '00', '20', '21', '22', '23', '09', '40', '1', '3', '2', '99', 'IMS', '07', '11', '10', '13', '12', '15', '14', '17', '16', '19', '18', 'BRT']

for x in  customer_supplier_payment_terms:
    term_id = sock.execute(dbname, uid, pwd, 'account.payment.term', 'search', [('name','=',x)])
    if not term_id:
        term_id = sock.execute(dbname, uid, pwd, 'account.payment.term', 'create', {'name': x,'note':x})
        print 'created pay_term_id:',term_id,' Name: ',x
print 'done!'
