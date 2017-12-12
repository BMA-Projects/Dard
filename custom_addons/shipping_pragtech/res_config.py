from openerp.osv import fields, osv
import openerp
from openerp import SUPERUSER_ID

class stock_config_settings(osv.osv_memory):
    _inherit = 'stock.config.settings'
    _columns = {
                    'shipping_type' : fields.selection([
                                                        ('Fedex','Fedex'),
                                                        ('UPS','UPS'),
                                                        ('USPS','USPS'),],'Address Validation by'),
                    'product_id':fields.many2one('product.product', 'Configure Handling charges (Service Product)'),
                    'priclist_id':fields.many2one('product.pricelist','Handling Charges Pricelist'),
                
                }
    
    _defaults = {
                    'shipping_type':'UPS',
                 }
    
    
    ##getter setter methods of admin_pwd
    def get_default_shipping_type(self, cr, uid, ids, context=None):
        ship_type = self.pool.get("ir.config_parameter").get_param(cr, uid, "mail.catchall.ship", default=None, context=context)
        if not ship_type:
            ship_type = 'UPS'
        return {'shipping_type': ship_type or False}
    
    def set_shipping_type(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "mail.catchall.ship", record.shipping_type or '', context=context)
            
    ##getter setter methods of handling service product
    def get_default_product_id(self, cr, uid, ids, context=None):
        product_id = self.pool.get("ir.config_parameter").get_param(cr, SUPERUSER_ID, "shipping_pragtech.product_id", default=None, context=context)
        if product_id:
            return {'product_id': int(product_id) or False}
        else:
            return {}
     
    def set_product_id(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, SUPERUSER_ID, ids, context=context):
            if record.product_id:
                config_parameters.set_param(cr, SUPERUSER_ID, "shipping_pragtech.product_id", record.product_id.id or False, context=context)
            else:
                config_ids = self.pool.get("ir.config_parameter").search(cr, uid, [('key', '=', 'shipping_pragtech.product_id')])
                if config_ids:
                    self.pool.get("ir.config_parameter").unlink(cr, uid, config_ids)
                    
                    
                    
                    
    ##getter setter methods of pricelist of hadling charges ............
    def get_default_priclist_id(self, cr, uid, ids, context=None):
        priclist_id = self.pool.get("ir.config_parameter").get_param(cr, SUPERUSER_ID, "shipping_pragtech.priclist_id", default=None, context=context)
        if priclist_id:
            return {'priclist_id': int(priclist_id) or False}
        else:
            return {}
     
    def set_priclist_id(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, SUPERUSER_ID, ids, context=context):
            if record.priclist_id:
                config_parameters.set_param(cr, SUPERUSER_ID, "shipping_pragtech.priclist_id", record.priclist_id.id or False, context=context)
            else:
                config_ids = self.pool.get("ir.config_parameter").search(cr, uid, [('key', '=', 'shipping_pragtech.priclist_id')])
                if config_ids:
                    self.pool.get("ir.config_parameter").unlink(cr, uid, config_ids)
            
stock_config_settings()