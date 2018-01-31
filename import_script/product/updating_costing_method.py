    #!/usr/bin/env python
# coding: utf-8

import xmlrpclib
import datetime
start_time = datetime.datetime.now()
print "\nstart time:::::::::", start_time

dbname = 'Dard_import'
username = 'admin'
pwd = 'admin'


sock_common = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

product_ids = sock.execute(dbname, uid, pwd, 'product.product', 'search',[])

for product in product_ids:
	print "product::::::::::::::",product
	update_cost_method =  sock.execute(dbname, uid, pwd, 'product.product', 'write', product,{'cost_method':'average'})
	print "update_cost_method::::::::::::::",update_cost_method

end_time = datetime.datetime.now()
print "the end time is :::>>>", end_time

total_time = end_time - start_time
print "The Total time taken is as follows ::::::>>>>", total_time

print "Products costing method is updated successfully ...!"
