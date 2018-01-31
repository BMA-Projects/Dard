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
from openerp.osv import fields, osv
import urllib
#import libxml2

import openerp.netsvc
# logger = openerp.netsvc.Logger()
from openerp.tools.translate import _
import datetime
from miscellaneous import Address
from fedex.config import FedexConfig
from fedex.services.address_validation_service import FedexAddressValidationRequest
import math
import  urllib2

# class sale_shop(osv.osv):
#     _name = "sale.shop"
#     _description = "Sales Shop"
#     _columns = {
#         'name': fields.char('Shop Name', size=64, required=True),
#         'payment_default_id': fields.many2one('account.payment.term', 'Default Payment Term', required=True),
#         'pricelist_id': fields.many2one('product.pricelist', 'Pricelist'),
#         'project_id': fields.many2one('account.analytic.account', 'Analytic Account', domain=[('parent_id', '!=', False)]),
#         'company_id': fields.many2one('res.company', 'Company', required=False),
#     }
#     _defaults = {
#         'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'sale.shop', context=c),
#     }
# 
# sale_shop()

def get_partner_details(firm_name, partneradd_lnk, context=None):
        result = {}
        if partneradd_lnk:
            result['name'] = partneradd_lnk.name
            result['firm'] = firm_name or partneradd_lnk.name
            result['add1'] = partneradd_lnk.street or ''
            result['add2'] = partneradd_lnk.street2 or ''
            result['city'] = partneradd_lnk.city or ''
            result['state_code'] = partneradd_lnk.state_id.code or ''
            result['zip5'] = ''
            result['zip4'] = ''
            if len(partneradd_lnk.zip.strip()) == 5:
                result['zip5'] = partneradd_lnk.zip
                result['zip4'] = ''
            elif len(partneradd_lnk.zip.strip()) == 4:
                result['zip4'] = partneradd_lnk.zip
                result['zip5'] = ''
            elif str(partneradd_lnk.zip).find('-'):
                zips = str(partneradd_lnk.zip).split('-')
                if len(zips[0]) == 5 and len(zips[1]) == 4:
                    result['zip5'] = zips[0]
                    result['zip4'] = zips[1]
                elif len(zips[0]) == 4 and len(zips[1]) == 5:
                    result['zip4'] = zips[0]
                    result['zip5'] = zips[1]
            else:
                result['zip4'] = result['zip5'] = ''
                
            result['email'] = partneradd_lnk.email or ''
            result['country_code'] = partneradd_lnk.country_id.code or ''
            result['phone'] = partneradd_lnk.phone or ''
        return result



