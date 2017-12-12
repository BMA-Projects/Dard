from openerp import models, fields, api, _
from datetime import datetime,date
from openerp.exceptions import Warning
from openerp.tools.translate import _
from lxml import etree
from openerp.osv.orm import setup_modifiers
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class sale_order_line_images(models.Model):
    _inherit = 'sale.order.line.images'

    type_ids = fields.Many2many('artwork.master.type',string='Type')
    shape_ids = fields.Many2many('artwork.master.shape',string='Shape')
    onloop_ids = fields.Many2many('artwork.master.onloop',string='On Loop')
    attachment_ids = fields.Many2many('artwork.master.attachment',string='Attachment')
    dim_ids = fields.Many2many('artwork.master.2d.3d',string='2D/3D')
    platting_ids = fields.Many2many('artwork.master.platting',string='Platting')
    decoration_ids = fields.Many2many('artwork.master.decoration',string='Decoration')
    location_ids = fields.Many2many('artwork.decoration.location','artwork_line_images_location_rel', string="Location")
    imprint_color_ids = fields.Many2many('artwork.decoration.imprint.color','artwork_line_images_imprint_color_rel', string="Imprinting Color")
    other_type_bool = fields.Boolean(string='Other')
    other_type_val = fields.Char('other')
    other_onloop_bool = fields.Boolean(string='Other')
    other_onloop_val = fields.Char('other')
    other_attachment_bool = fields.Boolean(string='Other')
    other_attachment_val = fields.Char('other')
    solid_attachment_bool = fields.Boolean(string='Solid Rib.(Colour)')
    solid_attachment_val = fields.Char('other')
    deluxe_attachment_bool = fields.Boolean(string='Deluxe')
    deluxe_attachment_val = fields.Selection([('a','A'),('b','B')],'Deluxe values')
    blade_attachment_bool = fields.Boolean(string='L/O Blade')
    blade_attachment_val = fields.Selection([('a','A'),('b','B'),('c','C')],'L/O Blade values')
    other_platting_bool = fields.Boolean(string='Other')
    other_platting_val = fields.Char('other')

class artwork_master_type(models.Model):
    _name = 'artwork.master.type'

    name = fields.Char(string='Name', required=True)

class artwork_master_shape(models.Model):
    _name = 'artwork.master.shape'

    name = fields.Char(string='Name', required=True)

class artwork_master_onloop(models.Model):
    _name = 'artwork.master.onloop'

    name = fields.Char(string='Name', required=True)

class artwork_master_attachment(models.Model):
    _name = 'artwork.master.attachment'

    name = fields.Char(string='Name', required=True)

class artwork_master_2d_3d(models.Model):
    _name = 'artwork.master.2d.3d'

    name = fields.Char(string='Name', required=True)

class artwork_master_platting(models.Model):
    _name = 'artwork.master.platting'

    name = fields.Char(string='Name', required=True)

class artwork_master_decoration(models.Model):
    _name = 'artwork.master.decoration'

    name = fields.Char(string='Name', required=True)


class artwork_decoration_location(models.Model):
    _name = 'artwork.decoration.location'

    name = fields.Char(string='Name', required=True)

class artwork_decoration_imprint_color(models.Model):
    _name = 'artwork.decoration.imprint.color'

    name = fields.Char(string='Name', required=True)



