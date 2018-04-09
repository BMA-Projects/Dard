import re
import math
import urllib
from urllib2 import Request, urlopen, URLError, quote
import xml.etree.ElementTree as etree
from openerp.osv import osv
from openerp.tools.translate import _
from openid.server.trustroot import RP_RETURN_TO_URL_TYPE

ups_service_type = {
    '01': 'Next Day Air',
    'ups_1DA': 'Next Day Air',
    '02': 'Second Day Air',
    'ups_2DA': 'Second Day Air',
    '03': 'Ground',
    'ups_GND': 'Ground',
    '07': 'Worldwide Express',
    '08': 'Worldwide Expedited',
    '11': 'Standard',
    '12': 'Three-Day Select',
    'ups_3DS': 'Three-Day Select',
    '13': 'Next Day Air Saver',
    'ups_1DP': 'Next Day Air Saver',
    '14': 'Next Day Air Early AM',
    'ups_1DM': 'Next Day Air Early AM',
    '54': 'Worldwide Express Plus',
    '59': 'Second Day Air AM',
    '65': 'Saver',
}

class Error(object):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        print '%s' % (self.message)
        raise

class Shipping(object):
    def __init__(self, weight, length, width, height, shipper,receipient):
        self.length = length
        self.width = width
        self.height = height
        self.weight = weight
        self.shipper = shipper
        self.receipient = receipient

class UPSShipping(Shipping):
    def __init__(self, weight, length, width, height, shipper,receipient):
        if (length + 2*width + 2*height) > 165:
            raise osv.except_osv(_("Exception: UPS !"), _("Package exceeds the maximum size total constraints of 165 inches (length + girth, where girth is 2 x width plus 2 x height). "))
        super(UPSShipping, self).__init__(weight,length, width, height,shipper,receipient)

    def send(self,):
        datas = self._get_data()
        data = datas[0]
        api_url = datas[1]
        try:
            request = Request(api_url, data)
            response_text = urlopen(request).read()
            response = self.__parse_response(response_text)
        except URLError, e:
            if hasattr(e, 'reason'):
                print 'Could not reach the server, reason: %s' % e.reason
            elif hasattr(e, 'code'):
                print 'Could not fulfill the request, code: %d' % e.code
            raise
        return response
        

    def __parse_response(self, response_text):
        root = etree.fromstring(response_text)
        status_code = root.findtext('Response/ResponseStatusCode')
        if status_code != '1':
            raise osv.except_osv(_("Exception: UPS !"), _(root.findtext('Response/Error/ErrorDescription')))
        else:
            response = self._parse_response_body(root)
        return response

class UPSRateRequest(UPSShipping):

    def __init__(self, ups_info, pickup_type_ups, service_type_ups, packaging_type_ups, weight, shipper,receipient, length, width, height, cust_default, sys_default):
        self.type = 'UPS'
        self.ups_info = ups_info
        self.pickup_type_ups = pickup_type_ups
        self.service_type_ups = service_type_ups
        self.packaging_type_ups = packaging_type_ups
        self.sr_no = 1 if cust_default and cust_default.split('/')[0] == self.type and cust_default.split('/')[1] == self.service_type_ups else 9
        self.sr_no = 2 if self.sr_no == 9 and sys_default and sys_default.split('/')[0] == self.type and sys_default.split('/')[1] == self.service_type_ups else self.sr_no
        super(UPSRateRequest, self).__init__(weight,length, width, height,shipper,receipient)

    def _get_data(self):
        data = []
        data.append("""<?xml version=\"1.0\"?>
        <AccessRequest xml:lang=\"en-US\">
            <AccessLicenseNumber>%s</AccessLicenseNumber>
            <UserId>%s</UserId>
            <Password>%s</Password>
        </AccessRequest>
        <?xml version=\"1.0\"?>
        <RatingServiceSelectionRequest xml:lang=\"en-US\">
            <Request>
                <TransactionReference>
                    <CustomerContext>Rating and Service</CustomerContext>
                    <XpciVersion>1.0001</XpciVersion>
                </TransactionReference>
                <RequestAction>Rate</RequestAction>
                <RequestOption>Rate</RequestOption>
            </Request>
        <PickupType>
            <Code>%s</Code>
        </PickupType>
        <Shipment>
            <Shipper>
                <Address>
                    <PostalCode>%s</PostalCode>
                    <CountryCode>%s</CountryCode>
                </Address>
            <ShipperNumber>%s</ShipperNumber>
            </Shipper>
            <ShipTo>
                <Address>
                    <PostalCode>%s</PostalCode>
                    <CountryCode>%s</CountryCode>
                <ResidentialAddressIndicator/>
                </Address>
            </ShipTo>
            <ShipFrom>
                <Address>
                    <PostalCode>%s</PostalCode>
                    <CountryCode>%s</CountryCode>
                </Address>
            </ShipFrom>
            <Service>
                <Code>%s</Code>
            </Service>
            <Package>
                <PackagingType>
                    <Code>%s</Code>
                </PackagingType>
                <PackageWeight>
                    <UnitOfMeasurement>
                        <Code>LBS</Code>
                    </UnitOfMeasurement>
                    <Weight>%s</Weight>
                </PackageWeight>
                <Dimensions>
                    <UnitOfMeasurement>
                        <Code>IN</Code>
                    </UnitOfMeasurement>
                    <Length>%s</Length>
                    <Width>%s</Width>
                    <Height>%s</Height>
                </Dimensions>
            </Package>
        </Shipment>
        </RatingServiceSelectionRequest>""" % (self.ups_info.access_license_no,self.ups_info.user_id,self.ups_info.password,self.pickup_type_ups,self.shipper.zip,self.shipper.country_code,self.ups_info.shipper_no,self.receipient.zip,self.receipient.country_code,self.shipper.zip,self.shipper.country_code,self.service_type_ups,self.packaging_type_ups,self.weight,self.length,self.width,self.height))
        data.append('https://wwwcie.ups.com/ups.app/xml/Rate' if self.ups_info.test else 'https://onlinetools.ups.com/ups.app/xml/Rate')
        return data

    def _parse_response_body(self, root):
        return UPSRateResponse(root, self.weight, self.length, self.width, self.height, self.sr_no)