class sale_order(osv.osv):
    _inherit = "sale.order"

    def ups_check_address_validate(self, cr, uid, ids, context=None):
        ## checking weather patner address valid or not
        partneraddr_obj = self.pool.get('res.partner')
        shippingups_obj = self.pool.get('shipping.ups')
        status = None
        shippingups_id = shippingups_obj.search(cr,uid,[('active','=',True)])
        for line in self.browse(cr, uid, ids):
            partner_id =line.partner_shipping_id.id
            
            if not shippingups_id:
                line.invalid_addr = True
            else:
                shippingups_id = shippingups_id[0]
     
                shippingups_ptr = shippingups_obj.browse(cr,uid,shippingups_id)
                access_license_no = shippingups_ptr.access_license_no
                user_id = shippingups_ptr.user_id
                password = shippingups_ptr.password
                shipper_no = shippingups_ptr.shipper_no
     
                ### Get Address from sale order
                 
                street = partneraddr_obj.browse(cr, uid, partner_id).street or ''
     
                street2 = partneraddr_obj.browse(cr, uid, partner_id).street2 or ''
     
                city = partneraddr_obj.browse(cr,uid,partner_id).city or ''
     
                state_code = partneraddr_obj.browse(cr, uid, partner_id).state_id.code or ''
     
                country_code = partneraddr_obj.browse(cr, uid, partner_id).country_id.code or ''
     
                postal_code = partneraddr_obj.browse(cr, uid, partner_id).zip or ''
              
                data = """<?xml version=\"1.0\"?>
        <AccessRequest xml:lang=\"en-US\">
            <AccessLicenseNumber>%s</AccessLicenseNumber>
            <UserId>%s</UserId>
            <Password>%s</Password>
        </AccessRequest>
        <?xml version="1.0"?>
        <AddressValidationRequest xml:lang="en-US">
           <Request>
              <TransactionReference>
                 <CustomerContext>Customer Data</CustomerContext>
                 <XpciVersion>1.0001</XpciVersion>
              </TransactionReference>
              <RequestAction>AV</RequestAction>
           </Request>
           <Address>
              <City>%s</City>
              <StateProvinceCode>%s</StateProvinceCode>
              <CountryCode>%s</CountryCode>
              <PostalCode>%s</PostalCode>
           </Address>
        </AddressValidationRequest>
        """ % (access_license_no,user_id,password,city,state_code,country_code,postal_code)
     
                if shippingups_ptr.test:
                    api_url = 'https://wwwcie.ups.com/ups.app/xml/AV'
                else:
                    api_url = 'https://onlinetools.ups.com/ups.app/xml/AV'
     
                try:
                    webf = urllib.urlopen(api_url, data)
                    response = webf.read()
     
                    sIndex = response.find('<ResponseStatusDescription>')
                    eIndex = response.find('</ResponseStatusDescription>')
                    status = response[sIndex+27:eIndex]
     
                    if status != 'Success':
                        line.invalid_addr = True
                         
                    else:
                        sIndex = eIndex = i = 0
     
                        sIndex = response.find('<City>',i)
                        eIndex = response.find('</City>',i)
                        city_resp = response[sIndex+6:eIndex]
                        i = eIndex + 7
     
                        sIndex = response.find('<StateProvinceCode>',i)
                        eIndex = response.find('</StateProvinceCode>',i)
                        state_code_resp = response[sIndex+19:eIndex]
                        i = eIndex + 20
     
                        sIndex = response.find('<PostalCodeLowEnd>',i)
                        eIndex = response.find('</PostalCodeLowEnd>',i)
                        postal_code_lowend_resp = response[sIndex+18:eIndex]
                        i = eIndex + 19
     
                        sIndex = response.find('<PostalCodeHighEnd>',i)
                        eIndex = response.find('</PostalCodeHighEnd>',i)
                        postal_code_highend_resp = response[sIndex+19:eIndex]
                        i = eIndex + 20
     
                        line.invalid_addr = True
                        while (sIndex != -1):
                            if city.upper() == city_resp and state_code.upper() == state_code_resp and (int(postal_code) >= int(postal_code_lowend_resp) and int(postal_code) <= int(postal_code_highend_resp)):
                                line.invalid_addr = True
                                break
     
                            sIndex = response.find('<City>',i)
                            if sIndex == -1:
                                break
                            eIndex = response.find('</City>',i)
                            city_resp = response[sIndex+6:eIndex]
     
                            sIndex = response.find('<StateProvinceCode>',i)
                            eIndex = response.find('</StateProvinceCode>',i)
                            state_code_resp = response[sIndex+19:eIndex]
     
                            sIndex = response.find('<PostalCodeLowEnd>',i)
                            eIndex = response.find('</PostalCodeLowEnd>',i)
                            postal_code_lowend_resp = response[sIndex+18:eIndex]
     
                            sIndex = response.find('<PostalCodeHighEnd>',i)
                            eIndex = response.find('</PostalCodeHighEnd>',i)
                            postal_code_highend_resp = response[sIndex+19:eIndex]
                            i = eIndex + 20
                except:
                    line.invalid_addr = False
                    pass
     
            if status != 'Success':
                self.write(cr, uid, line.id, {'is_test':False,'valid_note':'Address is InValid'}, context)
                cr.commit()
                raise osv.except_osv(_('Error'), _('Invalid address, Please fill correct shipping address'))
            line.is_test = True
            self.write(cr, uid, line.id, {'is_test':True,'valid_note':'Address is Valid'}, context)
            return True
        
        
    ## checking Fedex Address validation both shipper and receipient ...............
    def fedex_address_validation(self, cr, uid, ids, context=None):
            partneraddr_obj = self.pool.get('res.partner')
            shippingfedex_obj = self.pool.get('shipping.fedex')
            status = None
            shippingfedex_id = shippingfedex_obj.search(cr, uid, [('active','=',True)])

            for sales_order in self.browse(cr, uid, ids):
                partner_id =sales_order.partner_shipping_id
                if not shippingfedex_id:
                    raise osv.except_osv(_('Error'), _('Default Fedex settings not defined'))
                else:
                    shippingfedex_id = shippingfedex_id[0]
                    
                shippingfedex_ptr = shippingfedex_obj.browse(cr, uid, shippingfedex_id)
                account_no = shippingfedex_ptr.account_no
                key = shippingfedex_ptr.key
                password = shippingfedex_ptr.password
                meter_no = shippingfedex_ptr.meter_no
                is_test = shippingfedex_ptr.test
                
                CONFIG_OBJ = FedexConfig(key=key, password=password, account_number=account_no, meter_number=meter_no, use_test_server=is_test)
                connection = FedexAddressValidationRequest(CONFIG_OBJ)
                
                # The AddressValidationOptions are created with default values of None, which
                # will cause WSDL validation errors. To make things work, each option needs to
                # be explicitly set or deleted.
                
                ### Get Address from sale order
                
                cust_name = partner_id.name or ''
                cust_id = partner_id.id or ''  
                   
                street = partner_id.street or ''
     
                street2 = partner_id.street2 or ''
     
                city = partner_id.city or ''
     
                postal_code = partner_id.zip or ''
                
                phone = partner_id.phone or ''
                
                email = partner_id.email or ''
                
                receipient = Address(cust_name or cust_id, street, city, partner_id.state_id.code or '', postal_code, partner_id.country_id.code, street2 or '', phone or '', email or '', partner_id.company_id.name or '')
                
                ## Set the flags we want to True (or a value).
                connection.RequestTimestamp = datetime.datetime.now().isoformat()
                #connection.AddressValidationOptions.CheckResidentialStatus = True
                #connection.AddressValidationOptions.VerifyAddresses = True
                #connection.AddressValidationOptions.RecognizeAlternateCityNames = True
                #connection.AddressValidationOptions.MaximumNumberOfMatches = 3
                
                ## Delete the flags we don't want.
                #del connection.AddressValidationOptions.ConvertToUpperCase
                #del connection.AddressValidationOptions.ReturnParsedElements
                
                ## *Accuracy fields can be TIGHT, EXACT, MEDIUM, or LOOSE. Or deleted.
                #connection.AddressValidationOptions.StreetAccuracy = 'LOOSE'
                #del connection.AddressValidationOptions.DirectionalAccuracy
                #del connection.AddressValidationOptions.CompanyNameAccuracy
                
                ## Create some addresses to validate
                ### Shipper
                cust_address = sales_order.company_id
                if not cust_address:
                    raise osv.except_osv(_('Error'), _('Shop Address not defined!'),)

                shipper = Address(cust_address.name or cust_address.id , cust_address.street, cust_address.city, cust_address.state_id.code or '', cust_address.zip, cust_address.country_id.code, cust_address.street2 or '', cust_address.phone or '', cust_address.email, cust_address.name)
                
                
                source_address = connection.create_wsdl_object_of_type('AddressToValidate')
                source_address.Address.StreetLines = shipper.address1  # ['320 S Cedros', '#200']
                source_address.Address.City = shipper.city  # 'Solana Beach'
                source_address.Address.StateOrProvinceCode = shipper.state_code  # 'CA'
                source_address.Address.PostalCode = shipper.zip  # 92075
                source_address.Address.CountryCode = shipper.country_code  # 'US'
                connection.add_address(source_address)

		sale_order_destination_address = connection.create_wsdl_object_of_type('AddressToValidate')
                #sale_order_destination_address.CompanyName = receipient.company_name
                sale_order_destination_address.Address.StreetLines = receipient.address1 #['155 Old Greenville Hwy', 'Suite 103']
                sale_order_destination_address.Address.City = receipient.city #'Clemson'
                sale_order_destination_address.Address.StateOrProvinceCode = receipient.state_code #'SC'
                sale_order_destination_address.Address.PostalCode = receipient.zip #29631
                sale_order_destination_address.Address.CountryCode = receipient.country_code #'US'
                sale_order_destination_address.Address.Residential = False
                connection.add_address(sale_order_destination_address)

                try:
                    ## Send the request and print the response
                    connection.send_request()
                    sales_order.is_test = True
                    self.write(cr, uid, ids, {'is_test':True,'valid_note':'Address is Valid'}, context)
                    cr.commit()
                except Exception, e:
                    sales_order.invalid_addr = False
                    self.write(cr, uid, ids, {'is_test':False,'valid_note':'Address is InValid'}, context)
                    cr.commit()
                    raise osv.except_osv(_('Error'), _('Invalid address, Please fill correct shipping address'))
		results = len(connection.response.AddressResults)
		#print results
            return True        
        
    ## USPS Address validation checking before sale order confirmed .......................    
    def usps_address_validation(self, cr, uid, ids, context=None):
        shippingusps_obj = self.pool.get('shipping.usps')
        status = None
        for line in self.browse(cr, uid, ids, context):
            partner_lnk = line.partner_shipping_id
            address = self.pool.get('res.partner').address_get(cr,uid,[partner_lnk.id])
            partneradd_lnk = self.pool.get('res.partner').browse(cr,uid,address['default'])
            result_to = get_partner_details(partner_lnk.name,partneradd_lnk,context)
