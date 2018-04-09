from openerp import models, fields, api, _
from datetime import datetime,date
from openerp.exceptions import Warning
from openerp.tools.translate import _
from openerp.exceptions import Warning
from lxml import etree
from openerp.osv.orm import setup_modifiers

class res_partner(models.Model):
    _inherit = 'res.partner'

    device_id = fields.Char('Device')
    contact_id = fields.Integer('Contact')

    def sync_customer(self, cr, uid, ids, vals, context=None):
        if context is None: context = {}
        if vals.has_key('contacts') and vals['contacts']:
            for cust in vals['contacts']:
                args = [('device_id', '=' ,cust['device_id']),('contact_id', '=', cust['contact_id'])]
                cust_ids = self.search(cr, uid, args, context=context)
                if not cust_ids:
                    val = {}
                    val['name'] = cust['name'] or False
                    val['mobile'] = 'mobile' in cust and cust['mobile'] or False
                    val['phone'] = 'phone' in cust and cust['phone'] or False
                    val['email'] = 'email' in cust and cust['email'] or False
                    val['fax'] = 'Fax' in cust and cust['Fax'] or False
                    val['city'] = 'city' in cust and cust['city'] or False
                    val['state_id'] = 'state' in cust and cust['state'] or False
                    #val['country_id'] = cust['country'] or False
                    val['street'] = 'street' in cust and cust['street']
                    val['website'] = 'website' in cust and cust['website'] or False
                    val['zip'] = 'zip' in cust and cust['zip'] or False
                    val['image'] = 'image' in cust and cust['image']
                    val['device_id'] = cust['device_id'] or False
                    val['contact_id'] = cust['contact_id'] or False
                    self.create(cr, uid, val, context)
                else:
                    for cust_id in cust_ids:
                        val = {}
                        val['name'] = cust['name'] or False
                        val['mobile'] = 'mobile' in cust and cust['mobile'] or False
                        val['phone'] = 'phone' in cust and cust['phone'] or False
                        val['email'] = 'email' in cust and cust['email'] or False
                        val['fax'] = 'Fax' in cust and cust['Fax'] or False
                        val['city'] = 'city' in cust and cust['city'] or False
                        val['state_id'] = 'state' in cust and cust['state'] or False
                        #val['country_id'] = cust['country'] or False
                        val['street'] = 'street' in cust and cust['street']
                        val['website'] = 'website' in cust and cust['website'] or False
                        val['zip'] = 'zip' in cust and cust['zip'] or False
                        val['image'] = 'image' in cust and cust['image']
                        val['device_id'] = cust['device_id'] or False
                        val['contact_id'] = cust['contact_id'] or False
                        self.write(cr, uid, cust_id, val, context=context)
        return True