class UPSRateResponse(object):
    def __init__(self, root, weight, length, width, height,sr_no):
        self.root = root
        self.rate = root.findtext('RatedShipment/TotalCharges/MonetaryValue')
        self.service_type = ups_service_type[root.findtext('RatedShipment/Service/Code')]
        self.weight = weight
        self.length = length
        self.width = width
        self.height = height
        self.sr_no = sr_no


    def __repr__(self):
        return (self.service_type, self.rate, self.weight, self.length, self.width, self.height,self.sr_no)
        

class UPSShipmentConfirmRequest(UPSShipping):
    def __init__(self, ups_info, pickup_type_ups, service_type_ups, packaging_type_ups, weight, length, width, height, shipper,receipient):
        self.type = 'UPS'
        self.ups_info = ups_info
        self.pickup_type_ups = pickup_type_ups
        self.service_type_ups = service_type_ups
        self.packaging_type_ups = packaging_type_ups
        super(UPSShipmentConfirmRequest, self).__init__(weight,length, width, height,shipper,receipient)

    def _get_data(self):
        data = []
        data.append("""
<?xml version="1.0" ?>
<AccessRequest xml:lang='en-US'>
    <AccessLicenseNumber>%s</AccessLicenseNumber>
    <UserId>%s</UserId>
    <Password>%s</Password>
</AccessRequest>
<?xml version="1.0" ?>
<ShipmentConfirmRequest>
    <Request>
         <TransactionReference>
              <CustomerContext>guidlikesubstance</CustomerContext>
              <XpciVersion>1.0001</XpciVersion>
         </TransactionReference>
         <RequestAction>ShipConfirm</RequestAction>
         <RequestOption>nonvalidate</RequestOption>
    </Request>
    <Shipment>
        <Description>Rate Description</Description>
         <Shipper>
              <Name>%s</Name>
              <AttentionName>%s</AttentionName>
              <PhoneNumber>%s</PhoneNumber>
              <ShipperNumber>%s</ShipperNumber>
              <Address>
                   <AddressLine1>%s</AddressLine1>
                   <City>%s</City>
                   <StateProvinceCode>%s</StateProvinceCode>
                   <CountryCode>%s</CountryCode>
                   <PostalCode>%s</PostalCode>
              </Address>
         </Shipper>
         <ShipTo>
              <CompanyName>%s</CompanyName>
              <AttentionName>%s</AttentionName>
              <PhoneNumber>%s</PhoneNumber>
              <Address>
                   <AddressLine1>%s</AddressLine1>
                   <City>%s</City>
                   <StateProvinceCode>%s</StateProvinceCode>
                   <CountryCode>%s</CountryCode>
                   <PostalCode>%s</PostalCode>
                   <ResidentialAddress />
              </Address>
         </ShipTo>
         <PaymentInformation>
                <Prepaid>
                    <BillShipper>
                        <AccountNumber>%s</AccountNumber>
                    </BillShipper>
                </Prepaid>
        </PaymentInformation>
         <Service>
              <Code>%s</Code>
              <Description>%s</Description>
         </Service>
        <Package>
            
            <PackagingType>
                <Code>%s</Code>
            </PackagingType>
            <PackageWeight>
                <Weight>%s</Weight>
            </PackageWeight>
            <Dimensions>
                <UnitOfMeasurement>
                    <Code>IN</Code>
                </UnitOfMeasurement>
                <Length>%s</Length>
                <Width>%s</Width>
                <Height>%s</Height>
            </Dimensions>
        </Package>
    </Shipment>
    <LabelSpecification>
        <LabelPrintMethod>
            <Code>GIF</Code>
        </LabelPrintMethod>
        <LabelImageFormat>
            <Code>GIF</Code>
        </LabelImageFormat>
    </LabelSpecification>
</ShipmentConfirmRequest>""" % (self.ups_info.access_license_no,self.ups_info.user_id,self.ups_info.password, self.shipper.company_name, self.shipper.name, self.shipper.phone, self.ups_info.shipper_no, self.shipper.address1, self.shipper.city, self.shipper.state_code, self.shipper.country_code, self.shipper.zip, self.receipient.company_name, self.receipient.name, self.receipient.phone, self.receipient.address1, self.receipient.city, self.receipient.state_code, self.receipient.country_code, self.receipient.zip, self.ups_info.shipper_no, self.service_type_ups, ups_service_type[self.service_type_ups], self.packaging_type_ups, self.weight, self.length,self.width,self.height))
#        data.append('https://wwwcie.ups.com/ups.app/xml/ShipConfirm' if self.ups_info.test else 'https://onlinetools.ups.com/ups.app/xml/ShipConfirm')
        data.append('https://onlinetools.ups.com/ups.app/xml/ShipConfirm' if self.ups_info.test else 'https://onlinetools.ups.com/ups.app/xml/ShipConfirm')
        return data

    def _parse_response_body(self, root):
        return UPSShipmentConfirmResponse(root)
        

