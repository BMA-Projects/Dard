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
from openerp.tools.translate import _
import datetime
import urllib
import urllib2
import xmltodict
import json
import xmlrpclib
import base64
from openerp import api
import glob
from xml.dom import minidom
import codecs
import sys
from xml.sax.saxutils import escape
from openerp.tools.translate import _
from openerp.exceptions import Warning

sys.stdout = codecs.getwriter('utf8')(sys.stdout)


class sale_order(osv.osv):
    _inherit = "sale.order"

    _columns = {
        'download_link': fields.char("Download Link", size=500, copy=False),
        'shipping_tracker': fields.integer("Shipping Tracker"),
        'ship_line': fields.many2one('sale.order', 'Ship Line', copy=False),
        'carrier': fields.char('Ship Carrier', copy=False),
        'method': fields.char('Ship Method', copy=False),
        'ship_ids': fields.one2many('shipping.charges.line', 'ship_line', 'Ship Charges', copy=False),
        'is_shipped': fields.boolean('Is Shipped ?', copy=False),
        'shipping_done': fields.boolean('Shipped', copy=False),
        'shipping_tracking_numbers': fields.char("Shipping Tracking No.", copy=False)
    }

    def write(self, cr, uid, ids, values, context=None):
        result = super(sale_order, self).write(cr, uid, ids, values, context)
        if values.get('is_shipped', False):
            self.update_sale_orders_with_shipping(cr, uid, ids, context=context)
        return result

    def action_button_confirm(self, cr, uid, ids, context=None):
        starship_request_object = self.pool.get('starship.request')
        request_id = starship_request_object.search(cr, uid, [('active','=',True)])
        request_obj = starship_request_object.browse(cr, uid, request_id)
        has_recipient_account = False
        recipient_account_number = False
        order_name = ''
        for order in self.browse(cr, uid, ids):
            if order.is_test == False:
                raise osv.except_osv(_('Error'), _('Please Check address valid or invalid'))
            if len(str(request_obj.path))>1 and str(request_obj.path).endswith("/"):
                fo = open(request_obj.path+order.name+".xml", "wb")
                path = request_obj.path+order.name+".xml"
            else:
                fo = open(request_obj.path+"/"+order.name+".xml", "wb")
                path = request_obj.path+"/"+order.name+".xml"
            order_name = order.name+'.xml'
            order_id = order.id
            o_name = order.name
            customer_po_no = escape(order.client_po_ref) if order.client_po_ref else ''
            attention = escape(order.partner_shipping_id.attention) if order.partner_shipping_id.attention else ''
            email = order.partner_shipping_id.email if order.partner_shipping_id.email else ''
            company_id = order.company_id.id
            partner_id = order.partner_id.cust_number if order.partner_id.cust_number else ''
            delivery_service_name = order.x_delivery_id.name if order.x_delivery_id else ''

            if order.partner_shipping_id.street and order.partner_shipping_id.name \
                    and order.partner_shipping_id.country_id and order.partner_shipping_id.city\
                    and order.partner_shipping_id.zip and order.partner_shipping_id.state_id:
                street = escape(order.partner_shipping_id.street)
                street2 = escape(order.partner_shipping_id.street2) if order.partner_shipping_id.street2 else ''
                shipping_partner_name = escape(order.partner_shipping_id.name)
                country_id = order.partner_shipping_id.country_id.name
                city = escape(order.partner_shipping_id.city)
                ship_zip = order.partner_shipping_id.zip
                phone = ''
                if order.partner_shipping_id.phone:
                    phone = str(escape(order.partner_shipping_id.phone))
                    if phone.isdigit():
                        phone = phone
                    else:
                        phone = ''
                state_code = order.partner_shipping_id.state_id.code         
                if order.x_3rd_party:
                        has_recipient_account = 'Recipient'
                        recipient_account_number = order.x_ups_fedex
            else:
                raise osv.except_osv(_("Shipping Address Incomplete"),
                                     _("Please check if you have filled the street name, ship to name,"
                                       "country, city, ZIP and state in Shipping Address"))

            data = """<?xml version='1.0' encoding="utf-8"?>
            <SelectResult>
                <Document DocumentType="Orders" DocumentKey="%s" Company="%s">
                    <Header>
                        <Row FieldName="Cust No." Value="%s"/>
                        <Row FieldName="Order No." Value="%s"/>
                        <Row FieldName="Customer PO No." Value="%s"/>
                        <Row FieldName="Attention" Value="%s"/>
                        <Row FieldName="Ship To Address Line 1" Value="%s"/>
                        <Row FieldName="Ship To Address Line 2" Value="%s"/>
                        <Row FieldName="Ship To Name" Value="%s"/>
                        <Row FieldName="Ship To Country" Value="%s"/>
                        <Row FieldName="Ship To City" Value="%s"/>
                        <Row FieldName="Ship To Zip" Value="%s"/>
                        <Row FieldName="Ship To State" Value="%s"/>
                        <Row FieldName="Order Total" Value="%s"/>
                        <Row FieldName="Customer Phone" Value="%s"/>
                        <Row FieldName="Customer Email" Value="%s"/>
                        <Row FieldName="Billing Type" Value="%s"/>
                        <Row FieldName="Billing Account" Value="%s"/>
                        <Row FieldName="Carrier-Service" Value="%s"/>
                    </Header>
                    <LineItems>
                """% (o_name, company_id, partner_id, order_id, customer_po_no, attention, street, street2, shipping_partner_name, country_id,
                      city, ship_zip, state_code, order.amount_total, phone, email, has_recipient_account, recipient_account_number, delivery_service_name)

            sale_order_line_object = self.pool.get('sale.order.line')
            line_ids = sale_order_line_object.search(cr, uid, [('order_id','=',order_id)])
            if line_ids:
                line_data = """"""""
                for line in line_ids:
                    line_obj = sale_order_line_object.browse(cr, uid, [line])
                    if line_obj.product_id.type != 'service':
                        if line_obj.product_id:
                            product_description = escape(line_obj.product_id.name)
                            product_code = escape(line_obj.product_id.default_code) if line_obj.product_id.default_code else '(ID:' + str(line_obj.product_id.id) + ') ' + line_obj.product_id.name
                        else:
                            product_description = ''
                        if line_obj.product_uom:
                            product_uom = escape(line_obj.product_uom.name)
                        else:
                            product_uom = ''
                        line_data = line_data + """
                            <LineItem LineNumber="%s">
                                <Row FieldName="Item No." Value="%s"/>
                                <Row FieldName="Item Description" Value="%s"/>
                                <Row FieldName="Ordered Units" Value="%s"/>
                                <Row FieldName="Item Unit Price" Value="%s"/>
                                <Row FieldName="Item UOM" Value="%s"/>
                            </LineItem>"""% (line_obj.id, product_code,product_description, line_obj.product_uom_qty,
                                             line_obj.price_unit, product_uom)
            end_data = """
                    </LineItems>
                </Document>
            </SelectResult>
            """
            reload(sys)
            sys.setdefaultencoding('utf-8')
            data = data + line_data + end_data

            fo.write(str(data))
            fo.close()

            attachment_obj = self.pool.get('ir.attachment')
            sale_order_obj = self.pool.get('sale.order')

            with open(request_obj.path+"/"+order.name+".xml", "r") as myfile:
                data = myfile.read()
                myfile.close()
            result = base64.b64encode(data)

            attachment_id = attachment_obj.create(cr, uid, {'name': order_name, 'datas_fname': order_name,
                                                            'res_model': 'sale.order', 'res_id': order_id,
                                                            'datas': result})
            download_url = '/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=' + \
                           str(attachment_id)
            sale_order_obj.write(cr, uid, [order_id], {'download_link': download_url})
        id = super(sale_order, self).action_button_confirm(cr, uid, ids, context)
        return id

    def download_starship_request_through_url(self, cr, uid, ids, context=None):
        sale_id = ids[0]
        sale_order_obj = self.pool.get('sale.order')
        sale_order_data = sale_order_obj.browse(cr, uid, [sale_id])
        url = sale_order_data.download_link
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')

        date_order = datetime.datetime.now()
        date_order_new = date_order.date()
        ship_dt = sale_order_data.ship_dt
        ship_dt = datetime.datetime.strptime(ship_dt, '%Y-%m-%d').date()
