#!/usr/bin/env python
# coding: utf-8

import xmlrpclib
import datetime

dbname = 'dard_import_new'
username = 'admin'
pwd = 'BrQa!G3m?B'

sock_common = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

contact_ids = sock.execute(dbname, uid, pwd, 'res.partner', 'search',
                          [('parent_id', '!=', False)])
counter = 0
print "...........Updating Contact ids...........", datetime.datetime.now()
for contact_id in contact_ids:
    parent_id = sock.execute(dbname, uid, pwd, 'res.partner', 'read', contact_id, ['parent_id'])
    cust_number = sock.execute(dbname, uid, pwd, 'res.partner', 'read', parent_id.get('parent_id')[0], ['cust_number'])
    if cust_number:
        counter += 1
        cust_number = cust_number.get('cust_number')
        sock.execute(dbname, uid, pwd, 'res.partner', 'write', contact_id, {'search_contect': cust_number})
print "-----counter-----------", counter