class UPSShipmentConfirmResponse(object):
    def __init__(self, root):
        self.root = root
        self.shipment_digest = root.findtext('ShipmentDigest')

    def __repr__(self):
        return (self.shipment_digest)

class UPSShipmentAcceptRequest(UPSShipping):
    def __init__(self, ups_info, shipment_digest):
        self.ups_info = ups_info
        self.shipment_digest = shipment_digest

    def _get_data(self):
        data = []
        data.append("""
<?xml version="1.0" ?>
<AccessRequest xml:lang='en-US'>
    <AccessLicenseNumber>%s</AccessLicenseNumber>
    <UserId>%s</UserId>
    <Password>%s</Password>
</AccessRequest>
<?xml version="1.0" ?>
<ShipmentAcceptRequest>
    <Request>
        <RequestAction>ShipAccept</RequestAction>
    </Request>
    <ShipmentDigest>%s</ShipmentDigest>
</ShipmentAcceptRequest>""" % (self.ups_info.access_license_no,self.ups_info.user_id,self.ups_info.password,self.shipment_digest))
        data.append('https://wwwcie.ups.com/ups.app/xml/ShipAccept' if self.ups_info.test else 'https://onlinetools.ups.com/ups.app/xml/ShipAccept')
        return data

    def _parse_response_body(self, root):
        return UPSShipmentAcceptResponse(root)

class UPSShipmentAcceptResponse(object):
    def __init__(self, root):
        self.root = root
        self.tracking_number = root.findtext('ShipmentResults/PackageResults/TrackingNumber')
        self.image_format = root.findtext('ShipmentResults/PackageResults/LabelImage/LabelImageFormat/Code')
        self.graphic_image = root.findtext('ShipmentResults/PackageResults/LabelImage/GraphicImage')
        self.html_image = root.findtext('ShipmentResults/PackageResults/LabelImage/HTMLImage')

    def __repr__(self):
        return (self.tracking_number, self.image_format, self.graphic_image)

