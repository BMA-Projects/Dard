# -*- coding: utf-8 -*-
from openerp import models, fields


class ir_model_fields(models.Model):
    _inherit = 'ir.model.fields'

    read_only_groups = fields.Many2many(
        'res.groups', 'ir_model_fields_group_rel_read_only_group',
        'field_id', 'group_id', 'Read Only Groups')
    invisible_groups = fields.Many2many(
        'res.groups', 'ir_model_fields_group_rel_invisible_group',
        'field_id', 'group_id', 'Invisible Groups')

ir_model_fields()
