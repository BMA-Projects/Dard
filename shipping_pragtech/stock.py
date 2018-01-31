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
import urllib2
import urllib
from base64 import b64decode
import binascii
import openerp.addons.decimal_precision as dp
from datetime import date
import datetime
import time
import webbrowser
import HTMLParser
h = HTMLParser.HTMLParser()
import httplib
from openerp import api
import shippingservice
from miscellaneous import Address

from .xml_dict import dict_to_xml, xml_to_dict

from fedex.services.rate_service import FedexRateServiceRequest
from fedex.services.ship_service import FedexProcessShipmentRequest
from fedex.config import FedexConfig
import suds
from suds.client import Client
import openerp
from openerp.tools.translate import _
from openerp import  netsvc

# logger = openerp.netsvc.Logger()
import math
import socket
import urllib2
import Image

import logging 
from fedex.services.address_validation_service import FedexAddressValidationRequest 

class pack_weight(osv.osv):
    _name = 'pack.weight'
    _rec_name = 'pack'
    
    _columns = {
                  'pack':fields.char('Pack', size=100),
                  'weight' : fields.float('Weight', required=True),
                  'picking_id' : fields.many2one('stock.picking','Picking'),
                  'sequence':fields.integer('Sr.No.'),
                  'carrier_id':fields.many2one('delivery.carrier', 'Carrier'),
                  'carrier_tracking_ref':fields.char('Carrier Tracking Ref.', size=250),
                  'product_ul_line': fields.many2one("product.ul", "Package Dimensions Line"),
                }
    _defaults = {
                    'pack':'Pack-'+str(1),
                    'sequence':1,
                 
                 }
    _order = "sequence"
    
    ## check weather alrady active record exists or not ..........
    def _check_weight(self, cr, uid, ids, context=None):
        
        record_id = self.search(cr, uid, [('id','=',ids[0])])
        for line in self.browse(cr, uid, record_id):
            if line.weight != 0.0:
                return True
        return False
       
    _constraints = [
        (_check_weight, 'Please Give the Package Weight', ['weight']),
    ]
     
    ## for getting dynamically sequence and packing........
    def default_get(self,cr, uid, fields_list, context=None):
        ## set packing sequence default ...................
        data = super(pack_weight,self).default_get(cr, uid, fields_list, context=context)
        l = []
        nxt_seq = False
        if 'pack_weight_ids' in context:
            nxt_seq = len(context['pack_weight_ids'])
        if 'pack_weight_ids' in context:
            for line_id in context['pack_weight_ids']:
                if line_id[2] != False:
                    l.append(line_id[2]['sequence'])
        if nxt_seq:
            l.append(nxt_seq)       
        data['sequence'] = max(l)+1 if l else 1
        data['pack'] = "Pack-"+str(data['sequence'])
        return data
    
    
    ## restricted to delete tracking generated line .........
    def unlink(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if line.carrier_tracking_ref: 
                raise osv.except_osv(_('Error!'), _('You cannot delete a line with generated tracking refernce'))
        return super(pack_weight, self).unlink(cr, uid, ids, context=context)
    
pack_weight()


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

class shipping_response(osv.osv):
    _name = 'shipping.response'

    def generate_tracking_no(self, cr, uid, ids, context={}, error=True):

        def get_usps_servicename(service):
            if 'First-Class' in service:
                return 'First Class'
            elif 'Express Mail' in service:
                return 'Express Mail'
            elif 'Priority Mail' in service:
                return 'Priority'
            elif 'Library Mail' in service:
                return 'Library Mail'
            elif 'Parcel Post' in service:
                return 'Parcel Post'
            elif 'Media Mail' in service:
                return 'Media Mail'
            
#         logger.notifyChannel('init', netsvc.LOG_WARNING, 'generate_tracking_no called')
        saleorder_obj = self.pool.get('sale.order')
        stockmove_obj = self.pool.get('stock.move')
        stockpicking_obj = self.pool.get('stock.picking')
        pack_weight_obj = self.pool.get('pack.weight')
        attachment_pool = self.pool.get('ir.attachment')
        shippingresp_lnk = self.browse(cr,uid,ids[0])
        move_ids = stockmove_obj.search(cr,uid,[('picking_id','=',shippingresp_lnk.picking_id.id)])
        ## check is_label generated or not .......................
        ship_response_ids = self.search(cr,uid,[('picking_id','=',shippingresp_lnk.picking_id.id)])
        current_seq = shippingresp_lnk.sequence
        for line in self.browse(cr, uid, ship_response_ids):
            if line.sequence == current_seq and line.is_label_genrated == True:
                raise osv.except_osv(_('Error'), _('You can not generate another label of same sequence'))
        
        move_lines = stockmove_obj.browse(cr, uid, move_ids)
        for move_line in move_lines:
            move_line.product_id.qty_available
#             self.pool.get('stock.location')._product_reserve(cr, uid, [move_line.location_id.id], move_line.product_id.id, move_line.product_qty, {'uom': move_line.product_uom.id}, lock=True)
        partneradd_lnk = shippingresp_lnk.picking_id.sale_id.company_id
        if not partneradd_lnk:
            raise osv.except_osv(_('Error'), _('Company Address not defined!'),)
        result_from = get_partner_details(shippingresp_lnk.picking_id.sale_id.company_id.name,partneradd_lnk,context)

        partner_lnk = shippingresp_lnk.picking_id.partner_id
        address = self.pool.get('res.partner').address_get(cr,uid,[partner_lnk.id])
        partneradd_lnk = self.pool.get('res.partner').browse(cr,uid,address['default'])
        result_to = get_partner_details(partner_lnk.name,partneradd_lnk,context)
        ### Shipper
        cust_address = shippingresp_lnk.picking_id.sale_id.company_id
        if not cust_address:
            if error:
                raise osv.except_osv(_('Error'), _('Company Address not defined!'),)
            else:
                return False
        #shipper = Address(cust_address.name or cust_address.partner_id.name, cust_address.street, cust_address.city, cust_address.state_id.code or '', cust_address.zip, cust_address.country_id.code, cust_address.street2 or '', cust_address.phone or '', cust_address.email, cust_address.partner_id.name)
        shipper = Address(cust_address.name or cust_address.id , cust_address.street, cust_address.city, cust_address.state_id.code or '', cust_address.zip, cust_address.country_id.code, cust_address.street2 or '', cust_address.phone or '', cust_address.email, cust_address.name)

        ### Recipient
        cust_address = shippingresp_lnk.picking_id.partner_id
        #receipient = Address(cust_address.name or cust_address.partner_id.name, cust_address.street, cust_address.city, cust_address.state_id.code or '', cust_address.zip, cust_address.country_id.code, cust_address.street2 or '', cust_address.phone or '', cust_address.email, cust_address.partner_id.name)
        receipient = Address(cust_address.name or cust_address.id, cust_address.street, cust_address.city, cust_address.state_id.code or '', cust_address.zip, cust_address.country_id.code, cust_address.street2 or '', cust_address.phone or '', cust_address.email, cust_address.name, cust_address.company_id.name or '')
        weight = shippingresp_lnk.weight
        rate = shippingresp_lnk.rate
        tracking_no = False
        
        if shippingresp_lnk.type.lower() == 'usps': #and ('usps_active' in context.keys() and context.get('usps_active')):

            shippingusps_obj = self.pool.get('shipping.usps')
            shippingusps_id = shippingusps_obj.search(cr, uid, [('active','=',True)])
            if not shippingusps_id:
                if error:
                    raise osv.except_osv(_('Error'), _('Default USPS settings not defined'))
                return False
            else:
                shippingusps_id = shippingusps_id[0]
            shippingusps_ptr = shippingusps_obj.browse(cr, uid, shippingusps_id)
            user_id = shippingusps_ptr.user_id
            
            url = url = "https://secure.shippingapis.com/ShippingAPI.dll?API=DelivConfirmCertifyV4&" if shippingusps_ptr.test else "https://Secure.shippingapis.com/ShippingAPI.dll?API=DelivConfirmCertifyV4&"
            weight = math.modf(weight)
            pounds = int(weight[1])
            ounces = round(weight[0],4) * 16
            pounds*16 + ounces
            service_type = get_usps_servicename(shippingresp_lnk.name)
            values = {}
            values['XML'] = '<DelivConfirmCertifyV4.0Request USERID="'+ user_id +'"><Option>1</Option><ImageParameters></ImageParameters><FromName>' + result_from['name'] + '</FromName><FromFirm>' + result_from['firm'] + '</FromFirm><FromAddress1>' + result_from['add2'] + '</FromAddress1><FromAddress2>' + result_from['add1'] + '</FromAddress2><FromCity>' + result_from['city'] + '</FromCity><FromState>' + result_from['state_code'] + '</FromState><FromZip5>' + result_from['zip5'] + '</FromZip5><FromZip4>' + result_from['zip4'] + '</FromZip4><ToName>' + result_to['name'] + '</ToName><ToFirm>' + result_to['firm'] + '</ToFirm><ToAddress1>' + result_to['add2'] + '</ToAddress1><ToAddress2>' + result_to['add1'] + '</ToAddress2><ToCity>' + result_to['city'] + '</ToCity><ToState>' + result_to['state_code'] + '</ToState><ToZip5>' + result_to['zip5'] + '</ToZip5><ToZip4>' + result_to['zip4'] + '</ToZip4><WeightInOunces>' + '10' + '</WeightInOunces><ServiceType>' + service_type + '</ServiceType><SeparateReceiptPage>TRUE</SeparateReceiptPage><POZipCode></POZipCode><ImageType>TIF</ImageType><LabelDate></LabelDate><CustomerRefNo></CustomerRefNo><AddressServiceRequested></AddressServiceRequested><SenderName></SenderName><SenderEMail></SenderEMail><RecipientName></RecipientName><RecipientEMail></RecipientEMail></DelivConfirmCertifyV4.0Request>'
            url = url + urllib.urlencode(values)
            
            try:
                f = urllib2.urlopen(url)
                response = f.read()
            except Exception, e:
                if error:
                    raise osv.except_osv(_('Error'), _('%s' % (e)))
                return False
            
            if response.find('<Error>') != -1:
                sIndex = response.find('<Description>')
                eIndex = response.find('</Description>')
                if error:
                    raise osv.except_osv(_('Error'), _('%s') % (response[int(sIndex)+13:int(eIndex)],))
                return False

            i = sIndex = eIndex = 0
            sIndex = response.find('<DeliveryConfirmationNumber>',i)
            eIndex = response.find('</DeliveryConfirmationNumber>',i)
            tracking_no = response[int(sIndex) + 36:int(eIndex)]

            sIndex = response.find('<DeliveryConfirmationLabel>',i)
            eIndex = response.find('</DeliveryConfirmationLabel>',i)
            s_label = str(response[int(sIndex) + 27:int(eIndex)])
            

            """filename = "Label1.tif"
            FILE = open(filename,"w")
            FILE.write(b64decode(s_label))"""
            data_attach = {
                'name': 'PackingList.tif',
                'datas_fname':shippingresp_lnk.picking_id.sale_id.name +'.tif',
                'datas': binascii.b2a_base64(str(b64decode(s_label))),
                'description': 'Packing List',
                'res_name': shippingresp_lnk.picking_id.name,
                'res_model': 'stock.picking',
                'res_id': shippingresp_lnk.picking_id.id,
            }
            attach_id = attachment_pool.create(cr, uid, data_attach)
            write_val={}
            write_val['fedex_attach_id']=0
            write_val['ups_attach_id']=0
            write_val['usps_attach_id']=attach_id
            self.write(cr, uid, ids, write_val, context)
            context['attach_id'] = attach_id
            
            ## usps tracking number ..................
            if tracking_no:
                stockpicking_obj.write(cr,uid,shippingresp_lnk.picking_id.id,{'carrier_tracking_ref':tracking_no, 'shipping_label':binascii.b2a_base64(str(b64decode(s_label))), 'shipping_rate': rate})
                context['track_success'] = True
                context['tracking_no']=tracking_no
                self.write(cr, uid, ids, {'is_label_genrated':True},context)  
                ## carrier_id and tracking reference write in pack_weight object .....
                pack_id = pack_weight_obj.search(cr, uid, [('picking_id','=',shippingresp_lnk.picking_id.id),('sequence','=',shippingresp_lnk.sequence)])
                if pack_id:
                    pack_weight_obj.write(cr, uid, pack_id, {'carrier_tracking_ref':tracking_no}, context)
                
        
        elif shippingresp_lnk.type.lower() == 'fedex':
            #raise osv.except_osv(_('Error'), _('FedEx shipment request under construction'))
            shippingfedex_id = None
            picking_record = stockpicking_obj.browse(cr, uid, shippingresp_lnk.picking_id.id)
            
            shippingfedex_obj = self.pool.get('shipping.fedex')
            if not picking_record.is_customer_account:
                shippingfedex_id = shippingfedex_obj.search(cr, uid, [('active','=',True)])
                if not shippingfedex_id:
                    raise osv.except_osv(_('Error'), _('Default Fedex settings not defined'))
                else:
                    shippingfedex_id = shippingfedex_id[0]
            else:
                if not shippingresp_lnk.picking_id.fedex_id:
                    raise osv.except_osv('Warning', 'Please Enter Account Details')
                shippingfedex_id = shippingfedex_obj.search(cr, uid, [('partner_id','=',picking_record.partner_id.id),('country_id','=',picking_record.partner_id.country_id.id),('active','=',True)])
                shippingfedex_id = shippingfedex_id[0]
                  
            shippingfedex_ptr = shippingfedex_obj.browse(cr, uid, shippingfedex_id)
            account_no = shippingfedex_ptr.account_no
            key = shippingfedex_ptr.key
            password = shippingfedex_ptr.password
            meter_no = shippingfedex_ptr.meter_no
            is_test = shippingfedex_ptr.test
            CONFIG_OBJ = FedexConfig(key=key, password=password, account_number=account_no, meter_number=meter_no, use_test_server=is_test)
            # This is the object that will be handling our tracking request.
            # We're using the FedexConfig object from example_config.py in this dir.
            shipment = FedexProcessShipmentRequest(CONFIG_OBJ)
            # This is very generalized, top-level information.
            # REGULAR_PICKUP, REQUEST_COURIER, DROP_BOX, BUSINESS_SERVICE_CENTER or STATION
            fedex_servicedetails = stockpicking_obj.browse(cr,uid,shippingresp_lnk.picking_id.id)
            
            shipment.RequestedShipment.DropoffType = fedex_servicedetails.dropoff_type_fedex #'REGULAR_PICKUP'
            # See page 355 in WS_ShipService.pdf for a full list. Here are the common ones:
            # STANDARD_OVERNIGHT, PRIORITY_OVERNIGHT, FEDEX_GROUND, FEDEX_EXPRESS_SAVER
            shipment.RequestedShipment.ServiceType = fedex_servicedetails.service_type_fedex #'PRIORITY_OVERNIGHT'

            # What kind of package this will be shipped in.
            # FEDEX_BOX, FEDEX_PAK, FEDEX_TUBE, YOUR_PACKAGING
            shipment.RequestedShipment.PackagingType = fedex_servicedetails.packaging_type_fedex  #'FEDEX_PAK'

            # No idea what this is.
            # INDIVIDUAL_PACKAGES, PACKAGE_GROUPS, PACKAGE_SUMMARY
#             shipment.RequestedShipment.PackageDetail = fedex_servicedetails.package_detail_fedex #'INDIVIDUAL_PACKAGES'

#             # Shipper contact info.
            shipment.RequestedShipment.Shipper.Contact.PersonName = shipper.name #'Sender Name'
            shipment.RequestedShipment.Shipper.Contact.CompanyName = shipper.company_name #'Some Company'
            shipment.RequestedShipment.Shipper.Contact.PhoneNumber = shipper.phone or ''#'9012638716'
            #shipment.RequestedShipment.Shipper.Contact.PhoneNumber ='9012638716'
#              
#             # Shipper address.
            shipment.RequestedShipment.Shipper.Address.StreetLines = shipper.address1 #['Address Line 1']
            shipment.RequestedShipment.Shipper.Address.City =  shipper.city #'Herndon'
            shipment.RequestedShipment.Shipper.Address.StateOrProvinceCode = shipper.state_code #'VA'
            shipment.RequestedShipment.Shipper.Address.PostalCode = shipper.zip #'20171'
            shipment.RequestedShipment.Shipper.Address.CountryCode = shipper.country_code #'US'
            shipment.RequestedShipment.Shipper.Address.Residential = False
           
            

#             # Recipient contact info.
            shipment.RequestedShipment.Recipient.Contact.PersonName = receipient.name #'Recipient Name'
            shipment.RequestedShipment.Recipient.Contact.CompanyName = receipient.company_name #'Recipient Company'
            shipment.RequestedShipment.Recipient.Contact.PhoneNumber = receipient.phone or ''#'9012637906'
            #shipment.RequestedShipment.Recipient.Contact.PhoneNumber ='9012637906'
#                 
# 
# 
#             # Recipient address
            shipment.RequestedShipment.Recipient.Address.StreetLines = receipient.address1 #['Address Line 1']
            shipment.RequestedShipment.Recipient.Address.City = receipient.city #'Herndon'
            shipment.RequestedShipment.Recipient.Address.StateOrProvinceCode = receipient.state_code #'VA'
            shipment.RequestedShipment.Recipient.Address.PostalCode = receipient.zip #'20171'
            shipment.RequestedShipment.Recipient.Address.CountryCode = receipient.country_code #'US'
            # This is needed to ensure an accurate rate quote with the response.
            # This is needed to ensure an accurate rate quote with the response.
            if fedex_servicedetails.service_type_fedex == 'GROUND_HOME_DELIVERY':
                shipment.RequestedShipment.Recipient.Address.Residential = True
            shipment.RequestedShipment.EdtRequestType = 'NONE'
            shipment.RequestedShipment.ShippingChargesPayment.Payor.ResponsibleParty.AccountNumber = CONFIG_OBJ.account_number

            
            
            logging.basicConfig(level=logging.INFO)
#             connection = FedexAddressValidationRequest(CONFIG_OBJ)
# 
#             connection.AddressValidationOptions.CheckResidentialStatus = True
#             connection.AddressValidationOptions.VerifyAddresses = True
#             connection.AddressValidationOptions.RecognizeAlternateCityNames = True
#             connection.AddressValidationOptions.MaximumNumberOfMatches = 3
#     
#             connection.AddressValidationOptions.StreetAccuracy = 'LOOSE'
#             
#             del connection.AddressValidationOptions.DirectionalAccuracy 
#             del connection.AddressValidationOptions.CompanyNameAccuracy 
#             
#             address1 = connection.create_wsdl_object_of_type('AddressToValidate')
#             address1.CompanyName = receipient.company_name
#             #address1.Address.StreetLines = ['155 Old Greenville Hwy', 'Suite 103']
#             address1.Address.StreetLines = receipient.address1
#             address1.Address.City = receipient.city
#             address1.Address.StateOrProvinceCode = receipient.state_code
#             address1.Address.PostalCode = receipient.zip
#             address1.Address.CountryCode = receipient.country_code
#             address1.Address.Residential = False
#             connection.add_address(address1)
     
            ## Send the request and print the response
#             try:
#                 connection.send_request()
#             except Exception, e:
#                 raise osv.except_osv(_('Error'), _('%s' % (e,)))
#             
            # Who pays for the shipment?
            # RECIPIENT, SENDER or THIRD_PARTY
            shipment.RequestedShipment.ShippingChargesPayment.PaymentType = fedex_servicedetails.payment_type_fedex #'SENDER'

            # Specifies the label type to be returned.
            # LABEL_DATA_ONLY or COMMON2D
            shipment.RequestedShipment.LabelSpecification.LabelFormatType = 'COMMON2D'

            # Specifies which format the label file will be sent to you in.
            # DPL, EPL2, PDF, PNG, ZPLII
            shipment.RequestedShipment.LabelSpecification.ImageType = 'PNG'

            # To use doctab stocks, you must change ImageType above to one of the
            # label printer formats (ZPLII, EPL2, DPL).
            # See documentation for paper types, there quite a few.
            shipment.RequestedShipment.LabelSpecification.LabelStockType = 'PAPER_4X6'

            # This indicates if the top or bottom of the label comes out of the
            # printer first.
            # BOTTOM_EDGE_OF_TEXT_FIRST or TOP_EDGE_OF_TEXT_FIRST
            shipment.RequestedShipment.LabelSpecification.LabelPrintingOrientation = 'BOTTOM_EDGE_OF_TEXT_FIRST'

            package1_weight = shipment.create_wsdl_object_of_type('Weight')
            # Weight, in pounds.
            package1_weight.Value = fedex_servicedetails.weight_package #1.0
            package1_weight.Units = "LB"

            package1 = shipment.create_wsdl_object_of_type('RequestedPackageLineItem')
            package1.PhysicalPackaging = fedex_servicedetails.physical_packaging_fedex
            package1.Dimensions.Length = fedex_servicedetails.package_length
            package1.Dimensions.Width = fedex_servicedetails.package_width
            package1.Dimensions.Height = fedex_servicedetails.package_height
            package1.Dimensions.Units = 'IN'
            package1.Weight = package1_weight
            package1.GroupPackageCount = 1
            # Un-comment this to see the other variables you may set on a package.

            # This adds the RequestedPackageLineItem WSDL object to the shipment. It
            # increments the package count and total weight of the shipment for you.
            
#             del shipment.RequestedShipment.EdtRequestType 
#             del package1.PhysicalPackaging 
            
            shipment.add_package(package1)

            # If you'd like to see some documentation on the ship service WSDL, un-comment
            # this line. (Spammy).
            # Un-comment this to see your complete, ready-to-send request as it stands
            # before it is actually sent. This is useful for seeing what values you can
            # change.

            # If you want to make sure that all of your entered details are valid, you
            # can call this and parse it just like you would via send_request(). If
            # shipment.response.HighestSeverity == "SUCCESS", your shipment is valid.
#             try:
#                 shipment.send_validation_request()
#             except Exception, e:
#                 raise osv.except_osv(_('Error'), _('%s' % (e,)))
#                      
            # Fires off the request, sets the 'response' attribute on the object.
            try:
                shipment.send_request()
            except Exception, e:
                if error:
                        errormessage= e
                        raise osv.except_osv(_('Error'), _('%s' % (errormessage,)))                
            
            # This will show the reply to your shipment being sent. You can access the
            # attributes through the response attribute on the request object. This is
            # good to un-comment to see the variables returned by the Fedex reply.
            
            # Here is the overall end result of the query.
            # Getting the tracking number from the new shipment.
            fedexTrackingNumber = shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].TrackingIds[0].TrackingNumber 
            # Net shipping costs.
            fedexshippingrate = 0.0
            if fedex_servicedetails.payment_type_fedex == 'SENDER':
                fedexshippingrate = shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].PackageRating.PackageRateDetails[0].NetCharge.Amount
            # Get the label image in ASCII format from the reply. Note the list indices
            # we're using. You'll need to adjust or iterate through these if your shipment
            # has multiple packages.
            ascii_label_data = shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].Label.Parts[0].Image
            # Convert the ASCII data to binary.