class USPSShipping(Shipping):
    def __init__(self, weight, shipper,receipient):
        super(USPSShipping, self).__init__(weight,shipper,receipient)

    def send(self,):
        datas = self._get_data()
        data = datas[0]
        api_url = datas[1]
        values = {}
        values['XML'] = data
        api_url = api_url + urllib.urlencode(values)
        try:
            request = urlopen(api_url)
            response_text = request.read()
            response = self.__parse_response(response_text)
        except URLError, e:
            if hasattr(e, 'reason'):
                print 'Could not reach the server, reason: %s' % e.reason
            elif hasattr(e, 'code'):
                print 'Could not fulfill the request, code: %d' % e.code
            raise
        return response

    def __parse_response(self, response_text):
        root = etree.fromstring(response_text)
#        packages = root.getiterator("Package")
        error_tag = root.find('Package/Error')
        if error_tag:
            raise Exception('USPS %s' % (root.findtext('Package/Error/Description')))
        else:
            response = self._parse_response_body(root)
        return response

class USPSRateRequest(USPSShipping):
    def __init__(self, usps_info, service_type_usps, first_class_mail_type_usps, container_usps, size_usps, width_usps, length_usps, height_usps, girth_usps, weight, shipper, receipient, cust_default=False, sys_default=False):
        self.type = 'USPS'
        self.usps_info = usps_info
        self.service_type_usps = service_type_usps
        self.first_class_mail_type_usps = first_class_mail_type_usps
        self.container_usps = container_usps
        self.size_usps = size_usps
        self.width_usps = width_usps
        self.length_usps = length_usps
        self.height_usps = height_usps
        self.girth_usps = girth_usps
        self.sr_no = 1 if cust_default and cust_default.split('/')[0] == self.type and cust_default.split('/')[1] == self.service_type_usps else 9
        self.sr_no = 2 if self.sr_no == 9 and sys_default and sys_default.split('/')[0] == self.type and sys_default.split('/')[1] == self.service_type_usps else self.sr_no
        super(USPSRateRequest, self).__init__(weight,shipper,receipient)

    def _get_data(self):
        data = []

        service_type = '<Service>' + self.service_type_usps + '</Service>'

        if self.service_type_usps == 'First Class':
            service_type += '<FirstClassMailType>' + self.first_class_mail_type_usps + '</FirstClassMailType>'

        weight = math.modf(self.weight)
        pounds = int(weight[1])
        ounces = round(weight[0],2) * 16

        container = self.container_usps and '<Container>' + self.container_usps + '</Container>' or '<Container/>'

        size = '<Size>' + self.size_usps + '</Size>'
        if self.size_usps == 'LARGE':
            size += '<Width>' + self.width_usps + '</Width>'
            size += '<Length>' + self.length_usps + '</Length>'
            size += '<Height>' + self.height_usps + '</Height>'

            if self.container_usps == 'Non-Rectangular' or self.container_usps == 'Variable' or self.container_usps == '':
                size += '<Girth>' + str(self.girth_usps) + '</Girth>'

        data.append('<?xml version="1.0" ?><RateV4Request USERID="' + self.usps_info.user_id + '"><Revision/><Package ID="1ST">' + service_type + '<ZipOrigination>' + self.shipper.zip + '</ZipOrigination><ZipDestination>' + self.receipient.zip + '</ZipDestination><Pounds>' + str(pounds) + '</Pounds><Ounces>' + str(ounces) + '</Ounces>' + container + size + '<Machinable>true</Machinable></Package></RateV4Request>')
#        data.append("http://testing.shippingapis.com/ShippingAPITest.dll?API=RateV4&" if self.usps_info.test else "http://production.shippingapis.com/ShippingAPI.dll?API=RateV4&")
#         data.append("http://production.shippingapis.com/ShippingApi.dll?API=RateV4&" if self.usps_info.test else "http://production.shippingapis.com/ShippingAPI.dll?API=RateV4&")
        data.append("http://production.shippingapis.com/ShippingApi.dll?API=RateV4&" if self.usps_info.test else "http://production.shippingapis.com/ShippingAPI.dll?API=RateV4&")
#        data.append("http://production.shippingapis.com/ShippingAPITest.dll??API=RateV4&" if self.usps_info.test else "http://production.shippingapis.com/ShippingAPI.dll?API=RateV4&")

        return data

    def _parse_response_body(self, root):
        return USPSRateResponse(root, self.weight, self.sr_no)
    
class USPSRateResponse(object):
    def __init__(self, root, weight, sr_no):
        self.root = root
        self.rate = root.findtext('Package/Postage/Rate')
        self.service_type = str(root.findtext('Package/Postage/MailService')).replace("&lt;sup&gt;&amp;reg;&lt;/sup&gt;","")
        self.weight = weight
        self.sr_no = sr_no


    def __repr__(self):
        return (self.service_type, self.rate, self.weight, self.sr_no)