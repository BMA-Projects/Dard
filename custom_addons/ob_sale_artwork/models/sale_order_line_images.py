# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api, _
import base64
from urlparse import urljoin
from urllib import urlencode
from datetime import datetime
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import os
import random
from openerp.exceptions import except_orm,Warning
import errno

class SaleOrderLineImages(models.Model):
    """
    This model used for Artwork and Virtual files.
    ==============================================
    ->    On creating or modifying record it will store artwork file and virtual file at the physical storage.
    ->    States will indicate the status of particular Artwork.
    ->    User can upload multiple Artwork and will get multiple virtual files.
    ->    At least one Artwork should be Confirmed.
    ->    It will keep track of changing the states.
    """
    _name = "sale.order.line.images"
    _description = "Sale Order Line Images"
    _rec_name = 'art_image_name'
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _order = 'create_date desc'
    
    _track = {
        'state': {
            'ob_sale.mt_sol_new': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'ob_sale.mt_sol_sent_for_approval': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'sent_for_approval',
            'ob_sale.mt_sol_confirmed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirmed',
            'ob_sale.mt_sol_semi_confirmed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'semi_confirmed',
            'ob_sale.mt_sol_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
            'ob_sale.mt_sol_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
            'ob_sale.mt_sol_stage': lambda self, cr, uid, obj, ctx=None: obj['state'] not in ['draft', 'sent_for_approval', 'confirmed','semi_confirmed', 'done', 'cancel']
        },
    }

    @api.one
    def get_approval_link(self):
        dbname = self.env.cr.dbname
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        query = {'db': dbname, 'res_id' : self.id, 'virtual_state':'confirmed','data_key': self.data_key}
        self.approval_link = urljoin(base_url, '/ArtworkVerification' + "?%s" % (urlencode(query)))
        query.update({'virtual_state':'semi_confirmed'})
        self.semi_approval_link = urljoin(base_url, '/ArtworkVerification' + "?%s" % (urlencode(query)))
        query.update({'virtual_state':'cancel'})
        self.send_another_link = urljoin(base_url, '/ArtworkVerification' + "?%s" % (urlencode(query)))
    
    @api.v7
    def onchange_virtual_file(self, cr, uid, ids, virtual_file,virtual_file_name, context=None):
        return {}
    
    @api.v7
    def onchange_is_url(self, cr, uid, ids, is_url, context=None):
        if is_url:
            return {'value':{'virtual_file':'undefined','virtual_file_name':False}}
        else:
            return {'value':{'external_link':False}}
            
    @api.one
    @api.depends('order_line_id.order_id.partner_id')
    def get_partner_id(self):
        self.partner_id = self.order_line_id.order_id.partner_id
        
    @api.one
    def get_sale_order_id(self):
        self.order_id = self.order_line_id.order_id.id
    
    @api.one
    def get_sol_seq(self):
        self.sol_id = self.order_line_id.sol_seq

    @api.one
    def _get_rush_order(self):
        if self.order_id:
            res = self.order_id.rush_order
            self.red_bool = res

    description = fields.Text("Description")
    red_bool = fields.Boolean(compute="_get_rush_order" ,string="Red")
    art_image = fields.Text("Image")
    art_image_name = fields.Char("Key Word",size=64,required=True)
    art_image_local_name = fields.Char("Image Local Name",size=256)
    virtual_file = fields.Binary("Virtual File")
    virtual_file_name = fields.Char("Virtual File Name")
    virtual_file_name_url = fields.Char("Virtual File Name URL")
    sent_for_verification = fields.Boolean("Is Verified")
    state = fields.Selection([
                ('draft', 'Virtual Pending'),
                ('sent_for_approval', 'Sent for Approval'),
                ('confirmed', 'Approved'),
                ('semi_confirmed', 'Approved with Changes'),
                ('cancel', 'Send Another Virtual')], 'Status', required=True,readonly=True,
            track_visibility='onchange', default='draft',
            help='* The \'Virtual Pending\' status is set when new sale order line will created. \
                \n* The \'Sent for Approval\' status is set when Virtual team send the mail to customer for approval. \
                \n* The \'Approved\' status is set when customer will approved the virtual. \
                \n* The \'Approved with changes\' status is set when customer will approved the virtual. \
                \n* The \'Send Another Virtual\' status is set when customer will reject the current virtual or disapproved the sent virtual.')
    order_line_id = fields.Many2one('sale.order.line', 'Sale Order Line')
    approval_link = fields.Char(string='Approval Link',compute="get_approval_link")
    semi_approval_link = fields.Char(string='Semi Approval Link',compute="get_approval_link")
    send_another_link = fields.Char(string='Send Another Link',compute="get_approval_link")
    data_key = fields.Char(string="Data Key",default=str(random.randrange(1000)).zfill(4) + '_' + str(datetime.now()).replace(' ','_').replace(':','_').replace('-','_').replace('.','_'))
    history_ids = fields.One2many("virtual.history","sol_image_id","Virtual File History")
    mrp_id = fields.Many2one("mrp.production","MRP ID")
    purchase_line_id = fields.Many2one("purchase.order.line","Purchase Line ID")
    
    #need to pass value in context or somethoding else
    # Related field is not supported by the v8 and below 3 fields are very important.
    # Need to init while creating a record or need to pass argument while creating it.
