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

class StockPicking(models.Model):

    _inherit = "stock.picking"

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        if 'date_expected' in self._context:
            domain.append(('min_date','=',self._context.get('date_expected')))
        return super(StockPicking, self).search(domain)

class stock_move(models.Model):
    _inherit = 'stock.move'

    @api.v7
    def _picking_assign(self, cr, uid, move_ids, procurement_group, location_from, location_to, context=None):
        if not context:
            context = {}
        move_rec = self.browse(cr, uid, move_ids, context=context)[0]
        date_expected = move_rec.date_expected
        context = context.copy()
        context.update({
            'date_expected':date_expected
        })
        return super(stock_move, self)._picking_assign(cr, uid, move_ids, procurement_group, location_from, location_to, context=context)


