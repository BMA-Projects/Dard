# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import osv, fields
from openerp import _
from openerp.exceptions import Warning

class res_partner(osv.osv):

    _inherit = "res.partner"

    
    def onchange_email(self, cr, uid, ids, email=False,context=None):
        res = {'value': {}}
        if isinstance(ids, (int, long)):ids = [ids]
        search_ids = self.search(cr,uid,[('email','=',email)])
        if search_ids and ids and search_ids.count(ids[0]) >=1:search_ids.remove(ids[0])
        if email and len(search_ids) >= 1:
            raise Warning(_('Email must be unique!'))
        return res
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('email') and len(self.search(cr,uid,[('email','=',vals.get('email'))])) >= 1:
            raise Warning(_('Email must be unique!'))
        partner_id = super(res_partner, self).create(cr, uid, vals, context=context)
        return partner_id
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default['email'] = False
        return super(res_partner, self).copy(cr, uid, id, default, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):ids = [ids]
        if vals.has_key('email'):
            search_ids = self.search(cr,uid,[('email','=',vals.get('email'))])
            if search_ids and ids and search_ids.count(ids[0]) >=1:search_ids.remove(ids[0])
            if vals.get('email') and len(search_ids) >= 1:
                raise Warning(_('Email must be unique!'))
        res = super(res_partner, self).write(cr, uid, ids, vals, context=context)
        return res
    
