# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api, _
import logging
from openerp import tools
import time
from HTMLParser import HTMLParser
from openerp.osv import osv, orm, fields
from openerp import SUPERUSER_ID
from email.utils import formataddr
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

class mail_message(models.Model):
    _inherit = 'mail.message'

    def create(self, cr, uid, values, context=None):
        sale_order_line_image_obj = self.pool.get('sale.order.line.images')
        if 'model' in values:
            if values['model'] == 'sale.order.line.images':
                soli = values['res_id']
                if soli:
                    sale_order_line_image_id = sale_order_line_image_obj.browse(cr, uid, soli)
                    order_id = sale_order_line_image_id and sale_order_line_image_id.order_id and sale_order_line_image_id.order_id.name or ""
                    values['subject'] = "Re:" + order_id + "-" + sale_order_line_image_id.art_image_name
        newid = super(mail_message, self).create(cr, uid, values, context)
        return newid

class mail_compose_message(models.Model):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self):
        msg = super(mail_compose_message, self).send_mail()
        sale_order_line_image_obj = self.env['sale.order.line.images']
        if self.model == 'sale.order.line.images':
            virtual_history_obj = self.env["virtual.history"]
            cur_time = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            if 'sol_image_id' in self._context:
                if self._context['sol_image_id']:
                    history_values = {
                        'sent_date' : cur_time,
                        'sol_image_id' : self._context['sol_image_id'],
                        'name' : self._context['name'],
                        'name_url' : self._context['name_url'],
                        'is_url' : self._context['is_url'],
                        'external_link' : self._context['external_link'],
                    }
                    soli = sale_order_line_image_obj.search([['id','=',self._context['sol_image_id']]])
                    soli.write({'state': 'sent_for_approval', 'sent_for_verification': True})
                    virtual_history_obj.create(history_values)
        return msg

class mail_notification(osv.Model):
    """ Class holding notifications pushed to partners. Followers and partners
        added in 'contacts to notify' receive notifications. """
    _inherit = 'mail.notification'    
    
    def get_partners_to_email(self, cr, uid, ids, message, context=None):
        """ Override method for sent email from Send by Email wizard for sale and invoice 
            without checking partner have notify_email is True (prevent notification).
            
            Return the list of partners to notify, based on their preferences.

            :param browse_record message: mail.message to notify
            :param list partners_to_notify: optional list of partner ids restricting
                the notifications to process
        """
        if not context:
            context = {}
        notify_pids = []
        for notification in self.browse(cr, uid, ids, context=context):
            if notification.is_read:
                continue
            partner = notification.partner_id
            if context.get('parent_model_name', False) and context.get('parent_model_name') == 'sale.order.line.images':
                if context.get('artwork_image_contact_id', False) :
                    artwork_partner_id = self.pool.get('res.partner').browse(cr, uid, context.get('artwork_image_contact_id'))
                    if partner.id == artwork_partner_id.id:
                        if not artwork_partner_id.order_proof_email and not artwork_partner_id.email:
                            continue
                    else:
                        if not partner.email:
                            continue
                else:
                    if context.get('artwork_partner_id', False) :
                        artwork_partner_id = self.pool.get('res.partner').browse(cr, uid, context.get('artwork_partner_id'))
                        if partner.id == artwork_partner_id.id:
                            if not artwork_partner_id.order_proof_email and not artwork_partner_id.email:
                                continue
                        else:
                            if not partner.email:
                                continue
            else:
                if not partner.email:
                    continue

            # Do not send to partners having same email address than the author (can cause loops or bounce effect due to messy database)
            if message.author_id and message.author_id.email == partner.email:
                continue
                
            # Partner does not want to receive any emails or is opt-out
            if partner.notify_email == 'none':
                if not (partner.allow_send_by_email):
                    continue
            notify_pids.append(partner.id)
        return notify_pids


class mail_mail(osv.Model):
    """ Model holding RFC2822 email messages to send. This model also provides
        facilities to queue and send new email messages.  """
    _inherit = 'mail.mail'
    
    def send_get_mail_to(self, cr, uid, mail, partner=None, context=None):
        """Forge the email_to with the following heuristic:
          - if 'partner', recipient specific (Partner Name <email>)
          - else fallback on mail.email_to splitting """
        res = super(mail_mail, self).send_get_mail_to(cr, uid, mail=mail, partner=partner, context=context)
        if partner:
            if context.get('parent_model_name', False) and context.get('parent_model_name') == 'sale.order.line.images':
                if context.get('artwork_image_contact_id', False) :
                    artwork_partner_id = self.pool.get('res.partner').browse(cr, uid, context.get('artwork_image_contact_id'))
                    if partner.id == artwork_partner_id.id and artwork_partner_id.order_proof_email:
                        email_to = [formataddr((artwork_partner_id.name, artwork_partner_id.order_proof_email))]
                    else:
                        email_to = [formataddr((partner.name, partner.email))]
                else:
                    if context.get('artwork_partner_id', False) :
                        artwork_partner_id = self.pool.get('res.partner').browse(cr, uid, context.get('artwork_partner_id'))
                        if partner.id == artwork_partner_id.id and artwork_partner_id.order_proof_email:
                            email_to = [formataddr((artwork_partner_id.name, artwork_partner_id.order_proof_email))]
                        else:
                            email_to = [formataddr((partner.name, partner.email))]
            else:
                email_to = [formataddr((partner.name, partner.email))]
        else:
            email_to = tools.email_split(mail.email_to)
        return email_to