#            label_binary_data = binascii.a2b_base64(ascii_label_data)
            """
            #This is an example of how to dump a label to a PNG file.
            """
            # This will be the file we write the label out to.
#            png_file = open('example_shipment_label.png', 'wb')
#            png_file.write(b64decode(label_binary_data))
#            png_file.close()
            
            fedex_attachment_pool = self.pool.get('ir.attachment')
            fedex_data_attach = {
                'name': 'PackingList.png',
                'datas_fname':shippingresp_lnk.picking_id.sale_id.name +'.png',
                'datas': binascii.b2a_base64(str(b64decode(ascii_label_data))),
                'description': 'Packing List',
                'res_name': shippingresp_lnk.picking_id.name,
                'res_model': 'stock.picking',
                'res_id': shippingresp_lnk.picking_id.id,
            }
            
            fedex_attach_id = fedex_attachment_pool.create(cr, uid, fedex_data_attach)
                
            write_val={}
            write_val['fedex_attach_id']= fedex_attach_id
            write_val['ups_attach_id'] = 0
            write_val['usps_attach_id'] = 0
            self.write(cr, uid, ids, write_val, context)
                
            context['attach_id'] = fedex_attach_id
            context['tracking_no'] = fedexTrackingNumber
            """
            #This is an example of how to print the label to a serial printer. This will not
            #work for all label printers, consult your printer's documentation for more
            #details on what formats it can accept.
            """
            # Pipe the binary directly to the label printer. Works under Linux
            # without requiring PySerial. This WILL NOT work on other platforms.
            #label_printer = open("/dev/ttyS0", "w")
            #label_printer.write(label_binary_data)
            #label_printer.close()

            """
            #This is a potential cross-platform solution using pySerial. This has not been
            #tested in a long time and may or may not work. For Windows, Mac, and other
            #platforms, you may want to go this route.
            """
            ## fedex tracking number ............
            if fedexTrackingNumber:
                stockpicking_obj.write(cr,uid,shippingresp_lnk.picking_id.id,{'carrier_tracking_ref':fedexTrackingNumber, 'shipping_label':binascii.b2a_base64(str(b64decode(ascii_label_data))), 'shipping_rate': fedexshippingrate})
                context['track_success'] = True
                self.write(cr, uid, ids, {'is_label_genrated':True},context) 
                ## carrier id and tracking number write in pack.weight obj ..........
                pack_id = pack_weight_obj.search(cr, uid, [('picking_id','=',shippingresp_lnk.picking_id.id),('sequence','=',shippingresp_lnk.sequence)])
                if pack_id:
                    pack_weight_obj.write(cr, uid, pack_id, {'carrier_tracking_ref':fedexTrackingNumber}, context)

        elif shippingresp_lnk.type.lower() == 'ups':
            ups_info = None
            if not shippingresp_lnk.picking_id.is_customer_account:
                ups_info = self.pool.get('shipping.ups').get_ups_info(cr,uid,context)
            else:
                if not shippingresp_lnk.picking_id.ups_id:
                    raise osv.except_osv('Warning', 'Please Enter Account Details')
                ups_info = self.pool.get('shipping.ups').get_ups_partner_info(cr, uid, [shippingresp_lnk.picking_id.id], context)
            #stockpicking_obj = self.pool.get('stock.picking.out')#comment by anil
            pickup_type_ups = shippingresp_lnk.picking_id.pickup_type_ups
            service_type_ups = shippingresp_lnk.picking_id.service_type_ups
            packaging_type_ups = shippingresp_lnk.picking_id.packaging_type_ups
            ups = shippingservice.UPSShipmentConfirmRequest(ups_info, pickup_type_ups, service_type_ups, packaging_type_ups, weight, shipper, receipient)
            try:
                ups_response = ups.send()
            except Exception, e:
                if error:
                    errormessage = e
                    raise osv.except_osv(_('Error'), _('%s' % (errormessage,)))
                        
            ups = shippingservice.UPSShipmentAcceptRequest(ups_info, ups_response.shipment_digest)
            ups_response = ups.send()
            
            ups_attachment_id=stockpicking_obj.create_attachment(cr,uid,[shippingresp_lnk.picking_id.id],ups_response,context)
            context['attach_id'] = ups_attachment_id
            stockpicking_obj.write(cr,uid,shippingresp_lnk.picking_id.id,{'carrier_tracking_ref':ups_response.tracking_number, 'shipping_label':binascii.b2a_base64(str(b64decode(ups_response.graphic_image))), 'shipping_rate': rate})
            ## ups write tracking refernce and carreier id in pack.weight obj ....
            pack_id = pack_weight_obj.search(cr, uid, [('picking_id','=',shippingresp_lnk.picking_id.id),('sequence','=',shippingresp_lnk.sequence)])
            if pack_id:
                pack_weight_obj.write(cr, uid, pack_id, {'carrier_tracking_ref':ups_response.tracking_number}, context)
            context['track_success'] = True
            context['tracking_no'] = ups_response.tracking_number
            self.write(cr, uid, ids, {'is_label_genrated':True},context)
            write_val={}
            write_val['fedex_attach_id']=0
            write_val['usps_attach_id']=0
            if type(ups_attachment_id) == type([]):
                write_val['ups_attach_id']=ups_attachment_id[0]
            else:
                write_val['ups_attach_id']=ups_attachment_id
                
            self.pool.get('shipping.response').write(cr,uid,ids,write_val,context)
        
        ### Check Availability; Confirm; Validate : Automate Process Now step
        if context.get('track_success',False):
            ### Assign Carrier to Delivery carrier if user has not chosen
            type_fieldname = ''
            if shippingresp_lnk.type.lower() == 'usps':
                type_fieldname = 'is_usps'
            elif shippingresp_lnk.type.lower() == 'ups':
                type_fieldname = 'is_ups'
            elif shippingresp_lnk.type.lower() == 'fedex':
                type_fieldname = 'is_fedex'
            carrier_ids = self.pool.get('delivery.carrier').search(cr,uid,[(type_fieldname,'=',True)])
            if not carrier_ids:
                if error:
                    raise osv.except_osv(_('Error'), _('Shipping service output settings not defined'))
                return False
            self.pool.get('stock.picking').write(cr,uid,shippingresp_lnk.picking_id.id,{'carrier_id':carrier_ids[0]})
            pack_id = pack_weight_obj.search(cr, uid, [('picking_id','=',shippingresp_lnk.picking_id.id),('sequence','=',shippingresp_lnk.sequence)])
            self.pool.get('generate.labels').generate_shipping_report(cr, uid, ids, context)

            if pack_id:
                pack_weight_obj.write(cr, uid, pack_id, {'carrier_id':carrier_ids[0]}, context)
                
            
            ### Check Availabiity
            actionassign_result = stockpicking_obj.action_assign_new(cr,uid,[shippingresp_lnk.picking_id.id])
            if not actionassign_result:
                ### Force Availability
                saleorder_obj.write(cr, uid, shippingresp_lnk.picking_id.sale_id.id, {'state':'shipping_except'})
                return False
            
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            partial_datas = {
                'delivery_date' : current_time
            }

            for move in move_lines:
                if move.state in ('done', 'cancel'):
                    continue

                partial_datas['move%s' % (move.id)] = {
                    'product_id' : move.product_id.id,
                    'product_qty' : move.product_qty,
                    'product_uom' :move.product_uom.id,
                    'lot_ids' : move.lot_ids.id,
                }

            stockpicking_obj.do_transfer(cr, uid, [shippingresp_lnk.picking_id.id], context)
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_write(uid, 'stock.picking', shippingresp_lnk.picking_id.id, cr)
            wf_service.trg_write(uid, 'sale.order', shippingresp_lnk.picking_id.sale_id.id, cr)
            saleorder_obj.write(cr, uid, shippingresp_lnk.picking_id.sale_id.id, {'client_order_ref':context['tracking_no'], 'carrier_id':carrier_ids[0]})

            ### Write this shipping respnse is selected
            self.write(cr, uid, ids[0], {'selected':True})

            if context.get('batch_printing', False):
                return True
            
            
            #serverip = socket.gethostbyname(socket.gethostname())
            try:
                urllib2.urlopen('http://whatismyip.org').read()
            except Exception, e:                
                if error:
                    raise osv.except_osv(_('Error'), _('%s' % (e))) 
            
            self.write(cr, uid, ids, {'is_label_genrated':True}, context)   
            return True
            
        else:
            return False 
        
        
    def show_attachment(self, cr, uid, ids, context):
        
        for i in self.browse(cr, uid, ids):
            attachment_id=0
            if i.fedex_attach_id<>0:
                attachment_id=i.fedex_attach_id
            if i.ups_attach_id<>0:
                attachment_id=i.ups_attach_id
            
            if i.usps_attach_id<>0:
                attachment_id=i.usps_attach_id    
                     
            if attachment_id<>0:
                return {
                           'type': 'ir.actions.act_window',
                           'name': 'Shipping Receipt',
                           'datas_fname':'PackingList.png',
                           'view_mode': 'form',
                           'view_type': 'form',
                           'res_model': 'ir.attachment',
                           'nodestroy': True,
                           'res_id':attachment_id , # assuming the many2one is (mis)named 'teacher'
                           'context': context,
                       }
            else:
                    raise osv.except_osv('Error', 'Shipping Not Created')
                    return {'warning' : {'title':"Error",'message':"Shipping Not Created"},}
                
        return True
    
    ## getting carrier_tracking_ref .......
    def _get_carrier_tracking(self, cr, uid, ids, fields, arg, context=None):
        res ={}
        for line in self.browse(cr, uid, ids):
            res[line.id] = line.picking_id.carrier_tracking_ref
        return res
        
    _order = 'sr_no,type,name'

    _columns = {
        'name': fields.char('Service Type', size=100, readonly=True),
        'type': fields.char('Shipping Type', size=64, readonly=True),
        'rate': fields.char('Rate', size=64, readonly=True),
        'weight' : fields.float('Weight'),
        'length' : fields.integer('Length'),
        'width' : fields.integer('Width'),
        'height' : fields.integer('Height'),
        'cust_default':fields.boolean('Customer Default'),
        'sys_default' : fields.boolean('System Default'),
        'sr_no' : fields.integer('Sr. No'),
        'selected' : fields.boolean('Selected'),
        'picking_id' : fields.many2one('stock.picking','Picking'),
        'fedex_attach_id':fields.integer("Attachment ID"),
        'ups_attach_id':fields.integer("Attachment ID"),
        'usps_attach_id':fields.integer("Attachment ID"),
        'is_label_genrated':fields.boolean('Is Label Generate'),
        'label_genrated':fields.boolean('Label Generated?'),
        'carrier_track_no':fields.function(_get_carrier_tracking, string="Carrier Tracking Number", type='char', store=False),
        'pack_info':fields.char("Packages", size=100),
        'sequence':fields.integer('Sequence'),
    }
    
    _defaults = {
        'sr_no': 9,
        'selected': False
    }
