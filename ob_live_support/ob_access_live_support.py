# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, fields, api, _
from lxml import etree
from openerp.osv import osv, fields

class res_users(osv.osv):
    _name = 'res.users'
    _inherit = 'res.users'

    _columns = {
    		'live_support' : fields.boolean(string='Live Support', help='Approved For Live support')
    		}
	
    def check_support(self,cr,uid):
   		if uid:
   			context = {}
   			obj_user = self.pool.get('res.users').browse(cr,uid,uid)
   			if (obj_user.live_support == True):
   				return True
   			else:
   				return False