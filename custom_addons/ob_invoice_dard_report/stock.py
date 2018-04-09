
from openerp import models, fields, api, _

class stock_picking(models.Model):
    _inherit='stock.picking'

    @api.model
    def _create_invoice_from_picking(self,picking, vals):
    	res = super(stock_picking,self)._create_invoice_from_picking(picking,vals)
        if picking.sale_id:
        	attachment_obj =  self.env['ir.attachment']
        	attachment_ids = attachment_obj.search([('res_id','=',picking.sale_id.id),('res_model','=','sale.order')])
        	for att in attachment_ids:
        		attachment_obj.create({'res_id':res,'res_model':'account.invoice','type': 'binary','datas':att.datas,'name':att.name})
        return res