#         if not date_order_new >= ship_dt:
#             raise Warning(_('You cannot do shipping before the ship date !'))
        if len(url) > 1:
            return {
                "type": "ir.actions.act_url",
                "url": str(base_url)+str(url),
                "target": "self",
            }
        else:
            return

    @api.model
    def update_sale_orders_with_shipping(self, ids):
        # for order in self.search([('state', 'in', ('progress', 'manual')),('ship_ids', '=', None)]): # OLD CODE
        if ids:
            self = self.browse(ids[0])  # order # OLD CODE
            if self.ship_ids:
                self.ship_ids = False
            shipping_charges_line_obj = self.env['shipping.charges.line']
            sale_order_obj = self.env['sale.order']
            attachment_obj = self.env['ir.attachment']
            shipping_tracking_numbers = set()

            all_ship_ids = []
            ship_ids_old = []
            new_created_shipping = []

            order_id = self.id
            has_attachment = False
            once = True
            attachments = attachment_obj.search([('res_id', '=', order_id), ('res_model', '=', 'sale.order'),
                                                     ('name', 'ilike', 'ShipResult')])
            # Iterating attachments which are the ShipResults attached to the Sale Order
            # attachments = attachments.sorted(reverse=True)
            if attachments:
                attachment_ids = attachments.ids
                attachment_ids.sort(reverse=True)
                attachments = attachment_obj.browse(attachment_ids)

            status = False
            for attachment in attachments:
                if once:
                    once = False
                    has_attachment = True
                    xml_content = attachment.index_content
                    xml_parse = xmltodict.parse(xml_content)
                    result = json.dumps(xml_parse)
                    result = json.loads(result)
                    for name_value in result.get('WriteShipment', '').get('SourceDocument', '').get('FreightInfo', '').get('Shipment', '').get('NameValue', ''):
                        if name_value.get('@Name', '') == 'Status':
                            status = name_value.get('@Value', 'Empty')

                    temp_list = []
                    type_pack = type(result.get('WriteShipment', '').get('Packaging', '').get('Package', ''))

                    if type_pack is dict:
                        temp_list.append(result.get('WriteShipment', '').get('Packaging', '').get('Package', ''))
                    else:
                        temp_list = result.get('WriteShipment', '').\
                            get('Packaging', '').get('Package', '')  # Convert Dict to a List if its not a List

                    for package in temp_list:                        # Iterate Packages in a Response to create the
                        for row in package.get('Row', ''):           # shipping details
                            if row.get('@Name', '') == 'Tracking Number':
                                tracking_number = row.get('@Value', 'Empty')
                                shipping_tracking_numbers.add(tracking_number)
                            if row.get('@Name', '') == 'Package Number':
                                package_number = row.get('@Value', 'Empty')

                            # Grand Total
                            if row.get('@Name', '') == 'List Charges Total':
                                list_charges_total = row.get('@Value', 'Empty')
                                charge_name_total = 'Grand Total'
                            if row.get('@Name', '') == 'Applied Charges Total':
                                applied_charges_total = row.get('@Value', 'Empty')
                            if row.get('@Name', '') == 'Contract Charges Total':
                                contract_charges_total = row.get('@Value', 'Empty')

                            # Freight Charges
                            if row.get('@Name', '') == 'List Charges Freight Charges':
                                list_freight_charges_total = row.get('@Value', 'Empty')
                                charge_name_freight = 'Total Freight Charges'
                            if row.get('@Name', '') == 'Applied Charges Freight Charges':
                                applied_freight_charges_total = row.get('@Value', 'Empty')
                            if row.get('@Name', '') == 'Contract Charges Freight Charges':
                                contract_freight_charges_total = row.get('@Value', 'Empty')

                            # Accessorial Charges
                            if row.get('@Name', '') == 'List Charges Accessorial Charges':
                                list_charges_accessorial_total = row.get('@Value', 'Empty')
                                charge_name_accessorial = 'Total Accessorial Charges'
                            if row.get('@Name', '') == 'Applied Charges Accessorial Charges':
                                applied_charges_accessorial_total = row.get('@Value', 'Empty')
                            if row.get('@Name', '') == 'Contract Charges Accessorial Charges':
                                contract_charges_accessorial_total = row.get('@Value', 'Empty')

                            # Surcharges
                            if row.get('@Name', '') == 'List Charges Surcharges':
                                list_charges_surcharges_total = row.get('@Value', 'Empty')
                                charge_name_surcharges = 'Total Surcharges'
                            if row.get('@Name', '') == 'Applied Charges Fuel Surcharge':
                                applied_charges_surcharge_total = row.get('@Value', 'Empty')
                            if row.get('@Name', '') == 'Contract Charges Surcharges':
                                contract_charges_surcharges_total = row.get('@Value', 'Empty')

                            # Discounts
                            if row.get('@Name', '') == 'List Charges Discounts':
                                list_charges_discounts_total = row.get('@Value', 'Empty')
                                charge_name_discounts = 'Total Discounts'
                            if row.get('@Name', '') == 'Applied Charges Total':
                                applied_charges_discounts_total = 0
                            if row.get('@Name', '') == 'Contract Charges Discounts':
                                contract_charges_discounts_total = row.get('@Value', 'Empty')

                            # Misc
                            if row.get('@Name', '') == 'List Charges Misc Charges':
                                list_charges_misc_total = row.get('@Value', 'Empty')
                                charge_name_misc = 'Total Misc Charges'
                            if row.get('@Name', '') == 'Applied Charges Handling Fee':
                                applied_charges_handling_total = row.get('@Value', 'Empty')
                            if row.get('@Name', '') == 'Contract Charges Misc Charges':
                                contract_charges_handling_total = row.get('@Value', 'Empty')

                        for row in result.get('WriteShipment', '').get('SourceDocument', '').get('FreightInfo', '').\
                                get('Shipment', '').get('NameValue', ''):
                            if row.get('@Name', '') == 'Carrier':
                                service = row.get('@Value', 'Empty')
                            if row.get('@Name', '') == 'Service':
                                method = row.get('@Value', 'Empty')
                            if row.get('@Name', '') == 'Delivery Date':
                                delivery_date = row.get('@Value', 'Empty')
                            if row.get('@Name', '') == 'List Charges Total':
                                price_total = row.get('@Value', 'Empty')
                            if row.get('@Name', '') == 'Order Number':
                                order_name = row.get('@Value', 'Empty')
                                order_id =  sale_order_obj.search([('name', '=', order_name)])[0].id

                        if status != 'Delete':
                            new_ship_id = self.create_shipping_charge_line(shipping_charges_line_obj, order_id, tracking_number,
                                                                           charge_name_freight, list_freight_charges_total,
                                                                           applied_freight_charges_total, contract_freight_charges_total)
                            new_created_shipping.extend(new_ship_id)
                            new_ship_id = self.create_shipping_charge_line(shipping_charges_line_obj, order_id, tracking_number,
                                                                           charge_name_accessorial, list_charges_accessorial_total,
                                                                           applied_charges_accessorial_total, contract_charges_accessorial_total)
                            new_created_shipping.extend(new_ship_id)
                            new_ship_id = self.create_shipping_charge_line(shipping_charges_line_obj, order_id, tracking_number,
                                                                           charge_name_surcharges, list_charges_surcharges_total,
                                                                           applied_charges_surcharge_total, contract_charges_surcharges_total)
                            new_created_shipping.extend(new_ship_id)
                            new_ship_id = self.create_shipping_charge_line(shipping_charges_line_obj, order_id, tracking_number,
                                                                           charge_name_discounts, list_charges_discounts_total,
                                                                           applied_charges_discounts_total, contract_charges_discounts_total)
                            new_created_shipping.extend(new_ship_id)
                            new_ship_id = self.create_shipping_charge_line(shipping_charges_line_obj, order_id, tracking_number,
                                                                           charge_name_misc, list_charges_misc_total,
                                                                           applied_charges_handling_total, contract_charges_handling_total)
                            new_created_shipping.extend(new_ship_id)
                            new_ship_id = self.create_shipping_charge_line(shipping_charges_line_obj, order_id, tracking_number,
                                                                           charge_name_total, list_charges_total,
                                                                           applied_charges_total, contract_charges_total)
                            new_created_shipping.extend(new_ship_id)
                else:
                    attachment.unlink()
            if has_attachment:
                if status != 'Delete':
                    order_data = sale_order_obj.search([('name', '=', self.name)])

                    if order_data.ship_ids:
                            for ship_id in order_data.ship_ids:
                                ship_ids_old.extend(ship_id)

                    self.currency_id = order_data.currency_id.id

                    for old_ship in ship_ids_old:
                        all_ship_ids.append([4, old_ship.id, False])

                    slist = delivery_date.split("/")
                    if int(slist[2]) > 1900:
                        sdate = datetime.date(int(slist[2]), int(slist[0]), int(slist[1]))
                    else:
                        sdate = False

                    self.ship_ids = all_ship_ids
                    self.carrier = service
                    self.method = method
                    self.in_hand_date = sdate
                    self.shipping_tracking_numbers = ','.join(map(str, list(shipping_tracking_numbers)))
                    if self.picking_ids:
                        for picking in self.picking_ids:
                            picking.in_hand_date = sdate

                elif status == 'Delete':
                    if status == 'Delete':
                        self.ship_ids = False
                        self.carrier = False
                        self.method = False
                        self.in_hand_date = False
                        self.shipping_tracking_numbers = False
                        if self.picking_ids:
                            for picking in self.picking_ids:
                                picking.in_hand_date = False



    def create_shipping_charge_line(self, obj, ship_line, tracking_no,
                                    charge_name, list_charge, applied_charge, contract_charge):
        return obj.create({'ship_line': ship_line,
                    'tracking_no': tracking_no,
                    'charge_name': charge_name,
                    'list_charge': list_charge,
                    'applied_charge': applied_charge,
                    'contract_charge': contract_charge,
                    'charge_name': charge_name,
                    })