shipping_response()

def _get_shipping_type(self, cr, uid, context=None):
    return [
        ('Fedex','Fedex'),
        ('UPS','UPS'),
        ('USPS','USPS'),
        ('All','All'),
    ]
def _get_service_type_usps(self, cr, uid, context=None):
    
    return [
        ('First Class', 'First Class'),
#         ('First Class HFP Commercial', 'First Class HFP Commercial'),
#         ('FirstClassMailInternational', 'First Class Mail International'),
        ('Priority', 'Priority'),
        ('Priority Commercial', 'Priority Commercial'),
        ('Priority HFP Commercial', 'Priority HFP Commercial'),
#         ('PriorityMailInternational', 'Priority Mail International'),
        ('Express', 'Express'),
        ('Express Commercial', 'Express Commercial'),
#         ('Express SH', 'Express SH'),
#         ('Express SH Commercial', 'Express SH Commercial'),
        ('Express HFP', 'Express HFP'),
        ('Express HFP Commercial', 'Express HFP Commercial'),
#         ('ExpressMailInternational', 'Express Mail International'),
#         ('ParcelPost', 'Parcel Post'),
#         ('ParcelSelect', 'Parcel Select'),
#         ('StandardMail', 'Standard Mail'),
#         ('CriticalMail', 'Critical Mail'),
        ('Media', 'Media'),
        ('Library', 'Library'),
        ('All', 'All'),
        ('Online', 'Online'),
    ]

def _get_first_class_mail_type_usps(self, cr, uid, context=None):
    return [
        ('Letter', 'Letter'),
        ('Flat', 'Flat'),
        ('Parcel', 'Parcel'),
        ('Postcard', 'Postcard'),
    ]

def _get_container_usps(self, cr, uid, context=None):
    return [
        ('Variable', 'Variable'),
        ('Card', 'Card'),
        ('Letter', 'Letter'),
        ('Flat', 'Flat'),
        ('Parcel', 'Parcel'),
        ('Large Parcel', 'Large Parcel'),
        ('Irregular Parcel', 'Irregular Parcel'),
        ('Oversized Parcel', 'Oversized Parcel'),
        ('Flat Rate Envelope', 'Flat Rate Envelope'),
        ('Padded Flat Rate Envelope', 'Padded Flat Rate Envelope'),
        ('Legal Flat Rate Envelope', 'Legal Flat Rate Envelope'),
        ('SM Flat Rate Envelope', 'SM Flat Rate Envelope'),
        ('Window Flat Rate Envelope', 'Window Flat Rate Envelope'),
        ('Gift Card Flat Rate Envelope', 'Gift Card Flat Rate Envelope'),
        ('Cardboard Flat Rate Envelope', 'Cardboard Flat Rate Envelope'),
        ('Flat Rate Box', 'Flat Rate Box'),
        ('SM Flat Rate Box', 'SM Flat Rate Box'),
        ('MD Flat Rate Box', 'MD Flat Rate Box'),
        ('LG Flat Rate Box', 'LG Flat Rate Box'),
        ('RegionalRateBoxA', 'RegionalRateBoxA'),
        ('RegionalRateBoxB', 'RegionalRateBoxB'),
        ('Rectangular', 'Rectangular'),
        ('Non-Rectangular', 'Non-Rectangular'),
     ]

def _get_size_usps(self, cr, uid, context=None):
    return [
        ('REGULAR', 'Regular'),
        ('LARGE', 'Large'),
     ]

