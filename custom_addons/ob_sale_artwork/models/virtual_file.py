# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import except_orm,Warning
import random
from datetime import datetime
import os
import base64

class VirtualFiles(models.Model):
    
    """
    This model used for Virtual files.
    ==============================================
    ->    It will store the information about virtual file.
    """
    
    _name = "virtual.file"
    _description = "Virtual File"

    name = fields.Char("File Name", size=128)
    file = fields.Binary('File')
    file_url = fields.Char("File URL", size=512)
    description = fields.Char('Description', size=128)
    line_id = fields.Many2one("sale.order.line","Line ID")
    mrp_id = fields.Many2one("mrp.production","MRP ID")
    purchase_line_id = fields.Many2one("purchase.order.line","Purchase Line ID")

    @api.v8
    def create_link(self, srcPath, lnkPath):
        """
        Create the link according to given source and link path.
        @param isArtImage: for checking the link is for Artwork or Virtual file.
        @param srcPath: It is source path for which the link will be created.
        @param lnkPath: It is path for where link should be created.
        @return: True
        """
        if not os.path.islink(lnkPath):
            os.symlink(srcPath, lnkPath)
        return True

    @api.v8
    def store_file(self, data_fname, data):
        abs_path = self.env['ir.config_parameter'].get_param('global.path')
        web_path = self.env['ir.config_parameter'].get_param('global.web.path')
        if not abs_path:
            raise Warning(_('Physical Image Storage path not configured in the system parameter.\nPlease contact your Administrator.'))
        if not web_path:
            raise Warning(_('Physical Image Web Storage path not configured in the system parameter.\nPlease contact your Administrator.'))
        user_upl_path = abs_path + "/openerp/user_uploads/virtuals"
        lnkPath = web_path + "/web/static/src/img/web_virtuals"
        self.create_link(user_upl_path, lnkPath)
        phy_loc = user_upl_path + "/" + self._cr.dbname
        image_path =  phy_loc + "/" + data_fname
        if not os.path.exists(phy_loc):
            os.mkdir(phy_loc,0777)
        imgdata = base64.b64decode(data)
        with open(image_path, 'wb') as f:
            f.write(imgdata)
        return True

    @api.multi
    def write(self,vals):
        """
        By overriding this method we will modify the value of 'vals' dictionary. like removing binary data and add url for perticular file.
        """
        if vals.get('file',False):
            # data_fname = str(random.randrange(1000)).zfill(4) + '_' + str(datetime.now()).replace(' ','_') + '.' [-1]
            data_fname = str(random.randrange(1000)).zfill(4) + '_' + str(datetime.now()).replace(' ','_') + '.' + vals.get("file_url").split(".")[-1]
            data = vals.get('file',False)
            if self.store_file(data_fname, data):
                vals.update({'file_url': 'web/static/src/img/web_virtuals/' + self._cr.dbname + "/" + data_fname, 'file': False})
        return super(VirtualFiles, self).write(vals)
    
    @api.model
    def create(self, vals):
        """
        By overriding this method we will modify the value of 'vals' dictionary. like removing binary data and add url for perticular file.
        """
        if vals.get('file',False):
            # data_fname = str(random.randrange(1000)).zfill(4) + '_' + str(datetime.now()).replace(' ','_') + '.' [-1]
            data_fname = str(random.randrange(1000)).zfill(4) + '_' + str(datetime.now()).replace(' ','_') + '.' + vals.get("file_url").split(".")[-1]
            data = vals.get('file',False)
            if self.store_file(data_fname, data):
                vals.update({'file_url': 'web/static/src/img/web_virtuals/' + self._cr.dbname + "/" + data_fname, 'file': False})
        return super(VirtualFiles, self).create(vals)
    
    @api.multi
    def download_virtual_file(self):
        """
        It will return act_url for downloading the Virtual file by the virtual team. 
        """
        if not self.file_url:
            raise Warning(_('There is no virtual file found to download.'))
        return {
            'type': 'ir_actions_download_file', 
            'file_url': self.file_url, 
            'file_name' : self.name,
        }

class VirtualHistory(models.Model):
    """
    This model used for maintain the history of the virtual file send by the virtual team to the end user.
    """
    _name = "virtual.history"
    _description = "Virtual File History"
    
    name = fields.Char("Virtual File Name",size=132)
    sent_date = fields.Datetime("Sent Date")
    sol_image_id = fields.Many2one('sale.order.line.images',"SOL Image")
    name_url = fields.Char("Virtual File Name URL",size=256)
    is_url = fields.Boolean("Is URL")
    external_link = fields.Char("External Link",size=512)
    
    @api.multi
    def download_virtual(self):
        """
        It will return act_url for downloading the Virtual file by the virtual team. 
        """
        if not self:
            raise Warning(_('History not found.'))
        if self.is_url:
            raise Warning(_('External Link cannot be download from here. You can download it manually.'))
        else:
            if self.name:
                return {
                    'type': 'ir_actions_download_file',
                    'file_url' : self.name_url, 
                    'file_name': self.name,
                }
            else:
                raise Warning(_('No virtual file name found.'))