#             result_from = get_partner_details(line.shop_id.name,line.shop_id.cust_address,context)
            shippingusps_id = shippingusps_obj.search(cr, uid, [('active','=',True)])
            if not shippingusps_id:
                raise osv.except_osv(_('Error'), _('Default USPS settings not defined'))
            else:
                shippingusps_id = shippingusps_id[0]
            shippingusps_ptr = shippingusps_obj.browse(cr, uid, shippingusps_id)
            user_id = shippingusps_ptr.user_id
            values = {}
            ## address validation API for USPS ............................
            url = "http://production.shippingapis.com/ShippingAPITest.dll?API=Verify&"
            values['XML']='<AddressValidateRequest USERID="'+ user_id +'"><Address><Address1>' +result_to['add1']+ '</Address1><Address2>' +result_to['add2']+' </Address2><City>' + result_to['city'] + '</City><State>' + result_to['state_code'] + '</State><Zip5>' + result_to['zip5'] + '</Zip5><Zip4>' + result_to['zip4'] + '</Zip4></Address></AddressValidateRequest>' 
            url = url + urllib.urlencode(values)
            
            try:
                f = urllib2.urlopen(url)
                response = f.read()
            except Exception, e:
                raise osv.except_osv(_('Error'), _('%s' % (e)))
            
            if response.find('<Error>') != -1:
                line.invalid_addr = False
                self.write(cr, uid, ids, {'is_test':False,'valid_note':'Address is InValid'}, context)
                cr.commit()
                raise osv.except_osv(_('Error'), _('Invalid address, Please fill correct shipping address'))
            else:
                line.is_test = True
                self.write(cr, uid, ids, {'is_test':True,'valid_note':'Address is Valid'}, context)
        return True
        
        
    ## check address validation according to shipping type.................... 
    def check_address_validate(self, cr, uid, ids, context=None):
        
        ## Object of stock config settings use shipping type configuration for address validation............
        stk_config_obj = self.pool.get('stock.config.settings')
        ## call default get for taking default values ...........
        values = stk_config_obj.default_get(cr, uid, ['shipping_type'], context=context)
        if values['shipping_type'] == 'USPS':
            self.usps_address_validation(cr, uid, ids, context)
        elif values['shipping_type'] == 'Fedex':
            self.fedex_address_validation(cr, uid, ids, context)
        elif values['shipping_type'] == 'UPS':
            self.ups_check_address_validate(cr, uid, ids, context)
        else:
            raise osv.except_osv(_('Warning'), _('Please configure the shipping type '))
        return True    
        
        
        
    def action_button_confirm(self, cr, uid, ids, context=None):
        id = super(sale_order, self).action_button_confirm(cr, uid, ids, context)
        for line in self.browse(cr, uid, ids):
            if line.is_test == False:
                raise osv.except_osv(_('Error'), _('Please Check address valid or invalid'))
        return id

    def _default_journal(self, cr, uid, context={}):
        accountjournal_obj = self.pool.get('account.journal')
        accountjournal_ids = accountjournal_obj.search(cr,uid,[('name','=','Sales Journal')])
        if accountjournal_ids:
            return accountjournal_ids[0]
        else:
