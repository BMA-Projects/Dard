  # -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################  
from openerp.osv import fields
from openerp.osv import osv


class call_type(osv.osv):
    _name = 'call.type'

    _columns = {
                'name' : fields.char(string='Call Type', required=True, translate=True)
    }
    
class crm_phonecall(osv.osv):
    
    _inherit = 'crm.phonecall'
    
    _columns={
#               'call_type_ids' : fields.many2many('call.type', 'crm_call_type','crm_call_type_id', 'crm_call_type_id1',string='Call Type'),
              'call_type_ids' : fields.many2one('call.type', string="Call Type" ,required=True),
              'follow_up_date':  fields.date("Follow up date"),
              'follow_up_date_from':fields.function(lambda *a,**k:{}, method=True, type='date',string="Follow up from"),
              'follow_up_date_to':fields.function(lambda *a,**k:{}, method=True, type='date',string="Follow up to"),
    }
    