# class stock_picking(osv.osv):
#     ## overwite the object stock.picking..........
#     _inherit = "stock.picking"
# 
#     _columns = {
#         'use_shipping' : fields.boolean('Use Shipping'),
#         'shipping_type' : fields.selection([
#         ('Fedex','Fedex'),
#         ('UPS','UPS'),
#         ('USPS','USPS'),
#         ('All','All'),
#     ],'Shipping Type'),
#         'weight_package' : fields.float('Package Weight', digits_compute= dp.get_precision('Stock Weight'),required=True, help="Package weight which comes from weighinig machine in pounds"),
#         'service_type_usps' : fields.selection([
#                                                 ('First Class', 'First Class'),
#                                                 ('Priority', 'Priority'),
#                                                 ('Priority Commercial', 'Priority Commercial'),
#                                                 ('Priority HFP Commercial', 'Priority HFP Commercial'),
#                                                 ('PriorityMailInternational', 'Priority Mail International'),
#                                                 ('Express', 'Express'),
#                                                 ('Express Commercial', 'Express Commercial'),
#                                                 ('Express HFP', 'Express HFP'),
#                                                 ('Express HFP Commercial', 'Express HFP Commercial'),
#                                                 ('Media', 'Media'),
#                                                 ('Library', 'Library'),
#                                                 ('All', 'All'),
#                                                 ('Online', 'Online'),
#                                             ], 'Service Type', size=100),
#                 
#         'first_class_mail_type_usps' : fields.selection([
#                                                             ('Letter', 'Letter'),
#                                                             ('Flat', 'Flat'),
#                                                             ('Parcel', 'Parcel'),
#                                                             ('Postcard', 'Postcard'),
#                                                         ], 'First Class Mail Type', size=50),
#         'container_usps' : fields.selection([
#                                                 ('Variable', 'Variable'),
#                                                 ('Card', 'Card'),
#                                                 ('Letter', 'Letter'),
#                                                 ('Flat', 'Flat'),
#                                                 ('Parcel', 'Parcel'),
#                                                 ('Large Parcel', 'Large Parcel'),
#                                                 ('Irregular Parcel', 'Irregular Parcel'),
#                                                 ('Oversized Parcel', 'Oversized Parcel'),
#                                                 ('Flat Rate Envelope', 'Flat Rate Envelope'),
#                                                 ('Padded Flat Rate Envelope', 'Padded Flat Rate Envelope'),
#                                                 ('Legal Flat Rate Envelope', 'Legal Flat Rate Envelope'),
#                                                 ('SM Flat Rate Envelope', 'SM Flat Rate Envelope'),
#                                                 ('Window Flat Rate Envelope', 'Window Flat Rate Envelope'),
#                                                 ('Gift Card Flat Rate Envelope', 'Gift Card Flat Rate Envelope'),
#                                                 ('Cardboard Flat Rate Envelope', 'Cardboard Flat Rate Envelope'),
#                                                 ('Flat Rate Box', 'Flat Rate Box'),
#                                                 ('SM Flat Rate Box', 'SM Flat Rate Box'),
#                                                 ('MD Flat Rate Box', 'MD Flat Rate Box'),
#                                                 ('LG Flat Rate Box', 'LG Flat Rate Box'),
#                                                 ('RegionalRateBoxA', 'RegionalRateBoxA'),
#                                                 ('RegionalRateBoxB', 'RegionalRateBoxB'),
#                                                 ('Rectangular', 'Rectangular'),
#                                                 ('Non-Rectangular', 'Non-Rectangular'),
#                                              ],'Container', size=100),
#         'size_usps' : fields.selection([
#                                             ('REGULAR', 'Regular'),
#                                             ('LARGE', 'Large'),
#                                          ],'Size'),
#         'width_usps' : fields.float('Width', digits_compute= dp.get_precision('Stock Weight')),
#         'length_usps' : fields.float('Length', digits_compute= dp.get_precision('Stock Weight')),
#         'height_usps' : fields.float('Height', digits_compute= dp.get_precision('Stock Weight')),
#         'girth_usps' : fields.float('Girth', digits_compute= dp.get_precision('Stock Weight')),
#         'dropoff_type_fedex' : fields.selection([
#                 ('REGULAR_PICKUP','REGULAR PICKUP'),
#                 ('REQUEST_COURIER','REQUEST COURIER'),
#                 ('DROP_BOX','DROP BOX'),
#                 ('BUSINESS_SERVICE_CENTER','BUSINESS SERVICE CENTER'),
#                 ('STATION','STATION'),
#             ],'Dropoff Type'),
#         'service_type_fedex' : fields.selection([
#                 ('EUROPE_FIRST_INTERNATIONAL_PRIORITY','EUROPE_FIRST_INTERNATIONAL_PRIORITY'),
#                 ('FEDEX_1_DAY_FREIGHT','FEDEX_1_DAY_FREIGHT'),
#                 ('FEDEX_2_DAY','FEDEX_2_DAY'),
#                 ('FEDEX_2_DAY_FREIGHT','FEDEX_2_DAY_FREIGHT'),
#                 ('FEDEX_3_DAY_FREIGHT','FEDEX_3_DAY_FREIGHT'),
#                 ('FEDEX_EXPRESS_SAVER','FEDEX_EXPRESS_SAVER'),
#                 ('STANDARD_OVERNIGHT','STANDARD_OVERNIGHT'),
#                 ('PRIORITY_OVERNIGHT','PRIORITY_OVERNIGHT'),
#                 ('FEDEX_GROUND','FEDEX_GROUND'),
#            ],'Service Type'),
#         'packaging_type_fedex' : fields.selection([
#                 ('FEDEX_BOX','FEDEX BOX'),
#                 ('FEDEX_PAK','FEDEX PAK'),
#                 ('FEDEX_TUBE','FEDEX_TUBE'),
#                 ('YOUR_PACKAGING','YOUR_PACKAGING'),
#             ],'Packaging Type', help="What kind of package this will be shipped in"),
#         'package_detail_fedex' : fields.selection([
#                 ('INDIVIDUAL_PACKAGES','INDIVIDUAL_PACKAGES'),
#                 ('PACKAGE_GROUPS','PACKAGE_GROUPS'),
#                 ('PACKAGE_SUMMARY','PACKAGE_SUMMARY'),
#             ],'Package Detail'),
#         'payment_type_fedex' : fields.selection([
#                 ('RECIPIENT','RECIPIENT'),
#                 ('SENDER','SENDER'),
#                 ('THIRD_PARTY','THIRD_PARTY'),
#             ],'Payment Type', help="Who pays for the rate_request?"),
#         'physical_packaging_fedex' : fields.selection([
#                 ('BAG','BAG'),
#                 ('BARREL','BARREL'),
#                 ('BOX','BOX'),
#                 ('BUCKET','BUCKET'),
#                 ('BUNDLE','BUNDLE'),
#                 ('CARTON','CARTON'),
#                 ('TANK','TANK'),
#                 ('TUBE','TUBE'),
#             ],'Physical Packaging'),
#         'pickup_type_ups' : fields.selection([
#                 ('01','Daily Pickup'),
#                 ('03','Customer Counter'),
#                 ('06','One Time Pickup'),
#                 ('07','On Call Air'),
#                 ('11','Suggested Retail Rates'),
#                 ('19','Letter Center'),
#                 ('20','Air Service Center'),
#             ],'Pickup Type'),
#         'service_type_ups' : fields.selection([
#                 ('01','Next Day Air'),
#                 ('02','Second Day Air'),
#                 ('03','Ground'),
#                 ('07','Worldwide Express'),
#                 ('08','Worldwide Expedited'),
#                 ('11','Standard'),
#                 ('12','Three-Day Select'),
#                 ('13','Next Day Air Saver'),
#                 ('14','Next Day Air Early AM'),
#                 ('54','Worldwide Express Plus'),
#                 ('59','Second Day Air AM'),
#                 ('65','Saver'),
#             ],'Service Type'),
#         'packaging_type_ups' : fields.selection([
#                 ('00','Unknown'),
#                 ('01','Letter'),
#                 ('02','Package'),
#                 ('03','Tube'),
#                 ('04','Pack'),
#                 ('21','Express Box'),
#                 ('24','25Kg Box'),
#                 ('25','10Kg Box'),
#                 ('30','Pallet'),
#                 ('2a','Small Express Box'),
#                 ('2b','Medium Express Box'),
#                 ('2c','Large Express Box'),
#             ],'Packaging Type'),
#         'shipping_label': fields.binary('Logo'),
#         'shipping_rate': fields.float('Shipping Rate'),
#         'response_usps_ids': fields.one2many('shipping.response','picking_id','Shipping Response'),
#         'sale_id':fields.many2one('sale.order',"sale ID")
#         
#     }
# 
#     _defaults = {
#         'use_shipping' : True,
#         'shipping_type' : 'All',
#         'service_type_usps' : 'All',
#         'size_usps' : 'REGULAR',
#         'dropoff_type_fedex' : 'REGULAR_PICKUP',
#         'service_type_fedex' : 'FEDEX_GROUND',
#         'packaging_type_fedex' : 'YOUR_PACKAGING',
#         'package_detail_fedex' : 'INDIVIDUAL_PACKAGES',
#         'payment_type_fedex' : 'SENDER',
#         'physical_packaging_fedex' : 'BOX',
#         'pickup_type_ups' : '01',
#         'service_type_ups' : '03',
#         'packaging_type_ups' : '02'
#     }
#     
#     def generate_shipping(self, cr, uid, ids, context={}):
#         ## call the stock.picking.out methods which work same as stock.picking
#         self.pool.get('stock.picking.out').generate_shipping(cr, uid, ids, context)
#         return True
#     
#     def _get_cust_default_shipping(self, cr, uid, carrier_id, context):
#         ## call the stock.picking.out methods which work same as stock.picking
#         return self.pool.get('stock.picking.out')._get_cust_default_shipping(cr, uid, carrier_id, context)
#     def _get_sys_default_shipping(self, cr, uid, saleorderline_ids, weight, context):
#         ## call the stock.picking.out methods which work same as stock.picking
#         return self.pool.get('stock.picking.out')._get_sys_default_shipping(cr, uid, saleorderline_ids, weight, context)
#         
#         
# stock_picking()

