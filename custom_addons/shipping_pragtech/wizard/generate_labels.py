from openerp.osv import fields, osv
import urllib2
import urllib
from base64 import b64decode
import binascii
import openerp.addons.decimal_precision as dp
import time
import webbrowser

import HTMLParser

from openerp.osv import fields, osv

h = HTMLParser.HTMLParser()
import httplib
from openerp.addons.shipping_pragtech import shippingservice
from openerp.addons.shipping_pragtech import miscellaneous
from openerp.addons.shipping_pragtech.miscellaneous import Address

from openerp.addons.shipping_pragtech.xml_dict import dict_to_xml, xml_to_dict

from fedex.services.rate_service import FedexRateServiceRequest
from fedex.services.ship_service import FedexProcessShipmentRequest
from fedex.config import FedexConfig
import suds
from suds.client import Client

from openerp.tools.translate import _
from openerp import  netsvc

# logger = openerp.netsvc.Logger()
import math
import socket
import urllib2
try:
    from PIL import Image
except ImportError:
    import Image

import logging 
from fedex.services.address_validation_service import FedexAddressValidationRequest 


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
    
    

class generate_labels(osv.osv_memory):
    _name = "generate.labels"
    _description = "Generate selected labels"
    
    
#     def onchange_select_type(self, cr, uid, ids, type, context=None):
#         lble_obj = self.pool.get('generate.labels_details')
#         ttype_ids = lble_obj.search(cr, uid, [('name','=',type)])
#         print ttype_ids,'--------------------------jj'
#         for line in lble_obj.browse(cr, uid, ttype_ids):
#             if line.name == type:
# #                     
#                 print '-----------------------------------123'
#                 return {'value':{line.is_label_genrated:True}}
#     
#     
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

    
    
    _columns = {
                    'name':fields.char("Name",size=250),
                    'picking_id' : fields.many2one('stock.picking','Picking'),
                    'shipping_labels_ids':fields.one2many('generate.labels_details', 'labels_id', 'Shipping Quotes' ),
                    'shipping_type' : fields.selection([
                                                ('FedEx','FedEx'),
                                                ('UPS','UPS'),
                                                ('USPS','USPS'),
                                            ],'Shipping Type'),
                    'service_type_ups' : fields.selection([
                                ('Next Day Air','Next Day Air'),
                                ('Second Day Air','Second Day Air'),
                                ('Ground','Ground'),
                                ('Worldwide Express','Worldwide Express'),
                                ('Worldwide Expedited','Worldwide Expedited'),
                                ('Standard','Standard'),
                                ('Three-Day Select','Three-Day Select'),
                                ('Next Day Air Saver','Next Day Air Saver'),
                                ('Next Day Air Early AM','Next Day Air Early AM'),
                                ('Worldwide Express Plus','Worldwide Express Plus'),
                                ('Second Day Air AM','Second Day Air AM'),
                                ('Saver','Saver'),
                            ],'Service Type'),
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
                'service_type_usps' : fields.selection(_get_service_type_usps, 'Service Type', size=100),
                                
                
                }
    
    ## getting shipping quoutes information ...................
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(generate_labels, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')
 
        if not picking_ids or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        assert active_model in ('stock.picking'), 'Bad context propagation'
        picking_id, = picking_ids
        picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
        items = []
        packs = []
#         if not picking.pack_operation_ids:
#             picking.do_prepare_partial()
        for op in picking.response_usps_ids:
            item = {
                    'name' : op.name,
                    'type' : op.type,
                    'rate' : op.rate,
                    'picking_id' : op.picking_id.id, #Change the ids[0] when switch to create
                    'weight' : op.weight,
                    'sys_default' : False,
                    'cust_default' : False,
                    'sr_no' : op.sr_no,
                    'pack_info':op.pack_info, 
                    'sequence':op.sequence
            }
            items.append(item)
            packs.append(item)
#         self.pool.get('generate.labels_details').create(cr, uid, item, context=None)
         
        res.update(shipping_labels_ids=packs, picking_id=picking_id)
        return res
    
    def generate_shipping_report(self,cr, uid, ids, context=None):
        
        response_obj = self.pool.get('shipping.response')
        sr_browse_obj = response_obj.browse(cr, uid, ids[0])
        vals = {
                      'total_shipping_cost' : sr_browse_obj.rate,
                      'shipping_type' : sr_browse_obj.name,
              }
        sp_browse_obj = self.pool.get('stock.picking').browse(cr, uid,sr_browse_obj.picking_id.id)
        vals['shipping_carrier'] = sr_browse_obj.picking_id.carrier_id.id
        vals['delivery_date'] = sr_browse_obj.picking_id.min_date
        vals['delivery_order'] = sr_browse_obj.picking_id.name
        vals['sale_order'] = sr_browse_obj.picking_id.sale_id.name
        vals['state'] = sr_browse_obj.picking_id.state
        vals['customer'] = sr_browse_obj.picking_id.sale_id.partner_id.id
        vals['sale_order_date'] = sr_browse_obj.picking_id.sale_id.date_order
        
        rp_browse_obj = self.pool.get('res.partner').browse(cr, uid, sp_browse_obj.sale_id.partner_id.id)
        vals['delivery_state'] = rp_browse_obj.state_id.id
        vals['delivery_country'] = rp_browse_obj.country_id.id
        
        del_address = ''
        if rp_browse_obj.street:
            del_address+= str(rp_browse_obj.street) + " "
        if rp_browse_obj.street2:
            del_address+= str(rp_browse_obj.street2) + " "
        if rp_browse_obj.city:
            del_address+= str(rp_browse_obj.city) + " "
        if rp_browse_obj.zip:
            del_address+= str(rp_browse_obj.zip)
        vals['delivery_address'] = del_address
        if self.pool.get('shipping.report').create(cr, uid, vals):
            return True
    
    ## filter for ups shipping service using shipping type and service type on wizard one2many field 
    def onchange_ups_type(self, cr, uid, ids, ship_type, service_type_ups, picking_id, context=None):
        items = []
        map_ids = None
        map_list = []
        response_obj = self.pool.get('shipping.response')
#         picking = self.pool.get('stock.picking').browse(cr, uid, [picking_id], context=context)
        if ship_type and service_type_ups:
            map_ids = response_obj.search(cr, uid, [('type','=',ship_type),('name','=',service_type_ups),('picking_id','=',picking_id)])
            if map_ids:
                for line in response_obj.browse(cr, uid, map_ids):
                    item = {
                            'name' : line.name,
                            'type' : line.type,
                            'rate' : line.rate,
                            'picking_id' : picking_id, #Change the ids[0] when switch to create
                            'weight' : line.weight,
                            'length' : line.length,
                            'width' : line.width,
                            'height' : line.height,
                            'sys_default' : False,
                            'cust_default' : False,
    #                         'sr_no' : line.sr_no,
                            'pack_info':line.pack_info, 
    #                         'sequence':line.sequence
                    }
                    items.append(item)
            return {'value':{'shipping_labels_ids':items}}
        else:
            return {}
        
        
    ## filter for fedex shipping service using shipping type and service type on wizard one2many field
    def onchange_fedex_type(self, cr, uid, ids, ship_type, service_type_fedex, picking_id, context=None):
        items = []
        map_ids = None
        map_list = []
        response_obj = self.pool.get('shipping.response')
#         picking = self.pool.get('stock.picking').browse(cr, uid, [picking_id], context=context)
        if ship_type and service_type_fedex:
            map_ids = response_obj.search(cr, uid, [('type','=',ship_type),('name','=',service_type_fedex),('picking_id','=',picking_id)])
            if map_ids:
                for line in response_obj.browse(cr, uid, map_ids):
                    item = {
                            'name' : line.name,
                            'type' : line.type,
                            'rate' : line.rate,
                            'picking_id' : picking_id, #Change the ids[0] when switch to create
                            'weight' : line.weight,
                            'length' : line.length,
                            'width' : line.width,
                            'height' : line.height,
                            'sys_default' : False,
                            'cust_default' : False,
    #                         'sr_no' : line.sr_no,
                            'pack_info':line.pack_info, 
    #                         'sequence':line.sequence
                    }
                    items.append(item)
            return {'value':{'shipping_labels_ids':items}}
        else:
            return {}
        
    ## filter for usps shipping service using shipping type and service type on wizard one2many field
    def onchange_usps_type(self, cr, uid, ids, ship_type, service_type_usps, picking_id, context=None):
        items = []
        map_ids = None
        map_list = []
        response_obj = self.pool.get('shipping.response')
#         picking = self.pool.get('stock.picking').browse(cr, uid, [picking_id], context=context)
        if ship_type and service_type_usps:
            if service_type_usps == 'All':
                map_ids = response_obj.search(cr, uid, [('type','=',ship_type),('name','=','Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt;'),('picking_id','=',picking_id)])
            else:
                map_ids = response_obj.search(cr, uid, [('type','=',ship_type),('name','=',service_type_usps),('picking_id','=',picking_id)])
                
            if map_ids:
                for line in response_obj.browse(cr, uid, map_ids):
                    item = {
                            'name' : line.name,
                            'type' : line.type,
                            'rate' : line.rate,
                            'picking_id' : picking_id, #Change the ids[0] when switch to create
                            'weight' : line.weight,
                            'sys_default' : False,
                            'cust_default' : False,
        #                         'sr_no' : line.sr_no,
                            'pack_info':line.pack_info, 
        #                         'sequence':line.sequence
                    }
                    items.append(item)
            return {'value':{'shipping_labels_ids':items}}
        else:
            return {}
        
    def onchange_shipping_type(self, cr, uid, ids, ship_type, picking_id, context=None):
        
        items = []
        map_ids = None
        map_list = []
        response_obj = self.pool.get('shipping.response')
#         picking = self.pool.get('stock.picking').browse(cr, uid, [picking_id], context=context)
        if ship_type:
            map_ids = response_obj.search(cr, uid, [('type','=',ship_type),('picking_id','=',picking_id),('is_label_genrated','!=',True)])
            if map_ids:
                for line in response_obj.browse(cr, uid, map_ids):
                    item = {
                            'name' : line.name,
                            'type' : line.type,
                            'rate' : line.rate,
                            'picking_id' : picking_id, #Change the ids[0] when switch to create
                            'weight' : line.weight,
                            'length' : line.length,
                            'width' : line.width,
                            'height' : line.height,
                            'sys_default' : False,
                            'cust_default' : False,
        #                         'sr_no' : line.sr_no,
                            'pack_info':line.pack_info, 
        #                         'sequence':line.sequence
                    }
                    items.append(item)
            if ship_type == 'FedEx':
                return {'value':{'shipping_labels_ids':items,'service_type_ups':None,'service_type_usps':None}}
            if ship_type == 'UPS':
                return {'value':{'shipping_labels_ids':items,'service_type_fedex':None,'service_type_usps':None}}
            if ship_type == 'USPS':
                return {'value':    {'shipping_labels_ids':items,'service_type_ups':None,'service_type_fedex':None}}
        else:
            return {}
        
        
        
    
    ## generate selected labels ........................
    def generate_labels(self, cr, uid, ids, context={}, error=True):

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
        shipp_response_obj = self.pool.get('shipping.response')
        stockpicking_obj = self.pool.get('stock.picking')
        pack_weight_obj = self.pool.get('pack.weight')
        attachment_pool = self.pool.get('ir.attachment')
        label_details_line = self.pool.get('generate.labels_details')
        shippingresp_lnk = self.browse(cr,uid,ids[0])
        for wizard_obj in self.browse(cr, uid, ids[0]):
            seq_list = []
            map_list = []
            picking_id = None
#             ship_response_id = None
            ship_response_list = None
            
            ## for checking if any sequence are same or not while generating label .............
#             for shipment_line in wizard_obj.shipping_labels_ids:
#                 if shipment_line.is_label_genrated:
#                     if shipment_line.sequence not in seq_list:
#                         seq_list.append(shipment_line.sequence)
#                         map_list.append(shipment_line.id)
#                         picking_id = shipment_line.picking_id
#                     else:
#                         raise osv.except_osv(_('Error'), _('You can not generate another label of same sequence'))
            
            ## search for mapping the selected sequence ...............
#             for shipment_line in label_details_line.browse(cr, uid, map_list):
#                 print shipment_line
#                 if shipment_line.is_label_genrated:
#                     ship_response_id = shipp_response_obj.search(cr, uid, [('picking_id','=',shipment_line.picking_id.id),('sequence','=', shipment_line.sequence),('type','=', shipment_line.type)])
#                     ship_response_list.append(ship_response_id[0])
            ## for generating labels of mapped list .............................   
            ## it is for ups label generation ...................
            if wizard_obj.shipping_type and wizard_obj.service_type_ups:
                ship_response_list = shipp_response_obj.search(cr, uid, [('picking_id','=',wizard_obj.picking_id.id),('type','=', wizard_obj.shipping_type),('name','=',wizard_obj.service_type_ups)])
                picking_id = wizard_obj.picking_id
#                 print ship_response_id,'----------------------ggg'
#                 ship_response_list.append(ship_response_id)
            ## it is for ups label generation ...................
            elif wizard_obj.shipping_type and wizard_obj.service_type_fedex:
                ship_response_list = shipp_response_obj.search(cr, uid, [('picking_id','=',wizard_obj.picking_id.id),('type','=', wizard_obj.shipping_type),('name','=',wizard_obj.service_type_fedex)])
                picking_id = wizard_obj.picking_id
            
            ## it is for usps label generation ..................
            else: 
                if wizard_obj.service_type_usps == 'All':
                    ship_response_list = shipp_response_obj.search(cr, uid, [('picking_id','=',wizard_obj.picking_id.id),('type','=', wizard_obj.shipping_type),('name','=','Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt;')])
                else:
                    ship_response_list = shipp_response_obj.search(cr, uid, [('picking_id','=',wizard_obj.picking_id.id),('type','=', wizard_obj.shipping_type),('name','=',wizard_obj.service_type_usps)])
                picking_id = wizard_obj.picking_id
            if not ship_response_list:
                raise osv.except_osv(_('Error'), _('This service type of line not exists!'),)
                
            for shippingresp_lnk in shipp_response_obj.browse(cr, uid, ship_response_list):
                     
                move_ids = stockmove_obj.search(cr,uid,[('picking_id','=',shippingresp_lnk.picking_id.id)])
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
                    shipp_response_obj.write(cr, uid, [shippingresp_lnk.id], write_val, context)
                    context['attach_id'] = attach_id
                     
                    ## usps tracking number ..................
                    if tracking_no:
                        stockpicking_obj.write(cr,uid,[shippingresp_lnk.picking_id.id],{'carrier_tracking_ref':tracking_no, 'shipping_label':binascii.b2a_base64(str(b64decode(s_label))), 'shipping_rate': rate})
                        context['track_success'] = True
                        context['tracking_no']=tracking_no
                        shipp_response_obj.write(cr, uid, [shippingresp_lnk.id], {'is_label_genrated':True},context) 
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
                        if not picking_record.fedex_id:
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
                    #shipment.RequestedShipment.ShippingChargesPayment.Payor.AccountNumber = CONFIG_OBJ.account_number
                    shipment.RequestedShipment.ShippingChargesPayment.Payor.ResponsibleParty.AccountNumber = CONFIG_OBJ.account_number #USE THIS
                    logging.basicConfig(level=logging.INFO)
#                     connection = FedexAddressValidationRequest(CONFIG_OBJ)
#          
#                     connection.AddressValidationOptions.CheckResidentialStatus = True
#                     connection.AddressValidationOptions.VerifyAddresses = True
#                     connection.AddressValidationOptions.RecognizeAlternateCityNames = True
#                     connection.AddressValidationOptions.MaximumNumberOfMatches = 3
#              
#                     connection.AddressValidationOptions.StreetAccuracy = 'LOOSE'
#                      
#                     del connection.AddressValidationOptions.DirectionalAccuracy 
#                     del connection.AddressValidationOptions.CompanyNameAccuracy 
#                      
#                     address1 = connection.create_wsdl_object_of_type('AddressToValidate')
#                     address1.CompanyName = receipient.company_name
#                     #address1.Address.StreetLines = ['155 Old Greenville Hwy', 'Suite 103']
#                     address1.Address.StreetLines = receipient.address1
#                     address1.Address.City = receipient.city
#                     address1.Address.StateOrProvinceCode = receipient.state_code
#                     address1.Address.PostalCode = receipient.zip
#                     address1.Address.CountryCode = receipient.country_code
#                     address1.Address.Residential = False
#                     connection.add_address(address1)
#               
#                     ## Send the request and print the response
#                     try:
#                         connection.send_request()
#                     except Exception, e:
#                         raise osv.except_osv(_('Error'), _('%s' % (e,)))
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
                    package1.Dimensions.Length = fedex_servicedetails.package_length
                    package1.Dimensions.Width = fedex_servicedetails.package_width
                    package1.Dimensions.Height = fedex_servicedetails.package_height
                    package1.Dimensions.Units = 'IN'
                    package1.PhysicalPackaging = fedex_servicedetails.physical_packaging_fedex
                    package1.Weight = package1_weight
                    package1.GroupPackageCount = 1
                    # Un-comment this to see the other variables you may set on a package.
         
                    # This adds the RequestedPackageLineItem WSDL object to the shipment. It
                    # increments the package count and total weight of the shipment for you.
                     
#                     del shipment.RequestedShipment.EdtRequestType 
#                     del package1.PhysicalPackaging 
                     
                    shipment.add_package(package1)
         
                    # If you'd like to see some documentation on the ship service WSDL, un-comment
                    # this line. (Spammy).
                    # Un-comment this to see your complete, ready-to-send request as it stands
                    # before it is actually sent. This is useful for seeing what values you can
                    # change.
         
                    # If you want to make sure that all of your entered details are valid, you
                    # can call this and parse it just like you would via send_request(). If
                    # shipment.response.HighestSeverity == "SUCCESS", your shipment is valid.
#                     try:
#                         shipment.send_validation_request()
#                     except Exception, e:
#                         raise osv.except_osv(_('Error'), _('%s' % (e,)))
                              
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
                    shipp_response_obj.write(cr, uid, [shippingresp_lnk.id], write_val, context)
                         
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
                        stockpicking_obj.write(cr,uid,[shippingresp_lnk.picking_id.id],{'carrier_tracking_ref':fedexTrackingNumber, 'shipping_label':binascii.b2a_base64(str(b64decode(ascii_label_data))), 'shipping_rate': fedexshippingrate})
                        
                        context['track_success'] = True
                        shipp_response_obj.write(cr, uid, [shippingresp_lnk.id], {'is_label_genrated':True},context) 
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
                    ups = shippingservice.UPSShipmentConfirmRequest(ups_info, pickup_type_ups, service_type_ups, packaging_type_ups, weight, shippingresp_lnk.length, shippingresp_lnk.width, shippingresp_lnk.height, shipper, receipient)
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
                    stockpicking_obj.write(cr,uid,[shippingresp_lnk.picking_id.id],{'carrier_tracking_ref':ups_response.tracking_number, 'shipping_label':binascii.b2a_base64(str(b64decode(ups_response.graphic_image))), 'shipping_rate': rate})
                    ## ups write tracking refernce and carreier id in pack.weight obj ....
                    pack_id = pack_weight_obj.search(cr, uid, [('picking_id','=',shippingresp_lnk.picking_id.id),('sequence','=',shippingresp_lnk.sequence)])
                    if pack_id:
                        pack_weight_obj.write(cr, uid, pack_id, {'carrier_tracking_ref':ups_response.tracking_number}, context)
                    context['track_success'] = True
                    context['tracking_no'] = ups_response.tracking_number
                    shipp_response_obj.write(cr, uid, [shippingresp_lnk.id], {'is_label_genrated':True},context)
                    
                    write_val={}
                    write_val['fedex_attach_id']=0
                    write_val['usps_attach_id']=0
                    if type(ups_attachment_id) == type([]):
                        write_val['ups_attach_id']=ups_attachment_id[0]
                    else:
                        write_val['ups_attach_id']=ups_attachment_id
                          
                    shipp_response_obj.write(cr,uid,[shippingresp_lnk.id],write_val,context)
                 
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
                    self.pool.get('stock.picking').write(cr,uid,[shippingresp_lnk.picking_id.id],{'carrier_id':carrier_ids[0]})
                    self.generate_shipping_report(cr,uid,[shippingresp_lnk.id],context)
                    pack_id = pack_weight_obj.search(cr, uid, [('picking_id','=',shippingresp_lnk.picking_id.id),('sequence','=',shippingresp_lnk.sequence)])
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
            stockpicking_obj.do_transfer(cr, uid, [picking_id.id], context)
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_write(uid, 'stock.picking', picking_id.id, cr)
            wf_service.trg_write(uid, 'sale.order', picking_id.sale_id.id, cr)
            saleorder_obj.write(cr, uid, [picking_id.sale_id.id], {'client_order_ref':context['tracking_no'], 'carrier_id':carrier_ids[0]})
 
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
             
            shipp_response_obj.write(cr, uid, ids, {'label_genrated':True}, context)   
            return True
         
        else:
            return False 
    
generate_labels()

class generate_labels_details(osv.osv_memory):
    _name = "generate.labels_details"
    _columns = {
                    'name': fields.char('Service Type', size=100, ),
                    'type': fields.char('Shipping Type', size=64, ),
                    'rate': fields.char('Rate', size=64,),
                    'weight' : fields.float('Weight'),
                    'cust_default':fields.boolean('Customer Default'),
                    'sys_default' : fields.boolean('System Default'),
                    'sr_no' : fields.integer('Sr. No'),
                    'selected' : fields.boolean('Selected'),
                    'picking_id' : fields.many2one('stock.picking','Picking'),
                    'fedex_attach_id':fields.integer("Attachment ID"),
                    'ups_attach_id':fields.integer("Attachment ID"),
                    'usps_attach_id':fields.integer("Attachment ID"),
                    'is_label_genrated':fields.boolean('Select For Label Generate'),
                    'label_genrated':fields.boolean('Label Generated?'),
#                     'carrier_track_no':fields.function(_get_carrier_tracking, string="Carrier Tracking Number", type='char', store=False),
                    'pack_info':fields.char("Packages", size=100),
                    'sequence':fields.integer('Sequence'),
                    'labels_id':fields.many2one('generate.labels', 'Labels')
                
                }
generate_labels_details()
