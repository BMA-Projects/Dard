# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from urlparse import urljoin
from urllib import urlencode
from openerp import models, fields, api, _
from openerp.exceptions import except_orm,Warning
import random
from openerp import tools
from datetime import datetime
from openerp import SUPERUSER_ID, workflow
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time
import os
import base64
import re
import json

class SaleOrderLineImages(models.Model):
    _inherit = "sale.order.line.images"
    
    def unlink(self, cr, uid, ids, context=None):
        if len(ids):
            sale_order_id = self.browse(cr, uid, ids, context=context)[0].order_line_id.order_id.id
            res = super(SaleOrderLineImages, self).unlink(cr, uid, ids, context=context)
             
            sale_obj = self.pool.get('sale.order')
            virtual_list_data = []
            virtual_ids = []
             
            for order_line in sale_obj.browse(cr, uid, sale_order_id, context=context).order_line:
                virtual_ids = self.search(cr, uid, [('order_line_id','=', order_line.id)])
                datas = self.read(cr, uid, virtual_ids,['virtual_file_name_url','virtual_file_name','state'])
                for data in datas:
                    if data:
                        result = {}
                        result['image'] = str(data['virtual_file_name_url'])
                        result['name'] = str(data['virtual_file_name'])
                        result['state'] = ''
                        if str(data['state']) == 'draft':
                            result['state'] = 'Virtual Pending'
                        elif str(data['state']) == 'confirmed':
                            result['state'] = 'Approved'
                        elif str(data['state']) == 'semi_confirmed':
                            result['state'] = 'Approved With Change'
                        elif str(data['state']) == 'cancel':
                            result['state'] = 'Send Another Virtual'
                        virtual_list_data.append(result)
            sale_obj.write(cr, uid, [sale_order_id], {'art_multi_images': str(virtual_list_data)})
         
        return res
#     
    def write(self, cr, uid, ids, vals, context=None):
        sale_obj = self.pool.get('sale.order')
        virtual_ids = []
        res = super(SaleOrderLineImages,self).write(cr, uid, ids, vals, context=context)
        
        if ids or len(ids) :
            sale_order_id = self.browse(cr, uid, ids, context=context)[0].order_id.id
            virtual_list_data = []
             
            if 'state' in vals:
                for order_line in sale_obj.browse(cr, uid, sale_order_id, context=context).order_line:
                    virtual_ids = self.search(cr, uid, [('order_line_id','=', order_line.id)])
                    datas = self.read(cr, uid, virtual_ids,['virtual_file_name_url','virtual_file_name','state'])
                    for data in datas:
                        if data:
                            result = {}
                            result['image'] = str(data['virtual_file_name_url'])
                            result['name'] = str(data['virtual_file_name'])
                            result['state'] = ''
                            if str(data['state']) == 'draft':
                                result['state'] = 'Virtual Pending'
                            elif str(data['state']) == 'confirmed':
                                result['state'] = 'Approved'
                            elif str(data['state']) == 'semi_confirmed':
                                result['state'] = 'Approved With Change'
                            elif str(data['state']) == 'cancel':
                                result['state'] = 'Send Another Virtual'
                            virtual_list_data.append(result)
                sale_obj.write(cr, uid, [sale_order_id], {'art_multi_images': str(virtual_list_data)})
        return res
    
    def create(self, cr, uid, vals, context=None):
        sale_obj = self.pool.get('sale.order')
        virtual_ids = []
        
        res = super(SaleOrderLineImages,self).create(cr, uid, vals, context=context)
        
        sale_order_id = self.browse(cr, uid, res, context=context)[0].order_id.id
        virtual_list_data = []
        
        if 'art_image' in vals:
            for order_line in sale_obj.browse(cr, uid, sale_order_id, context=context).order_line:
                virtual_ids = self.search(cr, uid, [('order_line_id','=', order_line.id)])
                datas = self.read(cr, uid, virtual_ids,['virtual_file_name_url','virtual_file_name','state'])
                for data in datas:
                    if data:
                        result = {}
                        result['image'] = str(data['virtual_file_name_url'])
                        result['name'] = str(data['virtual_file_name'])
                        result['state'] = ''
                        if str(data['state']) == 'draft':
                            result['state'] = 'Virtual Pending'
                        elif str(data['state']) == 'confirmed':
                            result['state'] = 'Approved'
                        elif str(data['state']) == 'semi_confirmed':
                            result['state'] = 'Approved With Change'
                        elif str(data['state']) == 'cancel':
                            result['state'] = 'Send Another Virtual'
                        virtual_list_data.append(result)
            sale_obj.write(cr, uid, [sale_order_id], {'art_multi_images': str(virtual_list_data)})
        return res 

class sale_order(models.Model):
    _inherit = 'sale.order'
    art_multi_images = fields.Text('ArtWork Images')