class stock_picking(osv.osv):
    
    _inherit="stock.picking"
    
     
    def action_assign_new(self, cr, uid, ids, *args):
        
        """ Changes state of picking to available if all moves are confirmed.
        @return: True
        """
        for pick in self.browse(cr, uid, ids):
            move_ids = [x.id for x in pick.move_lines if x.state in ('confirmed','done')]
            if not move_ids:
                return False
            self.pool.get('stock.move').action_assign(cr, uid, move_ids)
        return True

    def get_ups_servicetype_name(self, cr, uid, ids, code, mag_code=False):
        if code:
            if code == '01':
                return 'Next Day Air'
            elif code == '02':
                return 'Second Day Air'
            elif code == '03':
                return 'Ground'
            elif code == '07':
                return 'Worldwide Express'
            elif code == '08':
                return 'Worldwide Expedited'
            elif code == '11':
                return 'Standard'
            elif code == '12':
                return 'Three-Day Select'
            elif code == '13':
                return 'Next Day Air Saver'
            elif code == '14':
                return 'Next Day Air Early AM'
            elif code == '54':
                return 'Worldwide Express Plus'
            elif code == '59':
                return 'Second Day Air AM'
            elif code == '65':
                return 'Saver'
            else:
                return False
        elif mag_code:
            if mag_code == 'ups_3DS':
                return 'Three-Day Select'
            elif mag_code == 'ups_GND':
                return 'Ground'
            elif mag_code == 'ups_2DA':
                return 'Second Day Air'
            elif mag_code == 'ups_1DP':
                return 'Next Day Air Saver'
            elif mag_code == 'ups_1DA':
                return 'Next Day Air'
            elif mag_code == 'ups_1DM':
                return 'Next Day Air Early AM'
        else:
            return False

    def generate_fedex_shipping(self, cr, uid, ids, dropoff_type_fedex, service_type_fedex, packaging_type_fedex, payment_type_fedex, physical_packaging_fedex, sequence, pack, weight, shipper_postal_code,shipper_country_code,customer_postal_code,customer_country_code, length, width, height, shipping_type,sys_default=False,cust_default=False, error=True, context=None):
        has_fedex_setting = False
        if 'fedex_active' in context.keys() and context['fedex_active'] == False:
            return True
        ptr = None
        is_customer_account = False
        shippingfedex_id = None
        fedex_id = None
        shippingfedex_obj = self.pool.get('shipping.fedex')
        for picking_record in self.browse(cr, uid, ids):
            ptr = picking_record.partner_id
            if not picking_record.partner_id.country_id.id:
                raise osv.except_osv(_('Error'), _('Partner country not defined'))
                
            country_id = picking_record.partner_id.country_id.id
            is_customer_account = picking_record.is_customer_account
            fedex_id = picking_record.fedex_id
        
        if not is_customer_account:
            shippingfedex_id = shippingfedex_obj.search(cr,uid,[('active','=',True)])
            if not shippingfedex_id:
                if error:
                    if shipping_type != 'All':
                        raise osv.except_osv(_('Error'), _('Default FedEx settings not defined'))
                    else:
                        return None
                else:
                    return False
            else:
                shippingfedex_id = shippingfedex_id[0]
                has_fedex_setting = True
        else:
            if not fedex_id:
                    raise osv.except_osv('Warning', 'Please Enter Account Details')
            shippingfedex_id = shippingfedex_obj.search(cr,uid,[('partner_id','=',ptr.id),('country_id','=',country_id),('active','=',True)])
            if not shippingfedex_id:
                if error:
                    if shipping_type != 'All':
                        raise osv.except_osv(_('Error'), _('Default FedEx settings not defined'))
                    else:
                        return None
                else:
                    return False
            else:
                shippingfedex_id = shippingfedex_id[0]
                has_fedex_setting = True


        if has_fedex_setting:
            shippingfedex_ptr = shippingfedex_obj.browse(cr,uid,shippingfedex_id)
            account_no = shippingfedex_ptr.account_no
            key = shippingfedex_ptr.key
            password = shippingfedex_ptr.password
            meter_no = shippingfedex_ptr.meter_no
            is_test = shippingfedex_ptr.test
            CONFIG_OBJ = FedexConfig(key=key, password=password, account_number=account_no, meter_number=meter_no, use_test_server=is_test)
            rate_request = FedexRateServiceRequest(CONFIG_OBJ)
            # This is very generalized, top-level information.
            # REGULAR_PICKUP, REQUEST_COURIER, DROP_BOX, BUSINESS_SERVICE_CENTER or STATION
            rate_request.RequestedShipment.DropoffType = dropoff_type_fedex

            # See page 355 in WS_ShipService.pdf for a full list. Here are the common ones:
            # STANDARD_OVERNIGHT, PRIORITY_OVERNIGHT, FEDEX_GROUND, FEDEX_EXPRESS_SAVER
            rate_request.RequestedShipment.ServiceType = service_type_fedex

            # What kind of package this will be shipped in.
            # FEDEX_BOX, FEDEX_PAK, FEDEX_TUBE, YOUR_PACKAGING
            rate_request.RequestedShipment.PackagingType = packaging_type_fedex


            # No idea what this is.
            # INDIVIDUAL_PACKAGES, PACKAGE_GROUPS, PACKAGE_SUMMARY
    #         rate_request.RequestedShipment.PackageDetail = package_detail_fedex

            rate_request.RequestedShipment.Shipper.Address.PostalCode = shipper_postal_code
            rate_request.RequestedShipment.Shipper.Address.CountryCode = shipper_country_code
            rate_request.RequestedShipment.Shipper.Address.Residential = False

            rate_request.RequestedShipment.Recipient.Address.PostalCode = customer_postal_code
            rate_request.RequestedShipment.Recipient.Address.CountryCode = customer_country_code
            # This is needed to ensure an accurate rate quote with the response.
            #rate_request.RequestedShipment.Recipient.Address.Residential = True
            #include estimated duties and taxes in rate quote, can be ALL or NONE
            rate_request.RequestedShipment.EdtRequestType = 'NONE'

            # Who pays for the rate_request?
            # RECIPIENT, SENDER or THIRD_PARTY
            rate_request.RequestedShipment.ShippingChargesPayment.PaymentType = payment_type_fedex

            package1_weight = rate_request.create_wsdl_object_of_type('Weight')
            package1_weight.Value = weight
            package1_weight.Units = "LB"

            package1 = rate_request.create_wsdl_object_of_type('RequestedPackageLineItem')
            package1.Dimensions.Length = length
            package1.Dimensions.Width = width
            package1.Dimensions.Height = height
            package1.Dimensions.Units = 'IN'
            package1.Weight = package1_weight
            #can be other values this is probably the most common
            package1.PhysicalPackaging = physical_packaging_fedex
            # Un-comment this to see the other variables you may set on a package.
            # This adds the RequestedPackageLineItem WSDL object to the rate_request. It
            # increments the package count and total weight of the rate_request for you.
            package1.GroupPackageCount = 1
            rate_request.add_package(package1)

            # If you'd like to see some documentation on the ship service WSDL, un-comment
            # this line. (Spammy).

            # Un-comment this to see your complete, ready-to-send request as it stands
            # before it is actually sent. This is useful for seeing what values you can
            # change.

            # Fires off the request, sets the 'response' attribute on the object.
            try:
                rate_request.send_request()
            except Exception, e:
                if error:
                    #raise Exception('%s' % (e))
                    raise osv.except_osv(_('%s' % (e)),'')
                return False

            # This will show the reply to your rate_request being sent. You can access the
            # attributes through the response attribute on the request object. This is
            # good to un-comment to see the variables returned by the FedEx reply.

            # Here is the overall end result of the query.

            for detail in rate_request.response.RateReplyDetails[0].RatedShipmentDetails:
                for surcharge in detail.ShipmentRateDetail.Surcharges:
                    if surcharge.SurchargeType == 'OUT_OF_DELIVERY_AREA':
                        print "ODA rate_request charge %s" % surcharge.Amount.Amount

            for rate_detail in rate_request.response.RateReplyDetails[0].RatedShipmentDetails:
                print "Net FedEx Charge %s %s" % (rate_detail.ShipmentRateDetail.TotalNetFedExCharge.Currency,rate_detail.ShipmentRateDetail.TotalNetFedExCharge.Amount)

            sr_no = 9
            sys_default_value = False
            cust_default_value = False
            if sys_default:
                sys_default_vals = sys_default.split('/')
                if sys_default_vals[0] == 'FedEx':
                    sys_default_value = True
                    sr_no = 2

            if cust_default:
                cust_default_vals = cust_default.split('/')
                if cust_default_vals[0] == 'FedEx':
                    cust_default_value = True
                    sr_no = 1

            fedex_res_vals = {
                'sequence':sequence,
                'pack_info':pack,
                'name' : service_type_fedex,
                'type' : 'FedEx',
                'rate' : rate_detail.ShipmentRateDetail.TotalNetFedExCharge.Amount,
                'picking_id' : ids[0], #Change the ids[0] when switch to create
                'weight' : weight,
                'length' : length,
                'width' : width,
                'height' : height,
                'sys_default' : sys_default_value,
                'cust_default' : cust_default_value,
                'sr_no' : sr_no
            }
            fedex_res_id = self.pool.get('shipping.response').create(cr, uid, fedex_res_vals)
            if fedex_res_id:
                return True
            else:
                return False


    def generate_usps_shipping(self, cr, uid, ids,service_type_usps,first_class_mail_type_usps,container,size_usps,weight,zip_origination,zip_destination,sys_default=False,cust_default=False,error=True,context=None):
        ### Shift the code to def create
        ### Check if it is in delivery orders - Done
        ### Deleting all that exist if user is generating shipping again - Done
        ### Defaults values of types
        ### New link to do Generate Shipping
        
        
        #logger.notifyChannel('init', netsvc.LOG_WARNING, 'service_type_usps is %s'%(urllib.urlencode(service_type),))
        if 'usps_active' in context.keys() and context['usps_active'] == False:
            return True
        
        stockpicking_lnk = self.browse(cr,uid,ids[0])
        usps_res_id = False
        
        shippingusps_obj = self.pool.get('shipping.usps')
        shippingusps_id = shippingusps_obj.search(cr,uid,[('active','=',True)])
        if not shippingusps_id:
            ### This is required because when picking is created when saleorder is confirmed and if the default parameter has some error then it should not stop as the order is getting imported from external sites
            if error:
                raise osv.except_osv(_('Error'), _('Active USPS settings not defined'))
            else:
                return False
        else:
            shippingusps_id = shippingusps_id[0]
        shippingusps_ptr = shippingusps_obj.browse(cr,uid,shippingusps_id)
        user_id = shippingusps_ptr.user_id
        
        url = "http://testing.shippingapis.com/ShippingAPITest.dll?API=RateV4&" if shippingusps_ptr.test else "http://production.shippingapis.com/ShippingAPI.dll?API=RateV4&"
        ## <Service></Service>
        service_type = '<Service>' + service_type_usps + '</Service>'
        
        
        if service_type_usps == 'First Class':
            service_type += '<FirstClassMailType>' + first_class_mail_type_usps + '</FirstClassMailType>'
        #logger.notifyChannel('init', netsvc.LOG_WARNING, 'service_type is %s'%(service_type,))
        ### <Container />
        container = container and '<Container>' + container + '</Container>' or '<Container/>'
        #logger.notifyChannel('init', netsvc.LOG_WARNING, 'container is %s'%(container,))
        ### <Size />
        size = '<Size>' + size_usps + '</Size>'
        if size_usps == 'LARGE':
            size += '<Width>' + str(stockpicking_lnk.width_usps) + '</Width>'
            size += '<Length>' + str(stockpicking_lnk.length_usps) + '</Length>'
            size += '<Height>' + str(stockpicking_lnk.height_usps) + '</Height>'
        
            if stockpicking_lnk.container_usps == 'Non-Rectangular' or stockpicking_lnk.container_usps == 'Variable' or stockpicking_lnk.container_usps == '':
                size += '<Girth>' + str(stockpicking_lnk.height_usps) + '</Girth>'
        #logger.notifyChannel('init', netsvc.LOG_WARNING, 'size is %s'%(size,))
        
        weight_org = weight
        weight = math.modf(weight)
        pounds = int(weight[1])
        ounces = round(weight[0],2) * 16
        
        #logger.notifyChannel('init', netsvc.LOG_WARNING, 'pounds is %s'%(pounds,))
        #logger.notifyChannel('init', netsvc.LOG_WARNING, 'ounces is %s'%(ounces,))
        
        values = {}
        values['XML'] = '<RateV4Request USERID="' + user_id + '"><Revision/><Package ID="1ST">' + service_type + '<ZipOrigination>' + zip_origination + '</ZipOrigination><ZipDestination>' + zip_destination + '</ZipDestination><Pounds>' + str(pounds) + '</Pounds><Ounces>' + str(ounces) + '</Ounces>' + container + size + '<Machinable>true</Machinable></Package></RateV4Request>'
#         logger.notifyChannel('init', netsvc.LOG_WARNING, 'values is %s'%(urllib.urlencode(values),))
        url = url + urllib.urlencode(values)
#         logger.notifyChannel('init', netsvc.LOG_WARNING, 'shipping url is %s'%(url,))
        try:
            f = urllib2.urlopen(url)
            response = f.read()
#             logger.notifyChannel('init', netsvc.LOG_WARNING, '!!!!!!shipping response is %s'%(response,))
        except Exception, e:
            raise Exception('%s' % (e))
            return False
        
        
        if response.find('<Error>') != -1:
            sIndex = response.find('<Description>')
            eIndex = response.find('</Description>')
            if error:
                raise Exception('%s' % (response[int(sIndex)+13:int(eIndex)],))
            else:
                return False
        
        
        
        i = sIndex = eIndex = 0
        sIndex = response.find('<MailService>',i)
        eIndex = response.find('</MailService>',i)
        rsIndex = response.find('<Rate>',i)
        reIndex = response.find('</Rate>',i)
        while (sIndex != -1):
            i = reIndex + 7
            mail_service = str(response[int(sIndex) + 13:int(eIndex)])
            chr(174)
            rate = response[int(rsIndex)+6:int(reIndex)]
            sIndex = response.find('<MailService>',i)
            eIndex = response.find('</MailService>',i)
            rsIndex = response.find('<Rate>',i)
            reIndex = response.find('</Rate>',i)
        
            
            """if sys_default:
                if mail_service.lower().find(def_service_type.lower()) != -1:
                    #print "Testng condition: ",mail_service.lower().find(def_service_type.lower())
                    if mail_service.lower().find(def_firstclass_type.lower()) != -1:
                        if def_container:
                            if mail_service.lower().find(def_container.lower()) != -1:
                                sys_default_value = True
                                sr_no = 1
                        else:
                            sys_default_value = True
                            sr_no = 1"""
        
            sys_default_value = False
            cust_default_value = False
            sr_no = 9
        
            if cust_default and cust_default.split('/')[0] == 'USPS':
                cust_default_value = True
                sr_no = 1
                    
            elif sys_default and sys_default.split('/')[0] == 'USPS':
                sys_default_value = True
                sr_no = 2
                    
            usps_res_vals = {
                'name' : mail_service,
                'type' : 'USPS',
                'rate' : rate,
                'picking_id' : ids[0], #Change the ids[0] when switch to create
                'weight' : weight_org,
                'sys_default' : sys_default_value,
                'cust_default' : cust_default_value,
                'sr_no' : sr_no,
            }
            usps_res_id = self.pool.get('shipping.response').create(cr,uid,usps_res_vals)
