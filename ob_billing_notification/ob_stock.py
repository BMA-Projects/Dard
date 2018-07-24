# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import osv,fields

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def _state_get(self, cr, uid, ids, field_name, arg, context=None):
        res = super(stock_picking, self)._state_get(cr, uid, ids, field_name=field_name, arg=arg, context=context)
        for picking_id in ids:
            picking = self.browse(cr, uid, picking_id, context=context)
            for key in res:
                if res.get(key) == 'assigned' and not picking.is_mail_sent:
                    self.notify_billing(cr, uid, picking_id, picking.origin, picking.company_id, context=context)
        return res


    def _get_pickings(self, cr, uid, ids, context=None):
        res = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.picking_id:
                res.add(move.picking_id.id)
        return list(res)

    _columns = {
        'state': fields.function(_state_get, type="selection", copy=False,
            store={
                'stock.picking': (lambda self, cr, uid, ids, ctx: ids, ['move_type'], 20),
                'stock.move': (_get_pickings, ['state', 'picking_id', 'partially_available'], 20)},
            selection=[
                ('draft', 'Draft'),
                ('cancel', 'Cancelled'),
                ('waiting', 'Waiting Another Operation'),
                ('confirmed', 'Waiting Availability'),
                ('partially_available', 'Partially Available'),
                ('assigned', 'Ready to Transfer'),
                ('done', 'Transferred'),
                ], string='Status', readonly=True, select=True, track_visibility='onchange',
            help="""
                * Draft: not confirmed yet and will not be scheduled until confirmed\n
                * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
                * Waiting Availability: still waiting for the availability of products\n
                * Partially Available: some products are available and reserved\n
                * Ready to Transfer: products reserved, simply waiting for confirmation.\n
                * Transferred: has been processed, can't be modified or cancelled anymore\n
                * Cancelled: has been cancelled, can't be confirmed anymore"""
        ),
        'is_mail_sent': fields.boolean('Is Mail Sent?'),
    }

    def notify_billing(self, cr, uid, picking_id, origin, company_id, context=None):
        if context is None: context = {}
        group_obj = self.pool.get('res.groups')
        user_obj = self.pool.get('res.users')
        sale_obj = self.pool.get('sale.order')
        mail_mail = self.pool.get('mail.mail')
        
        delivery = self.browse(cr, uid, picking_id, context=context)
        #Check picking type is out and delivery state is Ready to Deliver
        if delivery.picking_type_code == 'outgoing':
            sale_id = sale_obj.search(cr, uid, [('name','=',origin)])
            if sale_id:
                sale = sale_obj.browse(cr, uid, sale_id[0], context=context) or False
                shipping_cost = sale.amount_total
                mail_id = False
                #Check 'Create Invoice' is 'On Demand' and invoice should not be paid.
                if sale.order_policy == 'manual' and not sale.invoiced:
                    category_id = self.pool.get('ir.module.category').search(cr, uid, [('name','=','Warehouse')])
                    manager_ids = group_obj.search(cr, uid, [('name','=', 'Delivery Notifications'),('category_id','in',category_id)])
                    user_ids = group_obj.browse(cr, uid, manager_ids, context=context)[0].users
                    emails = []
                    for user_id in user_ids:
                        if user_id.email:
                            emails.append(user_id.email)
                    email_to = ''
                    for email in emails:
                        email_to = email_to and email_to + ',' + email or email_to + email

                    do = delivery.name and delivery.name or ""
                    body_html = '''
                    <div> 
                        <p>
                        Hello,
                        <br/><br/>
                            Delivery order ''' + do + ''' is ready to ship.
                            <br/><br/>
                            The details of shipping is as below.
                            <br/><br/>
                        </p>
                        <table border="1" cellpadding="5" cellspacing="1">
                            <tbody>
                                <tr>
                                    <td><strong>Delivery Order:</strong></td><td>''' + do + '''</td>
                                </tr>
                                <tr>
                                    <td><strong>Customer:</strong></td><td>''' + delivery.partner_id.name + '''</td>
                                </tr>
                                <tr>
                                    <td><strong>Delivery Method:</strong></td><td>''' + delivery.move_type + '''</td>
                                </tr>
                                <tr>
                                    <td><strong>Total Amount:</strong></td><td>''' + str(shipping_cost) + company_id.currency_id.symbol + '''</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    '''
                    mail_values = {
                        'email_from': company_id.partner_id.email or 'noreply@localhost',
                        'email_to': email_to,
                        'subject': 'Delivery order ' + do + ' is ready to ship',
                        'body_html': body_html,
                        'state': 'outgoing',
                        'type': 'email',
                    }
                    mail_id = mail_mail.create(cr, uid, mail_values, context=context)
                if mail_id:
                    #To avoid sending mail/notification multiple times
                    self.write(cr, uid, picking_id, {'is_mail_sent': True}, context=context)
                    return mail_mail.send(cr, uid, [mail_id], context=context)
                else:
                    return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
