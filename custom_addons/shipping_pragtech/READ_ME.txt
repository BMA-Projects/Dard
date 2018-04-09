Following Changes Needed to use Fedex Python Package:

1) Download  wsdl-test_ShipService_v10.wsdl from http://www.phpclasses.org/browse/file/42740.html

2) Put it in installed python fedex package e.g /usr/local/lib/python2.7/dist-packages/fedex/wsdl/ ShipService_v10.wsdl


3) Make following changes in /usr/local/lib/python2.7/dist-packages/services/ship_service.py
	change the old wsdl file name from "ShipService_v7.wsdl" to "ShipService_v10.wsdl", change the old "major" number from 7 to 10.

4) Add Below lines in your python code before:  shipment.add_package(package1) statement
	
	del shipment.RequestedShipment.EdtRequestType
        del package1.PhysicalPackaging



For more information follow the links:
https://github.com/gtaylor/python-fedex/issues/13

http://www.phpclasses.org/browse/file/42740.html
