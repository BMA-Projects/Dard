from openerp import models, fields, api

class saleperson_wizard(models.TransientModel):
    _name = 'saleperson.wizard'
    _description = 'Sales Person'

    user_id = fields.Many2one('res.users', 'Salesperson')

    @api.multi
    def action_apply(self,data): 
        user_id = self.user_id
        customer_ids = data.get('active_ids')
        customer_objects = self.env['res.partner'].browse(customer_ids) 
        customer_objects.write({'user_id':user_id.id})