#     partner_id = fields.Related('order_id', 'partner_id', type='many2one', relation='res.partner', string='Customer', store=True)
#     order_id = fields.Related('order_line_id', 'order_id', type='many2one', relation='sale.order', string='Sale Order', store=True)
#     sol_id = fields.Related('order_line_id', 'sol_seq', type='char', string='Order Line #', store=True)
    
    partner_id = fields.Many2one('res.partner', 'Customer', store=True)
    order_id = fields.Many2one('sale.order', 'Sale Order',compute='get_sale_order_id', store=True)
    sol_id = fields.Char('Order Line #', size=16,compute='get_sol_seq', store=True)
    is_url = fields.Boolean("Is URL")
    external_link = fields.Char("External Link")
    company_id = fields.Many2one("res.company", "Company", default=lambda self: self.env.user.company_id)
    
    @api.model
    def copy(self):
        raise Warning(_('Artwork Duplication'), _('Artwork can not be duplicate. It has to be generated from the Sale Order.'))
        return super(SaleOrderLineImages, self).copy()

    @api.one
    def write(self, vals):
        """
        By overriding this method we will modify the value of 'vals' dictionary. like removing binary data and add url for perticular file.
        """
        if vals.get('virtual_file',False):
            vals = self.store_file_physically(vals)
        return super(SaleOrderLineImages, self).write(vals)
    
    @api.model
    def create(self, vals):
        """
        By overriding this method we will modify the value of 'vals' dictionary. like removing binary data and add url for perticular file.
        """
        if not vals.get('sol_id'):
            sale_order_line_seq = self.env['sale.order.line'].browse(vals.get('order_line_id'))
            vals.update({'sol_id': sale_order_line_seq.sol_seq, 'order_id': sale_order_line_seq.order_id.id})
        
        if vals.get('virtual_file',False):
            vals = self.store_file_physically(vals)
        return super(SaleOrderLineImages, self).create(vals)
    
    @api.v8
    def store_file_physically(self, vals, isArtImage=False):
        """
        It will stores Artwork file or Virtual file physically in the addons folder.
        Also update values like.. Empty the binary data and stores the path of file. 
        @param isArtImage: for checking the file is for Artwork or Virtual file.
        @return: It will returns values for creating or updating the record.
        """
        
        abs_path = self.env['ir.config_parameter'].get_param('global.path')
        web_path = self.env['ir.config_parameter'].get_param('global.web.path')
        if not abs_path:
            raise Warning(_("Physical Image Storage path not configured in the system parameter.\nPlease contact your Administrator."))
        if not web_path:
            raise Warning(_("Physical Image Storage web path not configured in the system parameter.\nPlease contact your Administrator."))
        
        if isArtImage:
            data = vals.get('art_image',False)
            user_upl_path = abs_path + "/openerp/user_uploads/artworks"
            lnkPath = web_path + "/web/static/src/img/web_image"
            if not vals.get("art_image_name"):
                vals.update({'art_image': False})
                return vals
            data_fname = str(random.randrange(1000)).zfill(4) + '_' + str(datetime.now()).replace(' ','_') + '.' + vals.get("art_image_name").split(".")[-1]
            final_path = '/web/static/src/img/web_image/' + self.env.cr.dbname + "/" + data_fname
        else:
            if not vals.get("virtual_file_name"):
                vals.update({'virtual_file':False})
                return vals
            data = vals.get('virtual_file',False)
            user_upl_path = abs_path + "/openerp/user_uploads/virtuals"
            lnkPath = web_path + "/web/static/src/img/web_virtuals"
            data_fname = str(random.randrange(1000)).zfill(4) + '_' + str(datetime.now()).replace(' ','_') + '.' + vals.get("virtual_file_name").split(".")[-1]
            final_path = '/web/static/src/img/web_virtuals/' + self.env.cr.dbname + "/" + data_fname
            vals.update({'virtual_file': False, 'virtual_file_name_url': final_path})
        self.create_link(isArtImage, user_upl_path, lnkPath)
        phy_loc = user_upl_path + "/" + self.env.cr.dbname
        image_path =  phy_loc + "/" + data_fname
        if not os.path.exists(phy_loc):
            os.mkdir(phy_loc,0777)
        imgdata = base64.b64decode(data)
        with open(image_path, 'wb') as f:
            f.write(imgdata)
        return vals
    
    @api.v8
    def create_link(self, isArtImage, srcPath, lnkPath):
        """
        Create the link according to given source and link path.
        @param isArtImage: for checking the link is for Artwork or Virtual file.
        @param srcPath: It is source path for which the link will be created.
        @param lnkPath: It is path for where link should be created.
        @return: True
        """
        if not os.path.islink(lnkPath):
            try:
                os.symlink(srcPath, lnkPath)
            except:
                raise Warning(("Can't create destination directory"))
        return True
    
    @api.v8
    def get_base_url(self):
        return self.env['ir.config_parameter'].get_param('web.base.url')
    
    @api.multi
    def sent_for_approval(self):
        """
        This method will call _send_mail if virtual file will be upload by Artwork Team.
        Also change the state to "send_for_approval" and make "sent_for_verification" field True.
        """
        virtual_history_obj = self.env["virtual.history"]
        ir_model_data = self.env['ir.model.data']
        if self.is_url and not self.external_link:
            raise Warning(_("There is no External Link entered"))
        if not self.is_url and not self.virtual_file_name:
            raise Warning(_("There is no virtual file found.\nSelect Virtual file in the form first."))
        if not self.order_line_id.order_id.partner_id.email:
            raise Warning(_("Email address of customer not found."))
        template_id = self.env['ir.model.data'].get_object_reference('ob_sale_artwork', 'email_template_edi_virtual_process')[1]
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        cur_time = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        ctx.update({
            'default_model': 'sale.order.line.images',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'sent_date' : cur_time,
            'sol_image_id' : self.id,
            'name' : self.virtual_file_name,
            'name_url' : self.virtual_file_name_url,
            'is_url' : self.is_url,
            'external_link' : self.external_link,
            'sendmail_temp':True,
            'send_by_email_wizard': True,
        })
        if self.order_id:
            ctx.update({
                'parent_model_name': 'sale.order.line.images',
                'show_email':True,
                'artwork_image_contact_id': self.order_id and self.order_id.partner_id.id or False,
                'artwork_partner_id': self.order_id.partner_id and self.order_id.partner_id.id or False,  
                })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.v8
    def _send_email(self):
        """
        Send mail for verify the virtual artwork uploaded by Artwork Team.
        @return: True
        """
        email_temp_obj = self.env['email.template']
        mail_mail_obj = self.env['mail.mail']
        order_proof_email = self.partner_id.order_proof_email or self.partner_id.email
        template_id = self.env['ir.model.data'].get_object_reference('ob_sale_artwork', 'email_template_edi_virtual_process')[1]
        msg_id = email_temp_obj.search([['id','=',template_id]]).send_mail(self.id)[0]
        msg_rec = mail_mail_obj.search([['id','=',msg_id]])
        msg_rec.write({'email_to': order_proof_email,'auto_delete': True})
        msg_rec.send()
        msg_rec1 = mail_mail_obj.search([['id','=',msg_id]])
        if msg_rec1.id:
            return False
        else:
            return True
    
    @api.multi
    def download_img(self):
        """
        It will return act_url for downloading the Artwork image by the virtual team. 
        """
        if not self.art_image_name:
            raise Warning(_('Error!'), _('There is no image file found to download.'))
        return {
            'type': 'ir_actions_download_file', 
            'file_url': self.art_image_local_name, 
            'file_name' : self.art_image_name
        }
    
    @api.multi
    def download_virtual(self):
        """
        It will return act_url for downloading the Virtual file by the virtual team. 
        """
        if self.is_url:
            raise Warning(_('External Link cannot be download from here. You can download it manually.'))
        if not self.virtual_file_name:
            raise Warning(_('There is no virtual file found to download.'))
        return {
            'type': 'ir_actions_download_file', 
            'file_url': self.virtual_file_name_url, 
            'file_name' : self.virtual_file_name,
        }
        
    @api.v7
    def approve_art(self,cr, uid, id, context=None):
        self.write(cr, uid, id, {'state' : 'confirmed'})
        self.message_post(cr, uid, id, type="email", subtype='mail.mt_comment', body=_('Artwork Approved.'))
        return True
    
    @api.v7
    def semi_confirm_art(self,cr, uid, id, context=None):
        self.write(cr, uid, id, {'state' : 'semi_confirmed'})
        self.message_post(cr, uid, id, type="email", subtype='mail.mt_comment', body=_('Artwork Approved with changes.'))
        return True
    
    @api.v7
    def cancel_confirm_art(self,cr, uid, id, context=None):
        self.write(cr, uid, id, {'state' : 'cancel'})
        self.message_post(cr, uid, id, type="email", subtype='mail.mt_comment', body=_('Send Another Artwork.'))
        return True
    
    @api.multi    
    def do_semi_confirm(self):
#         self.write({'state' : 'semi_confirmed'})
#         self.message_post(type="email", subtype='mail.mt_comment', body=_('Artwork Approved with changes.'))
        return True

    @api.multi
    def do_confirm(self):
#         self.write({'state' : 'confirmed'})
#         self.message_post(type="email", subtype='mail.mt_comment', body=_('Artwork Approved.'))
        return True

    @api.multi    
    def do_semi_confirm(self):
#         self.write({'state' : 'semi_confirmed'})
#         self.message_post(type="email", subtype='mail.mt_comment', body=_('Artwork Approved with changes.'))
        return True
     
    @api.multi
    def do_cancel(self):
#         self.write({'state' : 'cancel'})
#         self.message_post(type="email", subtype='mail.mt_comment', body=_('Send Another Artwork.'))
        return True
