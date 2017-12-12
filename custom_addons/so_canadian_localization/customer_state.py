# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
#from openerp.addons.base_status.base_stage import base_stage

class CountryState(osv.osv):
    _inherit = "res.country.state"
    _rec_name = 'code'
    _columns = {
        'name': fields.char('Province Name', size=64, required=True, 
                            help='Administrative divisions of a country. E.g. Fed. State, Departement, Canton'),
        'code': fields.char('Province Code', size=3,
            help='The province code in max. three chars.', required=True),
    }
    
class PartnerZip(osv.osv):
    _inherit = "res.partner"

    _columns = {
        'zip': fields.char('Zip', change_default=True, size=7),
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('zip'):
            vals['zip'] = vals['zip'].upper()
            vals['zip'] = ' '.join([vals['zip'][:3], vals['zip'][3:]])
        return super(PartnerZip, self).create(cr, uid, vals,
                context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('zip'):
        # if 'zip' in vals:
            vals['zip'] = vals['zip'].upper()
            vals['zip'] = ' '.join([vals['zip'][:3], vals['zip'][3:]])
        return super(PartnerZip, self).write(cr, uid, ids, vals,
                context=context)
