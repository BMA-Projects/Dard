# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
#
# from openerp.osv import osv, fields
# #Override create method to set user to employee=True to work filter in contacts which list all partners without users.
# class res_users(osv.osv):
#     _inherit = 'res.users'
#
#     def create(self, cr, uid, vals, context=None):
#         user_id = super(res_users, self).create(cr, uid, vals, context=context)
#         user = self.browse(cr, uid, user_id, context=context)
#         if user.partner_id:
#             user.partner_id.write({'employee': True})
#         return user_id
