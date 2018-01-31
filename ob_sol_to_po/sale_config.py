from openerp import models, fields, api


# class sale_configuration(models.TransientModel):
#     _inherit = 'sale.config.settings'

#     create_po_or_poline = fields.Selection([
#         ('normal', 'Normal'),
#         ('create_new_line', 'Create New PO Line'),
#         ('create_new_po', 'Create New PO'),
#         ('new_po_with_new_line', 'Create New PO With New Line'),
#         ],
#         string='SO to Create PO/POL',
#         default='normal',
#         help= "Normal            : Create New Po As Per Base Flow\n"
#               "Create New PO     : Create New PO for each SO based on suppliers set at product level\n"
#               "Create New Po With New Line     : Create New PO for each SO based on suppliers set at product level and POLine as per SOLine\n"
#               "Create New PO Line: Looking for exisisting PO Quotation for same supplier and added only new line PO."
#     )

#     @api.model
#     def get_default_create_po_or_poline(self, fields):
#         recs = self.env["sale.config.settings"].search([], limit=1, order='id desc')
#         return {'create_po_or_poline': recs and recs[0].create_po_or_poline or False}

class sale_configuration(models.TransientModel):
    _inherit = 'sale.config.settings'

    create_po_or_poline = fields.Selection([
        ('normal', 'Normal'),
        ('create_new_line', 'Create New PO Line'),
        ('create_new_po', 'Create New PO'),
        ('new_po_with_new_line', 'Create New PO With New Line'),
        ],
        string='SO to Create PO/POL',
        default='normal',
        help= "Normal            : Create New Po As Per Base Flow\n"
              "Create New PO     : Create New PO for each SO based on suppliers set at product level\n"
              "Create New Po With New Line     : Create New PO for each SO based on suppliers set at product level and POLine as per SOLine\n"
              "Create New PO Line: Looking for exisisting PO Quotation for same supplier and added only new line PO."
    )

    @api.multi
    def get_default_create_po_or_poline(self):
        po_setting_type = self.env["ir.config_parameter"].get_param("po.settings")
        if not po_setting_type:
            po_setting_type = 'normal'
        return {'create_po_or_poline': po_setting_type or False}
    
    @api.multi
    def set_create_po_or_poline(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("po.settings", record.create_po_or_poline or '')