#             logger.notifyChannel('init', netsvc.LOG_WARNING, 'usps_res_id is %s'%(usps_res_id,))
        if usps_res_id:
            return True
        else:
            return False
            ## the function for creating quoates..............
    def create_quotes(self, cr, uid, ids, vals, context={}):
        
        quotes_vals = {
            'name' : vals.service_type,
            'type' : context['type'],
            'rate' : vals.rate,
            'picking_id' : ids[0], #Change the ids[0] when switch to create
            'weight' : vals.weight,
            'length' : vals.length,
            'width' : vals.width,
            'height' : vals.height,
            'sys_default' : False,
            'cust_default' : False,
            'sr_no' : vals.sr_no,
        }
        res_id = self.pool.get('shipping.response').create(cr, uid, quotes_vals)
#         logger.notifyChannel('init', netsvc.LOG_WARNING, 'res_id is %s'%(res_id,))
        if res_id:
            return res_id
        else:
            return False
        

    def create_attachment(self, cr, uid, ids, vals, context={}):
        ## create attachemnt for ups shipping service..............
        stockpicking_obj = self.pool.get('stock.picking')
        picking_id = stockpicking_obj.browse(cr, uid, ids)
        attachment_pool = self.pool.get('ir.attachment')
        data_attach = {
            'name': 'PackingList.' + vals.image_format.lower() ,
            'datas_fname':picking_id[0].sale_id.name+'.'+vals.image_format.lower(),
            'datas': binascii.b2a_base64(str(b64decode(vals.graphic_image))),
            'description': 'Packing List',
            'res_name': self.browse(cr,uid,ids[0]).name,
            'res_model': 'stock.picking',
            'res_id': ids[0],
        }
        attach_id = attachment_pool.create(cr, uid, data_attach)
        return attach_id
    ## remove the duplicates and adding new..................
    def refresh_the_quotes(self, cr, uid, ids, context):
        shipping_res_obj = self.pool.get('shipping.response')
        existed_ups_ids = []
        if 'name' in context:
            existed_ups_ids = shipping_res_obj.search(cr, uid, [('picking_id','=',ids),('type','=',context['type']),('name', '=',context['name'])])
            shipping_res_obj.unlink(cr, uid, existed_ups_ids)
        
        if 'all'  in context['type'] and 'ups_service_type' in context:
            existed_ups_ids = shipping_res_obj.search(cr, uid, [('picking_id','=',ids),('name', '=',context['ups_service_type'])])
            shipping_res_obj.unlink(cr, uid, existed_ups_ids)
        if 'all'  in context['type'] and 'fedex_service_type' in context:
            existed_ups_ids = shipping_res_obj.search(cr, uid, [('picking_id','=',ids),('name', '=',context['fedex_service_type'])])
            shipping_res_obj.unlink(cr, uid, existed_ups_ids)
        if 'all'  in context['type'] and 'usps_service_type' in context:
            existed_ups_ids = shipping_res_obj.search(cr, uid, [('picking_id','=',ids),('name', '=',context['usps_service_type'])])
            shipping_res_obj.unlink(cr, uid, existed_ups_ids)
        
    ## This function is called when the Generate Shipping Quote button is clicked
    def generate_shipping(self, cr, uid, ids, context={}):
        no_shipping_configured = False
        if context is None:
            context = {}
    #        logger.notifyChannel('init', netsvc.LOG_WARNING, 'inside generate_shipping context: %s'%(context,))
        for id in ids:
            stockpicking = self.browse(cr, uid, id)
            shipping_type = stockpicking.shipping_type

            weight = stockpicking.weight_package if stockpicking.weight_package else stockpicking.weight_net
            if not weight:
                raise Exception('Please Give Package Weight!')
            stockpicking.sale_id.company_id
            ##getting address from shop_id........
            cust_address = stockpicking.sale_id.company_id
            if not cust_address:
                raise Exception('Company Address not defined!')
            shipper = Address(cust_address.name or cust_address.name, cust_address.street, cust_address.city, cust_address.state_id.code or '', cust_address.zip, cust_address.country_id.code, cust_address.street2 or '', cust_address.phone or '', cust_address.email, cust_address.name)
            ### Recipient
            cust_address = stockpicking.partner_id
            cust_default=False
            sys_default=False
            receipient = Address(cust_address.name or cust_address.name, cust_address.street, cust_address.city, cust_address.state_id.code or '', cust_address.zip, cust_address.country_id.code, cust_address.street2 or '', cust_address.phone or '', cust_address.email, cust_address.name)
            # Deleting previous quotes
            shipping_res_obj = self.pool.get('shipping.response')
            shipping_res_obj.search(cr,uid,[('picking_id','=',ids[0])])
            ## condition for usps setting for generating or creating Quotes
            if shipping_type == 'UPS':
                context['type'] = 'UPS'
                ups_value = dict(self._columns['service_type_ups'].selection).get(stockpicking.service_type_ups)
                context['name'] = ups_value
                self.refresh_the_quotes(cr, uid, id, context)

            if shipping_type == 'Fedex':
                context['type'] = 'FedEx'
                context['name'] = stockpicking.service_type_fedex
                self.refresh_the_quotes(cr, uid, id, context)

            if shipping_type == 'USPS':
                context['type'] = 'USPS'
                context['name'] = stockpicking.service_type_usps
                if stockpicking.service_type_usps == 'All':
                    context['name'] = "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt;"

                self.refresh_the_quotes(cr, uid, id, context)

            if shipping_type == 'All':
                context['type'] = 'all'
                ups_value = dict(self._columns['service_type_ups'].selection).get(stockpicking.service_type_ups)
                context['ups_service_type'] = ups_value
                context['fedex_service_type'] = stockpicking.service_type_fedex
                context['usps_service_type'] =  stockpicking.service_type_usps
                if stockpicking.service_type_usps == 'All':
                    context['usps_service_type'] =  "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt;"

                self.refresh_the_quotes(cr, uid, id, context)
            if 'usps_active' not in context.keys() and (shipping_type == 'USPS' or shipping_type == 'All'):
                usps_info = self.pool.get('shipping.usps').get_usps_info(cr,uid,context)
            for line in stockpicking.pack_weight_ids:
                if 'usps_active' not in context.keys() and (shipping_type == 'USPS' or shipping_type == 'All'):
                    if usps_info != None:
                        service_type_usps = stockpicking.service_type_usps
                        first_class_mail_type_usps = stockpicking.first_class_mail_type_usps or ''
                        container_usps = stockpicking.container_usps or ''
                        size_usps = stockpicking.size_usps
                        width_usps = stockpicking.width_usps
                        length_usps = stockpicking.length_usps
                        height_usps = stockpicking.height_usps
                        girth_usps = stockpicking.girth_usps
                        usps = shippingservice.USPSRateRequest(usps_info, service_type_usps, first_class_mail_type_usps, container_usps, size_usps, str(width_usps), str(length_usps), str(height_usps), girth_usps, line.weight, shipper, receipient, cust_default, sys_default)
                        usps_response = usps.send()
                        context['type'] = 'USPS'
                        usps_qoute_id = self.create_quotes(cr, uid, ids, usps_response, context)
                        if usps_qoute_id:
                                shipping_res_obj.write(cr, uid, [usps_qoute_id], {'pack_info':line.pack, 'sequence':line.sequence})
                    else:
                        no_shipping_configured = True

                if shipping_type == 'UPS' or shipping_type == 'All':
                    ups_info = None
                    stockpicking = self.browse(cr, uid, id)
                    if not stockpicking.is_customer_account:
                        ups_info = self.pool.get('shipping.ups').get_ups_info(cr,uid,context)
                        if ups_info == None and no_shipping_configured == False:
                            no_shipping_configured = True

                    else:
                        if not stockpicking.ups_id:
                            raise osv.except_osv('Warning', 'Please Enter Account Details')
                        ups_info = self.pool.get('shipping.ups').get_ups_partner_info(cr,uid, [stockpicking.id],context)


                    pickup_type_ups = stockpicking.pickup_type_ups
                    service_type_ups = stockpicking.service_type_ups
                    packaging_type_ups = stockpicking.packaging_type_ups

                    if line.product_ul_line.length and line.product_ul_line.width and line.product_ul_line.length:
                        ups = shippingservice.UPSRateRequest(ups_info, pickup_type_ups, service_type_ups, packaging_type_ups, line.weight, shipper, receipient, line.product_ul_line.length, line.product_ul_line.width, line.product_ul_line.height, cust_default, sys_default)
                    else:
                        ups = shippingservice.UPSRateRequest(ups_info, pickup_type_ups, service_type_ups, packaging_type_ups, line.weight, shipper, receipient, 0, 0, 0, cust_default, sys_default)
                    ups_response = ups.send()
                    context['type'] = 'UPS'
                    ups_qoute_id = self.create_quotes(cr, uid, ids, ups_response, context)
                    if ups_qoute_id:
                        shipping_res_obj.write(cr, uid, [ups_qoute_id], {'pack_info':line.pack, 'sequence':line.sequence})


                if shipping_type == 'Fedex' or shipping_type == 'All':
                    dropoff_type_fedex = stockpicking.dropoff_type_fedex
                    service_type_fedex = stockpicking.service_type_fedex
                    packaging_type_fedex = stockpicking.packaging_type_fedex
#                         package_detail_fedex = stockpicking.package_detail_fedex
                    payment_type_fedex = stockpicking.payment_type_fedex
                    physical_packaging_fedex = stockpicking.physical_packaging_fedex
                    shipper_postal_code = shipper.zip
                    shipper_country_code = shipper.country_code
                    customer_postal_code = receipient.zip
                    customer_country_code = receipient.country_code
                    error_required = True

                    if line.product_ul_line.length and line.product_ul_line.width and line.product_ul_line.length:
                        self.generate_fedex_shipping(cr,uid,[id],dropoff_type_fedex,service_type_fedex,
                        packaging_type_fedex,payment_type_fedex,physical_packaging_fedex,line.sequence,line.pack,
                        line.weight,shipper_postal_code,shipper_country_code,customer_postal_code,customer_country_code,
                        int(line.product_ul_line.length), int(line.product_ul_line.width), int(line.product_ul_line.height),shipping_type,sys_default,cust_default,error_required, context)
                    else:
                        self.generate_fedex_shipping(cr,uid,[id],dropoff_type_fedex,service_type_fedex,
                        packaging_type_fedex,payment_type_fedex,physical_packaging_fedex,line.sequence,line.pack,
                        line.weight,shipper_postal_code,shipper_country_code,customer_postal_code,customer_country_code,
                        0, 0, 0, shipping_type,sys_default,cust_default,error_required, context)

        return True

    def _get_cust_default_shipping(self, cr, uid, carrier_id, context={}):
        
        if carrier_id:
            carrier_obj = self.pool.get('delivery.carrier')             
            carrier_lnk = carrier_obj.browse(cr, uid, carrier_id)
            cust_default = ''
            if carrier_lnk.is_ups:
                cust_default = 'UPS'
                service_type_ups = carrier_lnk.service_code or '03'
                cust_default += '/' + service_type_ups
            elif carrier_lnk.is_fedex:
                cust_default = 'FedEx'
                service_type_fedex = carrier_lnk.service_code or 'FEDEX_GROUND'
                cust_default += '/' + service_type_fedex
            elif carrier_lnk.is_usps:
                cust_default = 'USPS'
                service_type_usps = carrier_lnk.service_code or 'All'
                cust_default += '/' + service_type_usps
        else:
            cust_default = False
        return cust_default

    def _get_sys_default_shipping(self,cr, uid, saleorderline_ids, weight, context={}):
        sys_default = False
        if len(saleorderline_ids) <= 2:
            product_obj = self.pool.get('product.product')
            saleorderline_obj = self.pool.get('sale.order.line')
            product_shipping_obj = self.pool.get('product.product.shipping')
            product_categ_shipping_obj = self.pool.get('product.category.shipping')
            product_id = False
            ### Making sure product is not Shipping and Handling
            for line in saleorderline_obj.browse(cr,uid,saleorderline_ids):
                if line.product_id.type == 'service':
                    continue
                product_id = line.product_id.id
                
            if not product_id:
                return False
            product_shipping_ids = product_shipping_obj.search(cr,uid,[('product_id','=',product_id)])
            if not product_shipping_ids:
                categ_id = product_obj.browse(cr,uid,product_id).product_tmpl_id.categ_id.id
                product_categ_shipping_ids = product_categ_shipping_obj.search(cr,uid,[('product_categ_id','=',categ_id)])
                if not product_categ_shipping_ids:
                    ### Assume the default
                    if (weight*16) > 14.0:
                        sys_default = 'USPS/Priority/Parcel/REGULAR'
                    else:
                        sys_default = 'USPS/First Class/Parcel/REGULAR'
                    return sys_default
        
            if product_shipping_ids:
                cr.execute(
                    'SELECT * '
                    'FROM product_product_shipping '
                    'WHERE weight <= %s ' +
                    'and product_id=%s ' +
                    'order by sequence desc limit 1',
                    (weight,product_id))
            else:
                cr.execute(
                    'SELECT * '
                    'FROM product_category_shipping '
                    'WHERE weight <= %s '+
                    'and product_categ_id=%s '+
                    'order by sequence desc limit 1',
                    (weight,categ_id))
            res = cr.dictfetchall()
            ### Format- USPS/First Class/Letter
            if res:
                sys_default = res[0]['shipping_type'] + '/' + res[0]['service_type_usps'] + '/' + res[0]['container_usps'] + '/' + res[0]['size_usps']
        return sys_default
    
    
    def create(self, cr, uid, vals, context=None):
        sale_obj = self.pool.get('sale.order')
        order_id = None
        if 'origin' in vals and vals['origin']:
            order_id = sale_obj.search(cr, uid, [('name','=',vals['origin'])])
            if order_id:
                vals['sale_id'] = order_id[0]
        for order_record in sale_obj.browse(cr, uid, order_id):
            if order_record.is_ship_customer_account:
                vals['is_customer_account'] = True
        return super(stock_picking, self).create(cr, uid, vals, context=None)
    
    def write(self, cr, uid, ids, vals, context=None):
        if vals.has_key('pack_weight_ids') and vals['pack_weight_ids']:
            
