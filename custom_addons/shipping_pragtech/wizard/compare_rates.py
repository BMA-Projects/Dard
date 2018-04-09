from openerp.osv import fields, osv

class compare_shipping_rates(osv.osv_memory):
    _name = 'compare.shipping.rates'
    _columns = {
        'shipping_response_id':fields.many2one('shipping.response','Shipping Response Id'),
        'pack_info':fields.char("Packages", size=100),
        'name': fields.char('Service Type', size=100, readonly=True),
        'type': fields.char('Shipping Type', size=64, readonly=True),
        'weight':fields.float('Weight',size=64,readonly=True),
        'rate': fields.float('Rate', size=64, readonly=True),
    }
compare_shipping_rates()
