# -*- coding: utf-8 -*-
from openerp import models, fields


class res_groups(models.Model):
    _inherit = 'res.groups'

    read_only_res_groups = fields.Many2many(
        'ir.model.fields', 'ir_model_fields_group_rel_read_only_group',
        'group_id', 'field_id', 'Read Only Groups')
    invisible_res_groups = fields.Many2many(
        'ir.model.fields', 'ir_model_fields_group_rel_invisible_group',
        'group_id', 'field_id', 'Invisible Groups')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