#             self.write(cr, uid, ids, {'no_of_packets':len(vals['pack_weight_ids'])})
            vals.update({'no_of_packets':len(vals['pack_weight_ids'])})
        return super(stock_picking, self).write(cr, uid, ids, vals, context=context)
    


    def _cal_weight_usps(self, cr, uid, ids, name, args, context=None):
        
        res = {}
        self.pool.get('product.uom')
        for picking in self.browse(cr, uid, ids, context=context):
            weight_net = picking.weight_net or 0.00
            weight_net_usps = weight_net / 2.2
            res[picking.id] = {
                                'weight_net_usps': weight_net_usps,
                              }
        return res
    
    def _get_picking_line(self, cr, uid, ids, context=None):
        
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            result[line.picking_id.id] = True
        return result.keys()
    
    ## getting weight from pack_weight_lines ..............
    def _get_pack_weight(self, cr, uid, ids, field_name, field_value, arg, context=None):
        result={} 
        for records_picking in self.browse(cr, uid, ids, context=context):
            total=0.0
            for records_weight_lines in records_picking.pack_weight_ids:
                total += records_weight_lines.weight
            result[records_picking.id] = total
        return result
#     ## getting account according to selection of service type...................
#     def onchange_accounts(self, cr, uid, ids, type, context=None):
        
    ## it is for adding pack with max weight per package...................
    def add_packet_line(self, cr, uid, ids, context=None):
#         from auspost_pac.pac import PAC
#         from auspost_pac.models import Parcel
#         from auspost_pac.tests import TestPostcodeLookup 
#         from pprint import pprint
#         p = PAC('c8cf3045-91d0-40c5-babd-1516a6f78d6d')
#         parcel_obj = Parcel(width=40,height=35,length=65,weight=2)
# #         TestPostcodeLookup
#         width=40
#         height=35
#         depth=65
#         Weight=2
#         bris = p.domestic_parcel_services(4000, 2000, parcel_obj)
#         print bris,'-------------------------------12322'
#         for line in bris:
#             print line.name,'================================123'
#             print line.price,'================================123'
        sp_obj = self.browse(cr, uid, ids[0])
        total = 0.0
        try:
            if sp_obj.no_of_packets < 1 and sp_obj.max_weight < 0.01:
                raise Exception('Please Give the Valid No. of Package and Max Weight Per Package!')
            elif sp_obj.no_of_packets < 1:
                raise Exception('Please Give Valid No. of Package!')
            elif sp_obj.max_weight < 0.01:
                raise Exception('Please Give Valid Max. Weight Per Package!')
                  
            else:
                pack_weight_obj = self.pool.get('pack.weight')
                cr.execute("delete from pack_weight where picking_id=%s"%(ids[0]))
                for i in range(1,sp_obj.no_of_packets + 1):
                    record_id = pack_weight_obj.create(cr,uid,{'picking_id':ids[0],'weight':sp_obj.max_weight,'sequence':i,'pack':'Pack-' + str(i), 'product_ul_line': sp_obj.product_ul.id})
                    if record_id:
                        total = total + sp_obj.max_weight
                self.write(cr, uid, ids, {'weight_package':total})
#                     
                return True
                
        except Exception, exc:
                raise osv.except_osv(_('Error!'), _('%s' % (exc,)))
    

    _columns = {
        'use_shipping' : fields.boolean('Use Shipping'),
        'shipping_type' : fields.selection([
                                                ('Fedex','Fedex'),
                                                ('UPS','UPS'),
                                                ('USPS','USPS'),
                                                ('All','All'),
                                            ],'Shipping Type'),
#         'weight_package' : fields.float('Package Weight', digits_compute= dp.get_precision('Stock Weight'), help="Package weight which comes from weighinig machine in pounds"),
        'weight_package' : fields.function(_get_pack_weight, string="Package Weight", type='float', store=True),
        'service_type_usps' : fields.selection(_get_service_type_usps, 'Service Type', size=100),
        'first_class_mail_type_usps' : fields.selection(_get_first_class_mail_type_usps, 'First Class Mail Type', size=50),
        'container_usps' : fields.selection(_get_container_usps,'Container', size=100),
        'size_usps' : fields.selection(_get_size_usps,'Size'),
        'width_usps' : fields.float('Width', digits_compute= dp.get_precision('Stock Weight')),
        'length_usps' : fields.float('Length', digits_compute= dp.get_precision('Stock Weight')),
        'height_usps' : fields.float('Height', digits_compute= dp.get_precision('Stock Weight')),
        'girth_usps' : fields.float('Girth', digits_compute= dp.get_precision('Stock Weight')),
        #'machinable_usps' : fields.boolean('Machinable', domain=[('service_type_usps', 'in', ('first_class','parcel','all','online')), '|', ('first_class_mail_type_usps', 'in', ('letter','flat'))]),
        #'ship_date_usps' : fields.date('Ship Date', help="Date Package Will Be Mailed. Ship date may be today plus 0 to 3 days in advance."),
        'dropoff_type_fedex' : fields.selection([
                ('REGULAR_PICKUP','REGULAR PICKUP'),
                ('REQUEST_COURIER','REQUEST COURIER'),
                ('DROP_BOX','DROP BOX'),
                ('BUSINESS_SERVICE_CENTER','BUSINESS SERVICE CENTER'),
                ('STATION','STATION'),
            ],'Dropoff Type'),
        'service_type_fedex' : fields.selection([
                ('EUROPE_FIRST_INTERNATIONAL_PRIORITY','EUROPE_FIRST_INTERNATIONAL_PRIORITY'),
                ('FEDEX_1_DAY_FREIGHT','FEDEX_1_DAY_FREIGHT'),
                ('FEDEX_2_DAY','FEDEX_2_DAY'),
                ('FEDEX_2_DAY_FREIGHT','FEDEX_2_DAY_FREIGHT'),
                ('FEDEX_3_DAY_FREIGHT','FEDEX_3_DAY_FREIGHT'),
                ('FEDEX_EXPRESS_SAVER','FEDEX_EXPRESS_SAVER'),
                ('STANDARD_OVERNIGHT','STANDARD_OVERNIGHT'),
                ('PRIORITY_OVERNIGHT','PRIORITY_OVERNIGHT'),
                ('FEDEX_GROUND','FEDEX_GROUND'),
           ],'Service Type'),
        'packaging_type_fedex' : fields.selection([
                ('FEDEX_BOX','FEDEX BOX'),
                ('FEDEX_PAK','FEDEX PAK'),
                ('FEDEX_TUBE','FEDEX_TUBE'),
                ('YOUR_PACKAGING','YOUR_PACKAGING'),
            ],'Packaging Type', help="What kind of package this will be shipped in"),
        'package_detail_fedex' : fields.selection([
                ('INDIVIDUAL_PACKAGES','INDIVIDUAL_PACKAGES'),
                ('PACKAGE_GROUPS','PACKAGE_GROUPS'),
                ('PACKAGE_SUMMARY','PACKAGE_SUMMARY'),
            ],'Package Detail'),
        'payment_type_fedex' : fields.selection([
                ('RECIPIENT','RECIPIENT'),
                ('SENDER','SENDER'),
                ('THIRD_PARTY','THIRD_PARTY'),
            ],'Payment Type', help="Who pays for the rate_request?"),
        'physical_packaging_fedex' : fields.selection([
                ('BAG','BAG'),
                ('BARREL','BARREL'),
                ('BOX','BOX'),
                ('BUCKET','BUCKET'),
                ('BUNDLE','BUNDLE'),
                ('CARTON','CARTON'),
                ('TANK','TANK'),
                ('TUBE','TUBE'),
            ],'Physical Packaging'),
        'pickup_type_ups' : fields.selection([
                ('01','Daily Pickup'),
                ('03','Customer Counter'),
                ('06','One Time Pickup'),
                ('07','On Call Air'),
                ('11','Suggested Retail Rates'),
                ('19','Letter Center'),
                ('20','Air Service Center'),
            ],'Pickup Type'),
        'service_type_ups' : fields.selection([
                ('01','Next Day Air'),
                ('02','Second Day Air'),
                ('03','Ground'),
                ('07','Worldwide Express'),
                ('08','Worldwide Expedited'),
                ('11','Standard'),
                ('12','Three-Day Select'),
                ('13','Next Day Air Saver'),
                ('14','Next Day Air Early AM'),
                ('54','Worldwide Express Plus'),
                ('59','Second Day Air AM'),
                ('65','Saver'),
            ],'Service Type'),
        'packaging_type_ups' : fields.selection([
                ('00','Unknown'),
                ('01','Letter'),
                ('02','Package'),
                ('03','Tube'),
                ('04','Pack'),
                ('21','Express Box'),
                ('24','25Kg Box'),
                ('25','10Kg Box'),
                ('30','Pallet'),
                ('2a','Small Express Box'),
                ('2b','Medium Express Box'),
                ('2c','Large Express Box'),
            ],'Packaging Type'),
        'shipping_label' : fields.binary('Logo'),
        'shipping_rate': fields.float('Shipping Rate'),
        'response_usps_ids' : fields.one2many('shipping.response','picking_id','Shipping Response'),
        'pack_weight_ids': fields.one2many('pack.weight','picking_id','Package Weight'),
        'sale_id':fields.many2one('sale.order',"sale ID"),
        'is_customer_account':fields.boolean("Use Customer Account"),
        'weight_note':fields.text('Status',readonly=True),
        'fedex_id':fields.many2one('shipping.fedex', 'Fedex Customer Account'),
        'ups_id':fields.many2one('shipping.ups', 'UPS Customer Account'),
        'usps_id':fields.many2one('shipping.usps', 'USPS Customer Account'),
        'is_multiple_label':fields.boolean('Is Multiple label'),
        'no_of_packets':fields.integer("No. of Package"),
        'package_length': fields.integer("Length"),
        'package_width': fields.integer("Width"),
        'package_height': fields.integer("Height"),
        'product_ul': fields.many2one("product.ul", "Package Dimensions"),
        'max_weight':fields.float("Max Weight Per Package"),
        
    }

    @api.onchange('product_ul')
    def onchange_product_ul(self):
        self.package_length = self.product_ul.length
        self.package_width = self.product_ul.width
        self.package_height = self.product_ul.height
        return

    @api.multi
    @api.onchange('product_ul')
    def onchange_package_dimensions_lines(self):
        for pack_weight_id in self.pack_weight_ids:
            pack_weight_id.product_ul_line = self.product_ul

    _defaults = {
        'use_shipping' : True,
        'shipping_type' : 'All',
        'service_type_usps' : 'All',
        'size_usps' : 'REGULAR',
        'dropoff_type_fedex' : 'REGULAR_PICKUP',
        'service_type_fedex' : 'FEDEX_GROUND',
        'packaging_type_fedex' : 'YOUR_PACKAGING',
        'package_detail_fedex' : 'INDIVIDUAL_PACKAGES',
        'payment_type_fedex' : 'SENDER',
        'physical_packaging_fedex' : 'BOX',
        'pickup_type_ups' : '01',
        'service_type_ups' : '03',
        'packaging_type_ups' : '02'
    }
    
    ## mapping country for country vice customers accounts.......................
    def onchange_mapping_country(self, cr, uid, ids, is_account, shipping_type,partner_id, context=None):
        
        partner_obj = self.pool.get('res.partner')
        ups_obj = self.pool.get('shipping.ups')
        fedex_obj = self.pool.get('shipping.fedex')
        usps_obj = self.pool.get('shipping.usps')
        ups_id = []
        fedex_id = []
        usps_id = []
        partner_info = partner_obj.browse(cr, uid, partner_id)
        ## when we either select ups or all  ............................
        if shipping_type:
            if shipping_type == 'UPS':
                ups_id = ups_obj.search(cr, uid, [('partner_id','=',partner_info.id),('country_id','=',partner_info.country_id.id)])
                return {'domain':{'ups_id':[('id','in', ups_id)],'fedex_id':None,'usps_id':None}}
            ## when we either select fedex or all  ............................    
            if shipping_type == 'Fedex':
                fedex_id = fedex_obj.search(cr, uid, [('partner_id','=',partner_info.id),('country_id','=',partner_info.country_id.id)])
                return {'domain':{'ups_id':None,'fedex_id':[('id','in', fedex_id)],'usps_id':None}}
            ## when we either select usps or all.......................    
            if shipping_type == 'USPS':
                usps_id = usps_obj.search(cr, uid, [('partner_id','=',partner_info.id),('country_id','=',partner_info.country_id.id)])
                return {'domain':{'ups_id':None,'fedex_id':None,'usps_id':[('id','in', usps_id)]}}
            if shipping_type == 'All':
                ups_id = ups_obj.search(cr, uid, [('partner_id','=',partner_info.id),('country_id','=',partner_info.country_id.id)])
                fedex_id = fedex_obj.search(cr, uid, [('partner_id','=',partner_info.id),('country_id','=',partner_info.country_id.id)])
                usps_id = usps_obj.search(cr, uid, [('partner_id','=',partner_info.id),('country_id','=',partner_info.country_id.id)])
                return {'domain':{'ups_id':[('id','in', ups_id)],'fedex_id':[('id','in', fedex_id)],'usps_id':[('id','in',usps_id)]}}
        else:
            return {}
    
    ## customization done by tara chand..........................
    def open_compair_rate_wizard(self, cr, uid, ids, context={}):
        context['search_default_group_by_type'] = True
        context['search_default_group_by_name'] = True
         
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid, 'shipping_pragtech', 'compare_rate_search_view')
        id = result and result[1] or False
        rate_obj = self.pool.get('compare.shipping.rates')
        cr.execute("delete from compare_shipping_rates")
        check_list_ups = []
        check_list_usps = []
        check_list_fedex = []
        check_name_list_ups = []
        check_name_list_usps = []
        check_name_list_fedex = []
        #TODO belo code saving the unique record and latest record from model shipping.response
        for obj in self.browse(cr, uid, ids):
