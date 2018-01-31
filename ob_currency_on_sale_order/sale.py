from openerp.osv import fields, osv

class sale_order(osv.osv):
    _inherit = "sale.order"
    
    _columns = {
        'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency", string="Currency",
                                      store={
                                             'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['pricelist_id'], 10)
                                             }),
                }