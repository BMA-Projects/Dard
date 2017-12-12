# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from lxml import etree
from openerp.osv.orm import setup_modifiers
from openerp.tools.translate import _

class sale_order(osv.osv):
    _inherit = "sale.order"
        
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:context = {}
        res = super(sale_order, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        order_entry_group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ob_sale_artwork', 'group_virtual_data_entry')[1]
        if view_type == 'form' and order_entry_group_id and order_entry_group_id in [x.id for x in self.pool.get('res.users').browse(cr, uid, uid, context=context).groups_id]:
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='journal_id']")
            for node in nodes:
                node.set('invisible', '1')
                setup_modifiers(node, res['fields']['journal_id'])
            res['arch'] = etree.tostring(doc)
        return res
    

    def _default_journal(self, cr, uid, context={}):
        accountjournal_obj = self.pool.get('account.journal')
        accountjournal_ids = accountjournal_obj.search(cr,uid,[('name','=','Sales Journal')])
        order_entry_group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ob_sale_artwork', 'group_virtual_data_entry')[1]
        if accountjournal_ids and order_entry_group_id and order_entry_group_id not in [x.id for x in self.pool.get('res.users').browse(cr, uid, uid, context=context).groups_id]:
            return accountjournal_ids[0]
        else:
            return False