#            raise wizard.except_wizard(_('Error !'), _('Sales journal not defined.'))
            return False

    _columns = {
        'invalid_addr': fields.boolean('Invalid Address',readonly=True),
        'client_order_ref': fields.char('Tracking Number', size=64),
        'journal_id': fields.many2one('account.journal', 'Journal',readonly=True),
        'is_test':fields.boolean('is test'),
        'valid_note':fields.text('Status', readonly=True),
        'is_ship_customer_account':fields.boolean("Ship Using Customer A/C"),
        'carrier_id': fields.many2one(
            "delivery.carrier", string="Ship Using Company Account",
            help="Complete this field if you plan to invoice the shipping based on picking."),
    }

    _defaults = {
        'journal_id': _default_journal,
    }
    
    ## for Null the label and is_test field...
    def onchang_label(self, cr, uid, ids, shipping_id, context=None):
        
        if shipping_id and ids:
            self.write(cr, uid, ids, {'is_test':False,'valid_note':False},context)
            return {'value': {'is_test': False, 'valid_note':False}}
        return {'value': {}}
            
sale_order()

# class sale_shop(osv.osv):
#     
#     _inherit = "sale.shop"
#     _columns = {
#                 'suffix': fields.char('Suffix', size=64),
#                 'cust_address': fields.many2one('res.partner', 'Address'),
#                 }
# 
# sale_shop()
