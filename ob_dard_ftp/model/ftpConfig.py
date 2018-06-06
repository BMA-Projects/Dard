# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from datetime import date, timedelta
from ftplib import FTP
import base64
import os

from openerp import fields, models, api, _
from openerp.exceptions import except_orm,Warning
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

import logging
_logger = logging.getLogger(__name__)
osSep = os.sep

class ftp_config(models.Model):
    _name = 'ftp.config'
    _rec_name = 'ftp_host'

    ftp_host = fields.Char(size=64, string='FTP Address(Host):') 
    host_user = fields.Char(size=64, string='User')
    host_pass = fields.Char(size=64, string='Password')
    upload_path = fields.Char(size=256, string='Upload Path' ,help='Path where file is going to upload.\nMake sure path ends with path separator', default = "/")
    partner_id = fields.Many2one(comodel_name='res.partner', required=True, domain="[('customer','=',True),('is_company','=',True)]", string='Customer',\
                 help="CSV file will be generated for the selected customer.\n please select customer with customer number ")
    active = fields.Boolean('Active', help="If unchecked, it will allow you to hide the configuration without removing it.", default=True)
    
    partner_ids = fields.Many2many('res.partner', 'ftp_id', 'part_id', 'ftp_part_rel', 'Select Customers')
    
    
    
    @api.multi
    def test_ftp_connection(self):
        try:
            ftp = FTP(self.ftp_host)
            ftp.login(user=self.host_user,passwd=self.host_pass)
            ftp.cwd(self.upload_path)
        except Exception as exc:
            if exc.message == '550 Failed to change directory.':
                exc.args=('550 Invalid upload path.',)
            raise except_orm('Error',exc)
        raise Warning(_('Done!'), _('Connected Successfully!'))


class partner_statistics(models.Model):
    _name = 'partner.statistics'

    @api.model
    def gen_csv(self, days=1, fNamePrefix='000005'):
        days = days if isinstance(days,int) else 1
        config_rec = self.env['ftp.config'].search([('active','=',True)], limit=1)
        cron_rec = self.env.ref('ob_dard_ftp.ir_cron_ftp_upload')
        global_path = self.env['ir.config_parameter'].get_param('global.path')
        global_path = global_path + osSep if global_path[-1] != osSep else global_path

        data_dir = 'csv_data_'+str(config_rec.partner_id.name).replace(' ','_')
        csv_header = "PO #,Invoice #,Invoice Date,Total Amount\n"
        csv_data = ''
        filename = fNamePrefix +'_'+ date.strftime(date.today(),'%m%d%Y')+'.csv'
        curr_symbol = config_rec.partner_id.company_id.currency_id.symbol or ''
        if config_rec and global_path:
            so_obj = self.env['sale.order']
            invoice_obj = self.env['account.invoice']
            stock_picking_obj = self.env['stock.picking']
            attachment_obj = self.env['ir.attachment']

            dt = date.today() - timedelta(days)
            date_str = date.strftime(dt, DEFAULT_SERVER_DATE_FORMAT)
            date_csv = date.strftime(dt,'%m/%d/%Y')
            invoice_recs = invoice_obj.search([('validated_date','=',date_str),('partner_id','=', config_rec.partner_id.id),('type','=','out_invoice'),('state','=', 'open')])
            for invoice in invoice_recs:
                po_ref = ''
                if invoice.origin:
                    picking_rec = stock_picking_obj.search([('name','=',invoice.origin)], limit=1)
                    # SO name can be found in origin of picking or on invoice itself
                    so_name = picking_rec.origin if picking_rec and picking_rec.origin else invoice.origin
                    po_ref = so_obj.search([('name','=', so_name)], limit=1).client_po_ref or ''
                else:
                    if 'client_po_ref' in invoice._fields.keys(): #if field exist on invoice use this field
                        po_ref = invoice.client_po_ref or ''

                csv_data += ','.join([po_ref, (invoice.number), date_csv, curr_symbol + ('%0.2f'%invoice.amount_total),'\n'])
            if csv_data:
                csv_data = csv_header + csv_data
                try:
                    # TO create attachmnet placed code here cause
                    parent_dict_id = self.env.ref('ob_dard_ftp.ftp_dict')
                    attach_rec = attachment_obj.search([('name','=', filename),('parent_id','=', parent_dict_id.id)])
                    if attach_rec:
                        return True #do not generate for second time
                    attachment_obj.create({'name': filename, 'datas_fname': filename,'res_model': 'partner.statistics','parent_id':parent_dict_id.id,'partner_id':config_rec.partner_id.id,'datas': base64.b64encode(csv_data),})

                    if data_dir not in os.listdir(global_path):
                        os.mkdir(global_path+data_dir)
                    with open((global_path+data_dir +osSep+ filename), 'w') as f:
                        f.write(csv_data)
                except Exception as e:
                    msg = 'On local:Unable to create CSV file: %s'%(filename)
                    _logger.error(msg)

                #for FTP transfer
                try:
                    config_recs = self.env['ftp.config'].search([('active','=',True),('partner_id','=',config_rec.partner_id.id)]) #searching all cause if we require to send file over multiple ftp location
                    for config_rec in config_recs:
                        ftp = FTP(config_rec.ftp_host)
                        ftp.login(user=config_rec.host_user,passwd=config_rec.host_pass)
                        ftp.storbinary('STOR %s/%s/%s' % (config_rec.upload_path, 'Invoices', filename), open((global_path+data_dir +osSep+ filename), 'rb'))
                        # ftp.storbinary('STOR '+config_rec.upload_path+filename, open((global_path+data_dir +osSep+ filename), 'rb'))
                        ftp.quit()
                        _logger.info('FILE: "%s" transfered successfully over FTP:%s'%(filename,config_rec.ftp_host))
                except Exception as e:
                    _logger.error('>>%s<<'%e)
        return True
