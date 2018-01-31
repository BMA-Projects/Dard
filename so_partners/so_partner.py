# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################

from openerp.osv import osv, fields

# class partner_association(osv.osv):
#     _name = 'partner.association'
#     _description = 'Partner Association'
#     _rec_name = 'association_number'
#     _columns = {
#         'association_selection': fields.selection([('other','Other')], 'Associations'),
#         'association_number': fields.char('Association Number', size=64),
#         'partner_id': fields.many2one('res.partner', 'Customer', required=True, ondelete="cascade", select=True),
#     }
#     _defaults = {
#          'association_selection': 'other',
#      }
#
# class partner_email(osv.osv):
#     _name = 'partner.email'
#     _description = 'Partner Emails'
#     _rec_name = 'partner_email'
#     _columns = {
#         'email_selection': fields.selection([('personal','Personal Email'),('company','Company Email'),('other','Other')], 'Emails'),
#         'partner_email': fields.char('Email ID', size=64),
#         'partner_id': fields.many2one('res.partner', 'Customer', required=True, ondelete="cascade", select=True),
#     }
#     _defaults = {
#          'email_selection': 'company',
#      }
#
# class partner_phone(osv.osv):
#     _name = 'partner.phone'
#     _description = 'Partner Phone'
#     _rec_name = 'partner_phone'
#     _columns = {
#         'phone_selection': fields.selection([('home','Home Phone'),('office','Office Phone'),('other','Other')], 'Phone'),
#         'partner_phone': fields.char('Phone Number', size=64),
#         'extension': fields.char('Extension'),
#         'partner_id': fields.many2one('res.partner', 'Customer', required=True, ondelete="cascade", select=True),
#     }
#     _defaults = {
#          'phone_selection': 'office',
#      }
#
# class partner_mobile(osv.osv):
#     _name = 'partner.mobile'
#     _description = 'Partner Mobile'
#     _rec_name = 'mobile_number'
#     _columns = {
#         'mobile_selection': fields.selection([('personal','Personal'),('official','Official'),('other','Other')], 'Mobile'),
#         'mobile_number': fields.char('Mobile Number', size=64),
#         'partner_id': fields.many2one('res.partner', 'Customer', required=True, ondelete="cascade", select=True),
#     }
#     _defaults = {
#          'mobile_selection': 'official',
#      }
# class partner_fax(osv.osv):
#     _name = 'partner.fax'
#     _description = 'Partner Fax'
#     _rec_name = 'partner_fax'
#     _columns = {
#         'fax_selection': fields.selection([('fax1','Company Fax1'),('fax2','Company Fax2'),('other','Other')], 'Fax'),
#         'partner_fax': fields.char('Fax Number', size=64),
#         'partner_id': fields.many2one('res.partner', 'Customer', required=True, ondelete="cascade", select=True),
#     }
#     _defaults = {
#          'fax_selection': 'fax1',
#     }
    
# class partner_social_profile(osv.osv):
#     _name = 'partner.social.profile'
#     _description = 'Partner Social Profiles'
#     _rec_name = 'profile_link'
#     _columns = {
#         'profile_selection': fields.selection([('linkedin','Linkedin'),('facebook','Facebook'),('twitter','Twitter'),('other','Other')], 'Social Media Type'),
#         'profile_link': fields.char('Social Media Link', size=64),
#         'partner_id': fields.many2one('res.partner', 'Customer', required=True, ondelete="cascade", select=True),
#     }
#     _defaults = {
#          'profile_selection': 'linkedin',
#     }
    
class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        # 'association_id': fields.one2many('partner.association', 'partner_id', 'Association Type', help="Associations of Partner"),
        # 'partner_email_id': fields.one2many('partner.email', 'partner_id', 'Emails Type', help="Emails of Partner"),
        # 'partner_phone_id': fields.one2many('partner.phone', 'partner_id', 'Phone Type', help="Phone Numbers of Partner"),
        # 'partner_mobile_id': fields.one2many('partner.mobile', 'partner_id', 'Mobile Type', help="Mobile Numbers of Partner"),
        # 'partner_fax_id': fields.one2many('partner.fax', 'partner_id', 'Fax Type', help="Fax Numbers of Partner"),
        # 'partner_profile_id': fields.one2many('partner.social.profile', 'partner_id', 'Social Media Links', help="Social Media Links of Partner"),
	#From dard_customer_extension
        'account_id': fields.char('Account Id', readonly=True),
        'contact_id': fields.char('Contact Id', readonly=True),
        'asi_number': fields.char('ASI Number'),
        'pppc_number': fields.char('PPPC Number'),
        'sage_number': fields.char('SAGE Number'),
        'create_date': fields.datetime('Create Date', readonly=True),
        'function': fields.char('Job Title'),
        'industry': fields.char('Industry'),
        'extension': fields.char('Extension'),
        'source': fields.char('Source'),
        'source_url': fields.char('Source URL'),
    }
    _defaults = {
        'user_id': lambda self, cr, uid, ctx: uid or False
    }

