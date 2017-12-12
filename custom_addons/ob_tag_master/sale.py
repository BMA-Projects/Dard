# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp import models, fields, api, _
from openerp.exceptions import Warning,ValidationError

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    screen_ready = fields.Char('Screen #', size=6)

class sale_order(models.Model):
    _inherit = 'sale.order'

    client_po_ref = fields.Char('Customer PO Number', size=64)
    testmode = fields.Char('Test', size=64)

    _sql_constraints = [
        ('client_po_ref_unique', 'unique (client_po_ref)', 'You can not enter duplicate Customer PO Number !')
    ]

    # def onchange_client_po_ref(self, cr, uid, ids, client_po_ref, customer_id, context=None):
    #     context = context or {}
    #     res = {}
    #     if client_po_ref and customer_id:
    #         search_val = self.search(cr, uid, [('partner_id','=',customer_id), ('client_po_ref','=',client_po_ref)], context=context)
    #         if search_val:
    #             warning = {
    #                 'title': _('Warning!'),
    #                 'message' : _("You can not use same 'Customer PO Number' twice.")
    #             }
    #             return {'warning': warning}
    #     return res

    def action_button_confirm(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)
        partner_obj = self.pool.get("res.partner")
        tmpl_obj = self.pool.get('email.template')
        order = self.browse(cr, uid, ids, context=context)
        for rec in order:
            if not rec.client_po_ref or rec.client_po_ref == '':
                error = ValidationError(_('Customer PO Number must be required !'))
                setattr(error, 'args', ('Warning', error.value))
                raise error
            partner_id = rec.partner_id
            if partner_id:
                id = partner_id.id
                partner_ids = partner_obj.search(cr, uid, [('id','=',id)], context=context)
                partner = partner_obj.browse(cr, uid, id, context=context)
                email_from = rec.company_id.email 
                email_to = partner.email
#                 if not email_to:
#                     email_to = partner.email
                if not email_from:
                    email_from = 'noreply@localhost'
                tmpl_ids = tmpl_obj.search(cr, uid, [('name','=','E-mail Notification Template')])
                if tmpl_ids:
                    tmpl_obj.write(cr, uid, tmpl_ids[0], {'email_to':email_to,'email_from': email_from}, context=context)
                    tmpl_obj.send_mail(cr, uid, tmpl_ids[0], rec.id, True,)
        return res

    def print_quotation(self, cr, uid, ids, context=None):
        '''
        This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        self.signal_workflow(cr, uid, ids, 'quotation_sent')
        return self.pool['report'].get_action(cr, uid, ids, 'ob_tag_master.report_saleorder', context=context)


    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, part, context=context)
        partner_shipping_id = res['value'].get('partner_shipping_id', False)
        if partner_shipping_id:
            res['value'].update({'partner_shipping_id': False})
        return res

class category_code(models.Model):
    _name = 'category.code'

    _rec_name = 'code'

    code = fields.Char('Code')
    description = fields.Char('Description')

class res_country_state(models.Model):
    _inherit = 'res.country.state'

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.code:                
                result.append((record.id, '%s' % (record.code)))
            else:
                result.append((record.id,'%s' % (record.name)))
        return result

class res_partner(models.Model):
    _inherit = 'res.partner'

    sales_goal = fields.Float('Sales Goal')
    federal_id = fields.Char('Federal ID Number')
    federal_type = fields.Selection([('federal', 'Federal Tax ID'), ('social', 'Social Security Number')], 'Federal ID Type')
    categ_code_id = fields.Many2one('category.code', string='1099 Category Code')

class SaleOrderLineImages(models.Model):
    
    """
    This model used for Artwork and Virtual files.
    ==============================================
    ->    On creating or modifying record it will store artwork file and virtual file at the physical storage.
    ->    States will indicate the status of particular Artwork.
    ->    User can upload multiple Artwork and will get multiple virtual files.
    ->    At least one Artwork should be Confirmed.
    ->    It will keep track of changing the states.
    """
    
    _inherit = "sale.order.line.images"
    _track = {
        'state': {
            'ob_sale.mt_sol_new': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'ob_sale.mt_sol_sent_for_approval': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'sent_for_approval',
            'ob_sale.mt_sol_confirmed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirmed',
            'ob_sale.mt_sol_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
            'ob_sale.mt_sol_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
            'ob_sale.mt_sol_stage': lambda self, cr, uid, obj, ctx=None: obj['state'] not in ['draft', 'sent_for_approval', 'confirmed','done', 'cancel']
        },
    }
    
    state = fields.Selection([
                ('draft', 'Virtual Pending'),
                ('sent_for_approval', 'Sent for Approval'),
                ('confirmed', 'Approved'),
                ('cancel', 'Send Another Virtual')], 'Status', required=True,readonly=True,
            track_visibility='onchange', default='draft',
            help='* The \'Virtual Pending\' status is set when new sale order line will created. \
                \n* The \'Sent for Approval\' status is set when Virtual team send the mail to customer for approval. \
                \n* The \'Approved\' status is set when customer will approved the virtual. \
                \n* The \'Approved with changes\' status is set when customer will approved the virtual. \
                \n* The \'Send Another Virtual\' status is set when customer will reject the current virtual or disapproved the sent virtual.')

    @api.v8
    def _send_email(self):
        """
        Send mail for verify the virtual artwork uploaded by Artwork Team.
        @return: True
        """
        
        email_temp_obj = self.env['email.template']
        mail_mail_obj = self.env['mail.mail']
        order_proof_email = self.partner_id.order_proof_email or self.partner_id.email
        template_id = self.env['ir.model.data'].get_object_reference('ob_tag_master', 'email_template_edi_virtual_process_dard')[1]
        msg_id = email_temp_obj.search([['id','=',template_id]]).send_mail(self.id)[0]
        msg_rec = mail_mail_obj.search([['id','=',msg_id]])
        msg_rec.write({'email_to': order_proof_email,'auto_delete': True})
        msg_rec.send()
        msg_rec1 = mail_mail_obj.search([['id','=',msg_id]])
        if msg_rec1.id:
            return False
        else:
            return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
