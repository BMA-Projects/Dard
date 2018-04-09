from openerp.osv import fields, osv
from datetime import datetime
class shipping_report(osv.osv):
    _name = "shipping.report"

    _columns = {
        'sale_order' : fields.char('Sale Order'), #SO101
        'sale_order_date' : fields.datetime('Sales Order Date'), #07/01/2015
        'customer' : fields.many2one('res.partner', 'Customer'), #ABC
        'delivery_order' : fields.char('Delivery Order'), #WH/OUT/2012
        'delivery_date' : fields.datetime('Delivery Date'), #07/05/2015
        'delivery_address' : fields.char('Delivery address'), #ABC
        'delivery_state' : fields.many2one('res.country.state', 'Delivery State'), #CA
        'delivery_country' : fields.many2one('res.country', 'Delivery Country'), #US
        'shipping_carrier' : fields.many2one('delivery.carrier', 'Shipping Carrier'), #FedEx
        'shipping_type' : fields.char('Shipping Type'), #FedEx_Ground
        'total_shipping_cost' : fields.float('Total Shipping Cost'), #25
        'state' : fields.char("Status"),
    }
shipping_report()