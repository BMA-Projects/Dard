# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import fields, models, api, _
from openerp.exceptions import except_orm,Warning
import os
import base64
import os.path
import StringIO
import csv
from ftplib import FTP
import logging
import datetime
_logger = logging.getLogger(__name__)
osSep = os.sep

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    validated_date = fields.Date('validated date')

    @api.multi
    def write(self, vals):
        if vals.get('state') == 'open':
            vals.update({'validated_date': fields.date.today()})
        return super(account_invoice, self).write(vals)



    @api.model
    def generate_asi_file(self):
        file_store_path = self.env["ir.config_parameter"].get_param("ftp.csv.path")
        
        file_store_path = file_store_path + osSep if file_store_path[-1] != osSep else file_store_path        
         
        if not file_store_path:
            raise Warning(_("No Path Defined To store CSV file"))
        final_list = []
        csv_data = ''
        # header = ['Distributor ASI Number',  'Supplier ASI Number', 'Freight', 
        #           'Invoice No', 'Invoice Date', 'Supplier Sales Order No',
        #           'Final Bill Code', 'Distributor Purchase Order Number', 'Distributor Name', 
        #           'Distributor Address', 'Distributor City', 'Distributor State', 'Distributor Zip', 
        #           'Supplier Name', 'Supplier Address', 'Supplier City', 'Supplier State', 'Supplier Zip',
        #           'Ship To Name', 'Ship To City', 'Ship To State', 'Ship to Zip', 'Product (item) Number',
        #           'Product Description', 'Quantity Shipped', 'Unit Price', 'Unit of Measure', 
        #           'Item Extended Price', 'Invoice Note', 'Terms', 'Ship Via', 'Actual Ship Date',
        #           'Total Invoice Tax Amount', 'Total Invoice Amount', '\n']
        # csv_data += ','.join(header)
        
        
        config_recs = self.env['ftp.config'].search([('active','=',True)])
        
        all_customer_invoice = []
        if config_recs and config_recs.partner_ids:
            all_customer_invoice = self.search([('type','=','out_invoice'),
                                                ('state','in',['open']),
                                                ('partner_id', 'in', [partner.id for partner in config_recs.partner_ids])
                                                ])
        else:
            all_customer_invoice = self.search([('type','=','out_invoice'),
                                                ('state','in',['open']),
                                                ])
        if all_customer_invoice:
            for customer_invoice in all_customer_invoice:
                freight = 0.00
                distributor_asi_number = customer_invoice.partner_id.asi_number or ' '
                supplier_asi_number = '48500'
                invoice_no = customer_invoice.number and customer_invoice.number.split('/')[-1] or ' '
                invoice_date = customer_invoice.date_invoice or ' '
                supplier_sales_order_no = ' '  #blank
                if customer_invoice.residual != customer_invoice.amount_total:
                    # final_bill_code = 'PB '+ customer_invoice.number or ' '
                    final_bill_code = 'PB'
                else:
                    # final_bill_code = 'FB '+ customer_invoice.number or ' '
                    final_bill_code = 'FB'
                distributor_name = customer_invoice.partner_id.name or ' '
                distributor_address = str(customer_invoice.partner_id.street) + ' ' +  str(customer_invoice.partner_id.street2) or ' '
                distributor_city = customer_invoice.partner_id.city or ' '
                distributor_state = customer_invoice.partner_id.state_id.code or ' '
                distributor_zip = customer_invoice.partner_id.zip or ' '
                invoice_note = str(customer_invoice.comment).replace('\n',' ') if str(customer_invoice.comment).replace('\n',' ') != 'False' else  ' '
                terms = customer_invoice.payment_term.name or ' '
                total_invoice_tax_amount = customer_invoice.amount_tax or ' '
                total_invoice_amount = customer_invoice.amount_total or ' '
                #get Freight for Invoice:
                for inv_freight_line in customer_invoice.invoice_line:
                    if inv_freight_line.product_id.type == 'service':
                        freight += inv_freight_line.price_subtotal
                
                
                if customer_invoice.origin and customer_invoice.origin.startswith('WH\OUT'):
                    picking_search = self.env['stock.picking'].search([('name','=',customer_invoice.origin),('picking_type_id.code','=','outgoing')])
                    sale_search = self.env['sale.order'].search([('name','=',picking_search.origin)])
                    for inv_line in customer_invoice.invoice_line:
                        if inv_line.product_id.type != 'service':
                            product_number = inv_line.product_id.default_code or ' '
                            product_description = inv_line.product_id.name or ' '
                            unit_price = inv_line.price_unit or ' '
                            item_extended_price = inv_line.quantity*inv_line.price_unit or 0.00
                            # unit_of_measure = inv_line.uos_id.name or ' '
                            unit_of_measure = 'EA'
                            quantity_shipped = inv_line.quantity or ' '
                            
                            if sale_search:
                                for sale in sale_search:
                                    supplier_name = ' '
                                    supplier_address = ' '
                                    supplier_city = ' '
                                    supplier_state = ' '
                                    supplier_zip = ' '
                                    #for so_line in sale.order_line:
                                        #purchase_search = self.env['purchase.order'].search([('name','=',so_line.po_ref)])
                                        #if purchase_search:
                                        #    supplier_name = purchase_search.partner_id.name or ' '
                                        #    supplier_address = str(purchase_search.partner_id.street) + ' ' +  str(purchase_search.partner_id.street2) or ' '
                                        #    supplier_city = purchase_search.partner_id.city or ' '
                                        #    supplier_state = purchase_search.partner_id.state_id.name or ' '
                                        #    supplier_zip = purchase_search.partner_id.zip or ' '
                                    
                                    distributor_purchase_order_number = sale.client_po_ref or ' '
                                    ship_to_name = sale.partner_shipping_id.name or ' ' 
                                    ship_to_city = sale.partner_shipping_id.city or ' '
                                    ship_to_state = sale.partner_shipping_id.state_id.code or ' '
                                    ship_to_zip = sale.partner_shipping_id.zip or ' '
                                    ship_via = sale.x_delivery_id.name or ' '
                                    actual_ship_date = sale.ship_dt or ' '
                        
                                    
                                    data_list = [ str(distributor_asi_number), str(supplier_asi_number), str(("%.2f" % freight)), str(invoice_no), str(invoice_date),
                                         str(supplier_sales_order_no), str(final_bill_code), str(distributor_purchase_order_number), 
                                         str(distributor_name), str(distributor_address), str(distributor_city), str(distributor_state), str(distributor_zip), 
                                         str(supplier_name), str(supplier_address), str(supplier_city), str(supplier_state), str(supplier_zip),
                                         str(ship_to_name), str(ship_to_city), str(ship_to_state), str(ship_to_zip), str(product_number), 
                                         str(product_description), str(quantity_shipped), str(unit_price), str(unit_of_measure), str(item_extended_price), 
                                         str(invoice_note), str(terms), str(ship_via), str(actual_ship_date), str(total_invoice_tax_amount), 
                                         str(total_invoice_amount)]
                                    final_list.append(data_list)        
                
                if customer_invoice.origin and customer_invoice.origin.startswith('SO'):
                    if customer_invoice.invoice_line:
                        for inv_line in customer_invoice.invoice_line:
                            quantity_shipped = 0.00
                            stock_move = self.env['stock.move'].search([('origin','=',inv_line.invoice_id.origin),
                                                            ('product_id','=',inv_line.product_id.id),
                                                            ('state','=','done')
                                                            ])
                            if stock_move:
                                for move in stock_move:
                                    quantity_shipped += move.product_uom_qty
                            
                            if inv_line.product_id.type != 'service':
                                product_number = inv_line.product_id.default_code or ' '
                                product_description = inv_line.product_id.name or ' '
                                unit_price = inv_line.price_unit or ' '
                                item_extended_price = quantity_shipped*inv_line.price_unit or 0.00
                                # unit_of_measure = inv_line.uos_id.name or ' '
                                unit_of_measure = 'EA'
                                
                                sale_search = self.env['sale.order'].search([('name','=',customer_invoice.origin)])
                                
                                if sale_search:
                                    
                                    for sale in sale_search:
                                        supplier_name = ' '
                                        supplier_address = ' '
                                        supplier_city = ' '
                                        supplier_state = ' '
                                        supplier_zip = ' '
                                        if sale.order_line:
                                            for sale_line in sale.order_line:
                                                #purchase_search = self.env['purchase.order'].search([('name','=',sale_line.po_ref)])
                                                #if purchase_search:
                                                #    supplier_name = purchase_search.partner_id.name or ' '
                                                #    supplier_address = str(purchase_search.partner_id.street) + ' ' +  str(purchase_search.partner_id.street2) or ' '
                                                #    supplier_city = purchase_search.partner_id.city or ' '
                                                #    supplier_state = purchase_search.partner_id.state_id.name or ' '
                                                #    supplier_zip = purchase_search.partner_id.zip or ' '
                                                
                                                distributor_purchase_order_number = sale_line.order_id.client_po_ref or ' '
                                                
                                        ship_to_name = sale.partner_shipping_id.name or ' ' 
                                        ship_to_city = sale.partner_shipping_id.city or ' '
                                        ship_to_state = sale.partner_shipping_id.state_id.code or ' '
                                        ship_to_zip = sale.partner_shipping_id.zip or ' '
                                        ship_via = sale.x_delivery_id.name or ' '
                                        actual_ship_date = sale.ship_dt or ' '
                                                
                                        data_list = [ str(distributor_asi_number), str(supplier_asi_number), str(("%.2f" % freight)), str(invoice_no), str(invoice_date),
                                                     str(supplier_sales_order_no), str(final_bill_code), str(distributor_purchase_order_number), 
                                                     str(distributor_name), str(distributor_address), str(distributor_city), str(distributor_state), str(distributor_zip), 
                                                     str(supplier_name), str(supplier_address), str(supplier_city), str(supplier_state), str(supplier_zip),
                                                     str(ship_to_name), str(ship_to_city), str(ship_to_state), str(ship_to_zip), str(product_number), 
                                                     str(product_description), str(quantity_shipped), str(unit_price), str(unit_of_measure), str(item_extended_price), 
                                                     str(invoice_note), str(terms), str(ship_via), str(actual_ship_date), str(total_invoice_tax_amount), 
                                                     str(total_invoice_amount)]
                                        final_list.append(data_list)  
        for lst in final_list:
            lst = [str(updated_value).replace(',',' ') for updated_value in lst]
            lst.append('\n')
            csv_data += ','.join(lst)
        now = datetime.datetime.now()
        file_name = 'easybill'+now.strftime("%Y%m%d")+'.csv'
        if csv_data:
            attachment_obj = self.env['ir.attachment']
            attachment_id = attachment_obj.create({'name': 'Easybill', 'datas_fname': file_name,
                               'datas': base64.b64encode(csv_data),})
        
        
        data_dir = 'Easibill'
        #Create file on given parameter path
        try:
            if data_dir not in os.listdir(file_store_path):
                os.mkdir(file_store_path+data_dir)
            with open((file_store_path+data_dir + '/' + file_name), 'w') as f:
                f.write(csv_data)
        except Exception as e:
            msg = 'On local:Unable to create CSV file'
            _logger.error(msg)
        
        
        #for FTP transfer
        try:
            #config_recs = self.env['ftp.config'].search([('active','=',True)]) #searching all cause if we require to send file over multiple ftp location
            for config_rec in config_recs:
                ftp = FTP(config_rec.ftp_host)
                ftp.login(user=config_rec.host_user,passwd=config_rec.host_pass)
                file_to_transfer = open((file_store_path+data_dir + '/' + file_name), 'rb')
                ftp.storbinary('STOR '+config_rec.upload_path, file_to_transfer)
                ftp.quit()
                _logger.info('FILE: "%s" transfered successfully over FTP:%s' % (file_name,config_rec.ftp_host))
        except Exception as e:
            _logger.error('%s'%e)
        
        
        return True
    
    
    