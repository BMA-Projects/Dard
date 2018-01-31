# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _

class shipping_usps(osv.osv):
    _name = 'shipping.usps'
    
    ## for user default company .................
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'user_id': fields.char('UserID', size=64, required=True, translate=True),
        'test' : fields.boolean('Is test?'),
        'active' : fields.boolean('Active'),
        'partner_id':fields.many2one('res.partner', 'Customer'),
        'company_id':fields.many2one('res.company', 'Company', required=True),
        'country_id':fields.many2one('res.country', 'Country', required=True)
    }
    _defaults = {
        'active' : True,
        'company_id': _get_default_company,
    }
    ## check weather alrady active record exists or not ..........
    def _check_active_settings(self, cr, uid, ids, context=None):
        
        for o in self.browse(cr, uid, ids): 
            record_id = self.search(cr, uid, [('partner_id','=',o.partner_id.id),('country_id','=',o.country_id.id),('id','!=',ids[0])])
            if not record_id:
                return True
            return False
        
    _constraints = [
         (_check_active_settings, 'You Can Not Active Multiple Partner UPS Settings With Same Country', ['country_id']),
     ]
    
    def get_usps_info(self, cr, uid, context=None):
        ship_usps_id = self.search(cr,uid,[('active','=',True)])
        if not ship_usps_id:
            ### This is required because when picking is created when saleorder is confirmed and if the default
            ### parameter has some error then it should not stop as the order is getting imported from external sites
            if context['type'] == 'all':
                return None
            else:
                raise osv.except_osv(_('Error'), _('Active USPS settings not defined'))
        else:
            ship_usps_id = ship_usps_id[0]
        return self.browse(cr,uid,ship_usps_id)
    
    
    def get_usps_partner_info(self, cr, uid, ids, context=None):
        
        picking_obj = self.pool.get('stock.picking')
        
        for picking_record in picking_obj.browse(cr, uid, ids):
            if not picking_record.partner_id.country_id:
                raise osv.except_osv(_('Error'), _('Please define country for partner'))
                
            ship_ups_id = self.search(cr,uid,[('partner_id','=',picking_record.partner_id.id),('country_id','=',picking_record.partner_id.country_id.id),('active','=',True)])
            if not ship_ups_id:
                ### This is required because when picking is created when saleorder is confirmed and if the default parameter has some error then it should not stop as the order is getting imported from external sites
                raise osv.except_osv(_('Error'), _('Customer USPS settings not defined'))
            else:
                ship_ups_id = ship_ups_id[0]
            return self.browse(cr, uid, ship_ups_id)
    
shipping_usps()

class shipping_fedex(osv.osv):
    _name = 'shipping.fedex'
    
    ## for user default company .................
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    
    _rec_name = 'account_no'
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'account_no': fields.char('Account Number', size=64, required=True),
        'key': fields.char('Key', size=64, required=True),
        'password': fields.char('Password', size=64, required=True),
        'meter_no': fields.char('Meter Number', size=64, required=True),
        'integrator_id': fields.char('Integrator ID', size=64, required=True),
        'test' : fields.boolean('Is test?'),
        'active' : fields.boolean('Active'),
        'partner_id':fields.many2one('res.partner', 'Customer'),
        'company_id':fields.many2one('res.company', 'Company', required=True),
        'country_id':fields.many2one('res.country', 'Country', required=True)
    }
    _defaults = {
        'active' : True,
        'company_id': _get_default_company,
    }
    
    # check weather alrady active record exists or not ..........
    def _check_active_settings(self, cr, uid, ids, context=None):
        
        for o in self.browse(cr, uid, ids): 
            record_id = self.search(cr, uid, [('partner_id','=',o.partner_id.id),('country_id','=',o.country_id.id),('id','!=',ids[0])])
            if not record_id:
                return True
            return False
        
    _constraints = [
         (_check_active_settings, 'You Can Not Active Multiple Partner FEDEX Settings With Same Country ', ['country_id']),
     ]
shipping_fedex()

class shipping_ups(osv.osv):
    _name = 'shipping.ups'

    ## for user default company .................
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    
    _rec_name = 'shipper_no'
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'access_license_no': fields.char('Access License Number', size=64, required=True),
        'user_id': fields.char('UserID', size=64, required=True),
        'password': fields.char('Password', size=64, required=True),
        'shipper_no': fields.char('Shipper Number', size=64, required=True),
        'test' : fields.boolean('Is test?'),
        'active' : fields.boolean('Active'),
        'partner_id':fields.many2one('res.partner', 'Customer'),
        'company_id':fields.many2one('res.company', 'Company', required=True),
        'country_id':fields.many2one('res.country', 'Country', required=True)
    }
    _defaults = {
                'active':True,
                'company_id': _get_default_company,  
    }
    ## check weather alrady active record exists or not ..........
    def _check_active_settings(self, cr, uid, ids, context=None):
        
        for o in self.browse(cr, uid, ids): 
            record_id = self.search(cr, uid, [('partner_id','=',o.partner_id.id),('country_id','=',o.country_id.id),('id','!=',ids[0])])
            if not record_id:
                return True
            return False
        
    _constraints = [
         (_check_active_settings, 'You Can Not Active Multiple Partner UPS Settings With Same Country', ['country_id']),
     ]
    
    def get_ups_info(self,cr,uid,context=None):
        ship_ups_id = self.search(cr,uid,[('active','=',True)])
        if not ship_ups_id:
            if context['type'] == 'all':
                return None
            else:
                ### This is required because when picking is created when saleorder is confirmed and if the default parameter has some error then it should not stop as the order is getting imported from external sites
                raise osv.except_osv(_('Error'), _('Active UPS settings not defined'))
        else:
            ship_ups_id = ship_ups_id[0]
        return self.browse(cr,uid,ship_ups_id)
    ## customer account ups settings .......................
    def get_ups_partner_info(self, cr, uid, ids, context=None):
        
        picking_obj = self.pool.get('stock.picking')
        
        for picking_record in picking_obj.browse(cr, uid, ids):
            if not picking_record.partner_id.country_id:
                raise osv.except_osv(_('Error'), _('Please define country for partner'))
                
                
            ship_ups_id = self.search(cr,uid,[('partner_id','=',picking_record.partner_id.id),('country_id','=',picking_record.partner_id.country_id.id),('active','=',True)])
            if not ship_ups_id:
                ### This is required because when picking is created when saleorder is confirmed and if the default parameter has some error then it should not stop as the order is getting imported from external sites
                raise osv.except_osv(_('Error'), _('Customer UPS settings not defined'))
            else:
                ship_ups_id = ship_ups_id[0]
            return self.browse(cr, uid, ship_ups_id)
    
    
shipping_ups()