#     def _get_tracked_fields(self, cr, uid, updated_fields, context=None):
# 
#         if self._name == 'res.partner':
#            for name, column_info in self._all_columns.items():
#                setattr(column_info.column, 'track_visibility', 'onchange')
#                
#         return super(res_partner, self)._get_tracked_fields(cr, uid, updated_fields, context=context)
    
    # set all users to employee to filter only partners not users in contacts 
    # def _user_as_employee(self, cr, uid, ids=None, context=None):
    #     """It will set employee = True to prevent users to list in contacts."""
    #     if ids is not None:
    #         raise NotImplementedError("Ids is just there by convention! Please don't use it.")
    #
    #     res_users_obj = self.pool.get('res.users')
    #     res_users = res_users_obj.search(cr, uid, [])
    #     for user in res_users_obj.browse(cr, uid, res_users, context=context):
    #         if user.partner_id:
    #             user.partner_id.write({'employee': True})

    # def create(self, cr, uid, vals, context=None):
    #     ir_sequence_obj = self.pool.get('ir.sequence')
    #     if vals.get('is_company', False):
    #         vals['account_id'] = ir_sequence_obj.get(cr, uid, 'res.partner.company')
    #     else:
    #         vals['contact_id'] = ir_sequence_obj.get(cr, uid, 'res.partner.contact')
    #     return super(res_partner, self).create(cr, uid, vals, context=context)
    #
    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        ir_sequence_obj = self.pool.get('ir.sequence')
        for partner in self.browse(cr, uid, ids, context):
            #for company
            if vals.get('is_company', False) or partner.is_company and not partner.account_id:
                if not partner.account_id:
                    vals['account_id'] = ir_sequence_obj.get(cr, uid, 'res.partner.company')
                else:
                    vals['account_id'] = partner.account_id
            #for company convert to contact
            elif not vals.get('is_company', False) and partner.account_id and not partner.contact_id:
                vals['contact_id'] = ir_sequence_obj.get(cr, uid, 'res.partner.contact')
            #for child contacts in company
            elif partner.parent_id and not partner.is_company and not partner.account_id:
                company_code = partner.parent_id.account_id
                if company_code:
                    if not partner.contact_id:
                        vals['contact_id'] = company_code + '/' + ir_sequence_obj.get(cr, uid, 'res.partner.contact')
                    elif not '/' in partner.contact_id:
                        vals['contact_id'] = company_code + '/' + partner.contact_id
            #for individual contacts
            elif not partner.parent_id and not partner.is_company and not partner.contact_id:
                vals['contact_id'] = ir_sequence_obj.get(cr, uid, 'res.partner.contact')
        return super(res_partner, self).write(cr, uid, ids, vals, context=context)
    
    # def _assign_ids(self, cr, uid, ids=None, context=None):
    #     """It will assign contact and account ids to all records imported before module install."""
    #     if ids is not None:
    #         raise NotImplementedError("Ids is just there by convention! Please don't use it.")
    #
    #     partners = self.search(cr, uid, ['|',('contact_id','=', None),('account_id','=',None)], order='id')
    #     for partner in self.browse(cr, uid, partners, context=context):
    #         vals = {
    #             'is_company' : partner.is_company,
    #             'contact_id' : partner.contact_id,
    #             'account_id' : partner.account_id,
    #         }
    #         self.write(cr, uid, partner.id, vals, context=context)
    #     return  True

#  Added method for boolean field use_parent_address, if use_parent_address false value of address fields should be blank and vice versa
    def onchange_use_address(self, cr, uid, ids, use_parent_address, parent_id, context=None):
        result = {}
        address_fields = self._address_fields(cr, uid, context=context)
        if parent_id and use_parent_address:
            parent_company = self.browse(cr, uid, parent_id, context=context)
            result['value'] = dict((key, parent_company[key] if isinstance(parent_company[key], (bool, int, long, float, basestring)) else parent_company[key].id) for key in address_fields)
        else:
            result['value'] = dict((key, "") for key in address_fields)
        return result

    def onchange_address(self, cr, uid, ids, use_parent_address, parent_id, context=None):
        result = super(res_partner, self).onchange_address(cr, uid, ids, use_parent_address, parent_id, context)
        if not use_parent_address:
            self.onchange_use_address(cr, uid, ids, use_parent_address, parent_id, context)
            result['value'] = {'use_parent_address': True}
        return result

#End of so_partner
