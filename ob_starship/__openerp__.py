# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'Starship Integration',
    'version': '1.0',
    'category': 'Shipping',
    'description': """
Integration of BMA with Starship
===========================================================================
Story : 2591

BMA sends following information to StarShip :

    * Order shipping address
    * Item number and description.
    * Published item cost.

At the time of Sale Order confirmation :
    * It creates a new XML file on Specified location for Requests to Starship.

Starship reads the requests and stores the response in an another XML file.

BMA runs a cron job to read the XML file every fixed interval from the Response location.
    * Finds the Deliver order and updates it with the below information.
        * Shipping method
        * Tracking number
        * Shipment cost
    * It updates the Requested file with a status Done so that it doesnt read the file again.
    """,
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'depends': ['base','sale','shipping_pragtech','stock_account'],
    'data': [
        'security/ir.model.access.csv',
        'ob_starship_data.xml',
        'starship_view.xml',
        'starship_menu.xml',
        'sale_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=