#             print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",sorted(obj.response_usps_ids,key=lambda x:x.id)
            for res_ids in obj.response_usps_ids:
                if res_ids.type == 'UPS':
                    if res_ids.name in check_name_list_ups:
                        if res_ids.pack_info+res_ids.name in check_list_ups:
                            search_ids = rate_obj.search(cr, uid, [('name', '=', res_ids.name),('type','=',res_ids.type),('pack_info','=',res_ids.pack_info)])
                            browse_obj = rate_obj.browse(cr,uid,search_ids)
                            if browse_obj.shipping_response_id.id < res_ids.id :
                                rate_obj.write(cr, uid, search_ids, {'rate':res_ids.rate,'shipping_response_id':res_ids.id,'weight':res_ids.weight}, context)
                        else:
                            check_name_list_ups.append(res_ids.name)
                            check_list_ups.append(res_ids.pack_info+res_ids.name)
                            val = {
                                 'pack_info':res_ids.pack_info,
                                 'shipping_response_id':res_ids.id,
                                 'name':res_ids.name,
                                 'type':res_ids.type,
                                 'weight':res_ids.weight,
                                 'rate':res_ids.rate,
                             }
                            rate_obj.create(cr, uid, val)
                    else:
                            check_name_list_ups.append(res_ids.name)
                            check_list_ups.append(res_ids.pack_info+res_ids.name)
                            val = {
                                 'pack_info':res_ids.pack_info,
                                 'shipping_response_id':res_ids.id,
                                 'name':res_ids.name,
                                 'type':res_ids.type,
                                 'weight':res_ids.weight,
                                 'rate':res_ids.rate,
                             }
                            rate_obj.create(cr, uid, val)
                if res_ids.type == 'USPS':
                    if res_ids.name in check_name_list_usps:
                        if res_ids.pack_info+res_ids.name in check_list_usps:
                            search_ids = rate_obj.search(cr, uid, [('name', '=', res_ids.name),('type','=',res_ids.type),('pack_info','=',res_ids.pack_info)])
                            browse_obj = rate_obj.browse(cr,uid,search_ids)
                            if browse_obj.shipping_response_id.id < res_ids.id :
                                rate_obj.write(cr, uid, search_ids, {'rate':res_ids.rate,'shipping_response_id':res_ids.id,'weight':res_ids.weight}, context)
                        else:
                            check_name_list_usps.append(res_ids.name)
                            check_list_usps.append(res_ids.pack_info+res_ids.name)
                            val = {
                                 'pack_info':res_ids.pack_info,
                                 'shipping_response_id':res_ids.id,
                                 'name':res_ids.name,
                                 'type':res_ids.type,
                                 'weight':res_ids.weight,
                                 'rate':res_ids.rate,
                             }
                            rate_obj.create(cr, uid, val)
                    else:
                            check_name_list_usps.append(res_ids.name)
                            check_list_usps.append(res_ids.pack_info+res_ids.name)
                            val = {
                                 'pack_info':res_ids.pack_info,
                                 'shipping_response_id':res_ids.id,
                                 'name':res_ids.name,
                                 'type':res_ids.type,
                                 'weight':res_ids.weight,
                                 'rate':res_ids.rate,
                             }
                            rate_obj.create(cr, uid, val)
                if res_ids.type == 'FedEx':
                    if res_ids.name in check_name_list_fedex:
                        if res_ids.pack_info+res_ids.name in check_list_fedex:
                            search_ids = rate_obj.search(cr, uid, [('name', '=', res_ids.name),('type','=',res_ids.type),('pack_info','=',res_ids.pack_info)])
                            browse_obj = rate_obj.browse(cr,uid,search_ids)
                            if browse_obj.shipping_response_id.id < res_ids.id :
                                rate_obj.write(cr, uid, search_ids, {'rate':res_ids.rate,'shipping_response_id':res_ids.id,'weight':res_ids.weight}, context)
                        else:
                            check_name_list_fedex.append(res_ids.name)
                            check_list_fedex.append(res_ids.pack_info+res_ids.name)
                            val = {
                                 'pack_info':res_ids.pack_info,
                                 'shipping_response_id':res_ids.id,
                                 'name':res_ids.name,
                                 'type':res_ids.type,
                                 'weight':res_ids.weight,
                                 'rate':res_ids.rate,
                             }
                            rate_obj.create(cr, uid, val)
                    else:
                            check_name_list_fedex.append(res_ids.name)
                            check_list_fedex.append(res_ids.pack_info+res_ids.name)
                            val = {
                                 'pack_info':res_ids.pack_info,
                                 'shipping_response_id':res_ids.id,
                                 'name':res_ids.name,
                                 'type':res_ids.type,
                                 'weight':res_ids.weight,
                                 'rate':res_ids.rate,
                             }
                            rate_obj.create(cr, uid, val)
                self.pool.get('stock.picking').write(cr, uid, [res_ids.picking_id.id],{
                                                                                        'is_multiple_label':True
                                                                                       }, context=None)
        return {
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'compare.shipping.rates',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
#             'search_view_id': id,
        }
        
        
        
        
    ## update the shipping rate and create invoice of handling charges product ............................. 
    def _create_invoice_from_picking(self, cr, uid, picking, vals, context=None):
        invoice_obj = self.pool.get('account.invoice')
        response_obj = self.pool.get('shipping.response')
        invoice_line_obj = self.pool.get('account.invoice.line')
        maping_list = None
        total_rate = 0.0
        invoice_id = super(stock_picking, self)._create_invoice_from_picking(cr, uid, picking, vals, context=context)
        for picking_record in self.browse(cr, uid, [picking.id]):
            if not picking_record.is_customer_account:
                maping_list = response_obj.search(cr, uid, [('picking_id','=',picking_record.id),('is_label_genrated','=',True)])
        if maping_list:        
            for line in response_obj.browse(cr, uid, maping_list):
                total_rate = total_rate + float(line.rate) 
            invoice = invoice_obj.browse(cr, uid, invoice_id, context=context)
            invoice_line_obj.write(cr, uid, [invoice.invoice_line.id], {'price_unit':total_rate})
        #else:
        #    invoice = invoice_obj.browse(cr, uid, invoice_id, context=context)
        #    for line in invoice.invoice_line:
        #        invoice_line_obj.unlink(cr, uid, [line.id])
        ## for handling product if add in stock config.settings ..................        
        stk_config_obj = self.pool.get('stock.config.settings')
        values = stk_config_obj.default_get(cr, uid, ['producut_id'], context=context)
        pricelist_values = stk_config_obj.default_get(cr, uid, ['priclist_id'], context=context)
        
        if values.has_key('product_id') and values.has_key('priclist_id'):
            if values['product_id'] and pricelist_values['priclist_id']:
                prod_id = int(values['product_id'])
                price_list_id = int(pricelist_values['priclist_id'])
                registry = openerp.registry(cr.dbname)
                pricelist_pool = registry.get('product.pricelist')
                product_obj = self.pool.get('product.product').browse(cr, uid, prod_id)
                pricelist = pricelist_pool.browse(cr, uid, price_list_id)
                    
#                 if picking.partner_id.price_list_for_invoice:
#                 pricelist =  picking.partner_id.price_list_for_invoice
                price = pricelist_pool.price_get(cr,uid,[pricelist.id],
                     prod_id, picking.no_of_packets or 1.0, picking.partner_id.id, {
                        'uom': product_obj.uom_po_id.id,
                        'date': time.strftime('%Y-%m-%d'),
                        })[pricelist.id]
                if not price:
                    raise osv.except_osv(_('Warning'), _('Configure product not in handling pricelist'))
                    
                acc_id = product_obj.product_tmpl_id.categ_id.property_account_income_categ.id
                product_qty = picking.no_of_packets
                line_id = invoice_line_obj.create(cr, uid,{'product_id':values['product_id'],'quantity':product_qty,'invoice_id':invoice_id,'account_id':acc_id,'name':product_obj.name,'price_unit':price or 1.0})
                line_record = invoice_line_obj.browse(cr, uid, line_id)
                invoice_line_obj.write(cr, uid, [line_record.id], {'price_subtotal':price})
#                 else:
#                     raise osv.except_osv(_('Warning'), _('Please define handling misc. pricelist for partner'))
                        
        else:
            raise osv.except_osv(_('Warning'), _('Please Configure the Service Product and Handling Pricelist'))
                
        return invoice_id
    
     
stock_picking()    

class stock_move(osv.osv):
    _inherit = 'stock.move'

    def _cal_move_weight_new(self, cr, uid, ids, name, args, context=None):
        res = {}
        uom_obj = self.pool.get('product.uom')
        for move in self.browse(cr, uid, ids, context=context):
            weight = weight_net = 0.00
            
            converted_qty = move.product_qty
            if move.product_uom.id <> move.product_id.uom_id.id:
                converted_qty = uom_obj._compute_qty(cr, uid, move.product_uom.id, move.product_qty, move.product_id.uom_id.id)

            if move.product_id.weight > 0.00:
                weight = (converted_qty * move.product_id.weight)

            if move.product_id.weight_net > 0.00:
                    weight_net = (converted_qty * move.product_id.weight_net)

            res[move.id] =  {
                            'weight': weight,
                            'weight_net': weight_net,
                            }
        return res

    _columns = {
        'weight': fields.function(_cal_move_weight_new, method=True, type='float', string='Weight', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_move_weight',
                  store={
                 'stock.move': (lambda self, cr, uid, ids, c=None: ids, ['product_id', 'product_qty', 'product_uom'], 20),
                 }),
        'weight_net': fields.function(_cal_move_weight_new, method=True, type='float', string='Net weight', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_move_weight',
                  store={
                 'stock.move': (lambda self, cr, uid, ids, c=None: ids, ['product_id', 'product_qty', 'product_uom'], 20),
                 }),
        }

stock_move()