class StockInvoiceOnshipping(osv.osv):
    _inherit = "stock.invoice.onshipping"

    _columns = {
        'shipping_charges': fields.selection([('none', 'None'),
                                              ('l', 'List Charges'),
                                              ('a', 'Applied Charge'),
                                              ('c', 'Contract Charge')], 'Shipping Charge Type'),
        'include_shipping_charges': fields.boolean('Include shipping charges ?'),
        'stock_id': fields.many2one('stock.picking', 'Stock Id')
    }
    _defaults = {
        'shipping_charges':'none',
        'include_shipping_charges': True,
        'shipping_charges': 'l',
    }

    def create(self, cr, uid, vals, context=None):
        if context.get('active_model', '') == 'stock.picking':
            vals['stock_id'] = context['active_id']
        id = super(StockInvoiceOnshipping, self).create(cr, uid, vals, context=context)
        return id

    def open_invoice(self, cr, uid, ids, context=None):
        sio = super(StockInvoiceOnshipping, self).open_invoice(cr, uid, ids, context=context)
        selected_charge = 0
        stock_invoice_onshipping_data = self.browse(cr, uid, ids, context=context)
        account_invoice_obj = self.pool.get('account.invoice')
        sale_order_obj = self.pool.get('sale.order')
        account_invoice_line_obj = self.pool.get('account.invoice.line')
        product_product_obj = self.pool.get('product.product')
        stock_config_settings_obj = self.pool.get('stock.config.settings')
        values_product_id = stock_config_settings_obj.default_get(cr, uid, ['product_id'], context=context)
        # stock_config_settings_id = stock_config_settings_obj.search(cr, uid, [], limit=1, order='id desc')[0]
        # shippping_and_handling_product = stock_config_settings_obj.browse(cr, uid, [stock_config_settings_id], context=context)
        #shippping_and_handling_product = product_product_obj.search(cr, uid, [('name_template', '=', 'Shipping & Handling charges')])

        model_data_obj = self.pool.get('ir.model.data')
        service_product = model_data_obj.get_object_reference(cr, uid, 'ob_starship', 'service_product_starship')
        if values_product_id.get('product_id', False):
            model = context.get('active_model', '')
            id = context.get('active_id', '')
            obj = self.pool.get(model)
            stock_id = obj.browse(cr, uid, [id], context=context)
            if stock_id.sale_id.ship_ids:
                for ship in stock_id.sale_id.ship_ids:
                    if ship.charge_name == 'Grand Total':
                        selected_charge = selected_charge + ship.applied_charge

            obj.write(cr, uid, id, {'total_charge': selected_charge})
            sale_order_obj.write(cr, uid, stock_id.sale_id.id, {'shipping_done': True})
            invoice_id = account_invoice_obj.search(cr, uid, [('origin', '=', stock_id.name)])
            if invoice_id:
                invoice_datas = account_invoice_obj.browse(cr, uid, invoice_id)
            	for invoice_data in invoice_datas:
                    if invoice_data.type == 'out_invoice':
                    	line_id = account_invoice_line_obj.search(cr, uid,
                                                                  [('invoice_id', '=', invoice_data.id),
                                                                   ('product_id', '=',
                                                                    values_product_id.get('product_id', False))])
                    	if not stock_id.sale_id.x_3rd_party:
                            service_product_id = product_product_obj.browse(cr, uid, [service_product[1]], context)
                            account_invoice_line_obj.write(cr, uid, line_id[0],
                                                           {'product_id': service_product_id.id,
                                                            'name': service_product_id.product_tmpl_id.name,
                                                            'price_unit': selected_charge, 'quantity': 1})
                    	else:
                            account_invoice_line_obj.write(cr, uid, line_id[0],
                                                           {'price_unit': selected_charge, 'quantity': 1})

        return True


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    _columns = {
        'total_charge': fields.float('Total Charge'),
    }
