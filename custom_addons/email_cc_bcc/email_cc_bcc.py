# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import re
import base64
import logging


import openerp
import openerp.report
from openerp import netsvc
from openerp import tools
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.osv.orm import except_orm
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class mail_compose_message(osv.TransientModel):
    _inherit = 'mail.compose.message'
    _columns = {
        'email_cc_ids': fields.many2many('res.partner',
            'mail_compose_message_res_partner_cc_rel',
            'wizard_id', 'partner_cc_id', 'Email CC'),
        'email_bcc_ids': fields.many2many('res.partner',
            'mail_compose_message_res_partner_bcc_rel',
            'wizard_id', 'partner_bcc_id', 'Email BCC'),
    }
    _defaults = {
         'email_cc_ids': lambda self, cr, uid, ctx={}: [],
         'email_bcc_ids': lambda self, cr, uid, ctx={}: [],
    }
    def generate_email_for_composer(self, cr, uid, template_id, res_id, context=None):
        """ Call email_template.generate_email(), get fields relevant for
            mail.compose.message, transform email_cc and email_to into partner_ids """

        template_values = self.pool.get('email.template').generate_email(cr, uid, template_id, res_id, context=context)
        # filter template values
        fields = ['body_html', 'subject', 'email_to', 'email_recipients', 'email_cc','email_bcc', 'attachment_ids', 'attachments']
        values = dict((field, template_values[field]) for field in fields if template_values.get(field))
        values['body'] = values.pop('body_html', '')

        # transform email_to, email_cc into partner_ids
        partner_ids = set()
        partner_cc_ids = set()
        partner_bcc_ids = set()
        mails = tools.email_split(values.pop('email_to', ''))
        mails_cc = tools.email_split(values.pop('email_cc', ''))
        mails_bcc = tools.email_split(values.pop('email_bcc', ''))
        ctx = dict((k, v) for k, v in (context or {}).items() if not k.startswith('default_'))
        for mail in mails:
            partner_id = self.pool.get('res.partner').find_or_create(cr, uid, mail, context=ctx)
            partner_ids.add(partner_id)
        for mail_cc in mails_cc:
            partner_cc_id = self.pool.get('res.partner').find_or_create(cr, uid, mail_cc, context=ctx)
            partner_cc_ids.add(partner_cc_id)
            
        for mail_bcc in mails_bcc:
            partner_bcc_id = self.pool.get('res.partner').find_or_create(cr, uid, mail_bcc, context=ctx)
            partner_bcc_ids.add(partner_bcc_id)
        email_recipients = values.pop('email_recipients', '')
        if email_recipients:
            for partner_id in email_recipients.split(','):
                if partner_id:  # placeholders could generate '', 3, 2 due to some empty field values
                    partner_ids.add(int(partner_id))
            

        # legacy template behavior: void values do not erase existing values and the
        # related key is removed from the values dict
        if partner_ids:
            values['partner_ids'] = list(partner_ids)
        if partner_cc_ids:
            values['email_cc_ids'] = list(partner_cc_ids)
        if partner_bcc_ids:
            values['email_bcc_ids'] = list(partner_bcc_ids)
        return values
    
    def onchange_template_id(self, cr, uid, ids, template_id, composition_mode, model, res_id, context=None):
        """ - mass_mailing: we cannot render, so return the template values
            - normal mode: return rendered values """
        if template_id and composition_mode == 'mass_mail':
            values = self.pool.get('email.template').read(cr, uid, template_id, ['subject', 'body_html', 'attachment_ids'], context)
            values.pop('id')
        elif template_id:
            values = self.generate_email_for_composer(cr, uid, template_id, res_id, context=context)
            # transform attachments into attachment_ids; not attached to the document because this will
            # be done further in the posting process, allowing to clean database if email not send
            values['attachment_ids'] = values.pop('attachment_ids', [])
            ir_attach_obj = self.pool.get('ir.attachment')
            for attach_fname, attach_datas in values.pop('attachments', []):
                data_attach = {
                    'name': attach_fname,
                    'datas': attach_datas,
                    'datas_fname': attach_fname,
                    'res_model': 'mail.compose.message',
                    'res_id': 0,
                    'type': 'binary',  # override default_type from context, possibly meant for another model!
                }
                values['attachment_ids'].append(ir_attach_obj.create(cr, uid, data_attach, context=context))
        else:
            values = self.default_get(cr, uid, ['body', 'subject', 'partner_ids', 'attachment_ids','email_cc_ids','email_bcc_ids'], context=context)
        if values.get('body_html'):
            values['body'] = values.pop('body_html')
        return {'value': values}
    
    def send_mail(self, cr, uid, ids, context=None):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed. """
        if context is None:
            context = {}
        ir_attachment_obj = self.pool.get('ir.attachment')
        active_ids = context.get('active_ids')
        is_log = context.get('mail_compose_log', False)

        for wizard in self.browse(cr, uid, ids, context=context):
            mass_mail_mode = wizard.composition_mode == 'mass_mail'
            active_model_pool_name = wizard.model if wizard.model else 'mail.thread'
            active_model_pool = self.pool.get(active_model_pool_name)

            # wizard works in batch mode: [res_id] or active_ids
            res_ids = active_ids if mass_mail_mode and wizard.model and active_ids else [wizard.res_id]

            for res_id in res_ids:
                # mail.message values, according to the wizard options
                post_values = {
                    'subject': wizard.subject,
                    'body': wizard.body,
                    'parent_id': wizard.parent_id and wizard.parent_id.id,
                    'partner_ids': [partner.id for partner in wizard.partner_ids],
                    'email_cc_ids': [(4,partner_cc.id) for partner_cc in wizard.email_cc_ids],
                    'email_bcc_ids': [(4,partner_bcc.id) for partner_bcc in wizard.email_bcc_ids],
                    'attachment_ids': [attach.id for attach in wizard.attachment_ids],
                }
                
                # mass mailing: render and override default values
                if mass_mail_mode and wizard.model:
                    email_dict = self.render_message(cr, uid, wizard, res_id, context=context)
                    post_values['partner_ids'] += email_dict.pop('partner_ids', [])
                    post_values['attachments'] = email_dict.pop('attachments', [])
                    attachment_ids = []
                    for attach_id in post_values.pop('attachment_ids'):
                        new_attach_id = ir_attachment_obj.copy(cr, uid, attach_id, {'res_model': self._name, 'res_id': wizard.id}, context=context)
                        attachment_ids.append(new_attach_id)
                    post_values['attachment_ids'] = attachment_ids
                    post_values.update(email_dict)
                # post the message
                
                subtype = 'mail.mt_comment'
                if is_log:  # log a note: subtype is False
                    subtype = False
                elif mass_mail_mode:  # mass mail: is a log pushed to recipients, author not added
                    subtype = False
                    context = dict(context, mail_create_nosubscribe=True)  # add context key to avoid subscribing the author
                msg_id = active_model_pool.message_post(cr, uid, [res_id], type='comment', subtype=subtype, context=context, **post_values)
                # mass_mailing: notify specific partners, because subtype was False, and no-one was notified
                if mass_mail_mode and post_values['partner_ids']:
                    self.pool.get('mail.notification')._notify(cr, uid, msg_id, post_values['partner_ids'], context=context)

        return {'type': 'ir.actions.act_window_close'}
mail_compose_message()

class mail_message(osv.Model):
    _inherit = 'mail.message'
    _columns = {
        'email_cc_ids': fields.many2many('res.partner', 'mail_notification_cc',
            'message_id', 'partner_id', 'CC',
            help='Partners that have a notification pushing this message in their mailboxes'),
        'email_bcc_ids': fields.many2many('res.partner', 'mail_notification_bcc',
            'message_id', 'partner_id', 'BCC',
            help='Partners that have a notification pushing this message in their mailboxes'),
    }
    
mail_message()

class mail_notification(osv.Model):
    _inherit = 'mail.notification'
    
    def _notify(self, cr, uid, msg_id, partners_to_notify=None, context=None, force_send=False, user_signature=True):
        """ Send by email the notification depending on the user preferences

            :param list partners_to_notify: optional list of partner ids restricting
                the notifications to process
        """
        if context is None:
            context = {}
        mail_message_obj = self.pool.get('mail.message')
        # optional list of partners to notify: subscribe them if not already done or update the notification
        if partners_to_notify:
            notifications_to_update = []
            notified_partners = []
            notif_ids = self.search(cr, SUPERUSER_ID, [('message_id', '=', msg_id), ('partner_id', 'in', partners_to_notify)], context=context)
            for notification in self.browse(cr, SUPERUSER_ID, notif_ids, context=context):
                notified_partners.append(notification.partner_id.id)
                notifications_to_update.append(notification.id)
            partners_to_notify = filter(lambda item: item not in notified_partners, partners_to_notify)
            if notifications_to_update:
                self.write(cr, SUPERUSER_ID, notifications_to_update, {'read': False}, context=context)
            
            mail_message_obj.write(cr, uid, msg_id, {'notified_partner_ids': [(4, id) for id in partners_to_notify]}, context=context)

        # mail_notify_noemail (do not send email) or no partner_ids: do not send, return
        if context.get('mail_notify_noemail'):
            return True
        # browse as SUPERUSER_ID because of access to res_partner not necessarily allowed
        msg = self.pool.get('mail.message').browse(cr, SUPERUSER_ID, msg_id, context=context)
        
         
        notify_partner_ids = self.get_partners_to_email(cr, SUPERUSER_ID,[x.id for x in msg.notification_ids], msg, context=context)
        if not notify_partner_ids:
            return True

        # add the context in the email
        # TDE FIXME: commented, to be improved in a future branch
        # quote_context = self.pool.get('mail.message').message_quote_context(cr, uid, msg_id, context=context)

        mail_mail = self.pool.get('mail.mail')
        # add signature
        body_html = msg.body
        # if quote_context:
            # body_html = tools.append_content_to_html(body_html, quote_context, plaintext=False)
        signature = msg.author_id and msg.author_id.user_ids and msg.author_id.user_ids[0].signature or ''
        if signature:
            body_html = tools.append_content_to_html(body_html, signature, plaintext=True, container_tag='div')

        # email_from: partner-user alias or partner email or mail.message email_from
        if msg.author_id and msg.author_id.user_ids and msg.author_id.user_ids[0].alias_domain and msg.author_id.user_ids[0].alias_name:
            email_from = '%s <%s@%s>' % (msg.author_id.name, msg.author_id.user_ids[0].alias_name, msg.author_id.user_ids[0].alias_domain)
        elif msg.author_id:
            email_from = '%s <%s>' % (msg.author_id.name, msg.author_id.email)
        else:
            email_from = msg.email_from
        cc_email_list = []
        for cc in msg.email_cc_ids:
            cc_email_list.append(self.pool.get('res.partner').browse(cr,uid,cc.id).email)

        bcc_email_list = []
        for bcc in msg.email_bcc_ids:
            bcc_email_list.append(self.pool.get('res.partner').browse(cr,uid,bcc.id).email)
        
        references = False
        if msg.parent_id:
            references = msg.parent_id.message_id
        mail_values = {
            'mail_message_id': msg.id,
            'auto_delete': True,
            'body_html': body_html,
            'email_from': email_from,
            'references': references,
            'email_cc': ",".join(cc_email_list),
            'email_bcc':",".join(bcc_email_list),
        }
        email_notif_id = mail_mail.create(cr, uid, mail_values, context=context)
        try:
            return mail_mail.send(cr, uid, [email_notif_id], recipient_ids=notify_partner_ids, context=context)
        except Exception:
            return False
mail_notification()

class mail_thread(osv.AbstractModel):
    _inherit = 'mail.thread'

    def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification',
                        subtype=None, parent_id=False, attachments=None, context=None,
                        content_subtype='html', **kwargs):
        
        """ Post a new message in an existing thread, returning the new
            mail.message ID.

            :param int thread_id: thread ID to post into, or list with one ID;
                if False/0, mail.message model will also be set as False
            :param str body: body of the message, usually raw HTML that will
                be sanitized
            :param str type: see mail_message.type field
            :param str content_subtype:: if plaintext: convert body into html
            :param int parent_id: handle reply to a previous message by adding the
                parent partners to the message in case of private discussion
            :param tuple(str,str) attachments or list id: list of attachment tuples in the form
                ``(name,content)``, where content is NOT base64 encoded

            Extra keyword arguments will be used as default column values for the
            new mail.message record. Special cases:
                - attachment_ids: supposed not attached to any document; attach them
                    to the related document. Should only be set by Chatter.
            :return int: ID of newly created mail.message
        """
        if context is None:
            context = {}
        if attachments is None:
            attachments = {}
        mail_message = self.pool.get('mail.message')
        ir_attachment = self.pool.get('ir.attachment')

        assert (not thread_id) or \
                isinstance(thread_id, (int, long)) or \
                (isinstance(thread_id, (list, tuple)) and len(thread_id) == 1), \
                "Invalid thread_id; should be 0, False, an ID or a list with one ID"
        if isinstance(thread_id, (list, tuple)):
            thread_id = thread_id[0]

        # if we're processing a message directly coming from the gateway, the destination model was
        # set in the context.
        model = False
        if thread_id:
            model = context.get('thread_model', self._name) if self._name == 'mail.thread' else self._name
            if model != self._name:
                del context['thread_model']
                return self.pool.get(model).message_post(cr, uid, thread_id, body=body, subject=subject, type=type, subtype=subtype, parent_id=parent_id, attachments=attachments, context=context, content_subtype=content_subtype, **kwargs)

        # 0: Parse email-from, try to find a better author_id based on document's followers for incoming emails
        email_from = kwargs.get('email_from')
        if email_from and thread_id and type == 'email' and kwargs.get('author_id'):
            email_list = tools.email_split(email_from)
            doc = self.browse(cr, uid, thread_id, context=context)
            if email_list and doc:
                author_ids = self.pool.get('res.partner').search(cr, uid, [
                                        ('email', 'ilike', email_list[0]),
                                        ('id', 'in', [f.id for f in doc.message_follower_ids])
                                    ], limit=1, context=context)
                if author_ids:
                    kwargs['author_id'] = author_ids[0]
        author_id = kwargs.get('author_id')
        if author_id is None:  # keep False values
            author_id = self.pool.get('mail.message')._get_default_author(cr, uid, context=context)

        # 1: Handle content subtype: if plaintext, converto into HTML
        if content_subtype == 'plaintext':
            body = tools.plaintext2html(body)

        # 2: Private message: add recipients (recipients and author of parent message) - current author
        #   + legacy-code management (! we manage only 4 and 6 commands)
        partner_ids = set()
        kwargs_partner_ids = kwargs.pop('partner_ids', [])
        for partner_id in kwargs_partner_ids:
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 4 and len(partner_id) == 2:
                partner_ids.add(partner_id[1])
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 6 and len(partner_id) == 3:
                partner_ids |= set(partner_id[2])
            elif isinstance(partner_id, (int, long)):
                partner_ids.add(partner_id)
            else:
                pass  # we do not manage anything else
            
        email_cc_ids = set()
        kwargs_email_cc_ids = kwargs.pop('email_cc_ids', [])
        for email_cc_id in kwargs_email_cc_ids:
            if isinstance(partner_id, (list, tuple)) and email_cc_id[0] == 4 and len(email_cc_id) == 2:
                email_cc_ids.add(email_cc_id[1])
            if isinstance(email_cc_id, (list, tuple)) and email_cc_id[0] == 6 and len(email_cc_id) == 3:
                email_cc_ids |= set(email_cc_id[2])
            elif isinstance(email_cc_id, (int, long)):
                email_cc_ids.add(email_cc_id)
            else:
                pass  # we do not manage anything else
        email_bcc_ids = set()
        kwargs_email_bcc_ids = kwargs.pop('email_bcc_ids', [])
        for email_bcc_id in kwargs_email_bcc_ids:
            if isinstance(partner_id, (list, tuple)) and email_bcc_id[0] == 4 and len(email_bcc_id) == 2:
                email_bcc_ids.add(email_bcc_id[1])
            if isinstance(email_bcc_id, (list, tuple)) and email_bcc_id[0] == 6 and len(email_bcc_id) == 3:
                email_bcc_ids |= set(email_bcc_id[2])
            elif isinstance(email_bcc_id, (int, long)):
                email_bcc_ids.add(email_bcc_id)
            else:
                pass  # we do not manage anything else
        
            
            
        if parent_id and not model:
            parent_message = mail_message.browse(cr, uid, parent_id, context=context)
            private_followers = set([partner.id for partner in parent_message.partner_ids])
            if parent_message.author_id:
                private_followers.add(parent_message.author_id.id)
            private_followers -= set([author_id])
            partner_ids |= private_followers

        # 3. Attachments
        #   - HACK TDE FIXME: Chatter: attachments linked to the document (not done JS-side), load the message
        attachment_ids = kwargs.pop('attachment_ids', []) or []  # because we could receive None (some old code sends None)
        if attachment_ids:
            filtered_attachment_ids = ir_attachment.search(cr, SUPERUSER_ID, [
                ('res_model', '=', 'mail.compose.message'),
                ('create_uid', '=', uid),
                ('id', 'in', attachment_ids)], context=context)
            if filtered_attachment_ids:
                ir_attachment.write(cr, SUPERUSER_ID, filtered_attachment_ids, {'res_model': model, 'res_id': thread_id}, context=context)
        attachment_ids = [(4, id) for id in attachment_ids]
        # Handle attachments parameter, that is a dictionary of attachments
        for name, content in attachments:
            if isinstance(content, unicode):
                content = content.encode('utf-8')
            data_attach = {
                'name': name,
                'datas': base64.b64encode(str(content)),
                'datas_fname': name,
                'description': name,
                'res_model': model,
                'res_id': thread_id,
            }
            attachment_ids.append((0, 0, data_attach))

        # 4: mail.message.subtype
        subtype_id = False
        if subtype:
            if '.' not in subtype:
                subtype = 'mail.%s' % subtype
            ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, *subtype.split('.'))
            subtype_id = ref and ref[1] or False

        # automatically subscribe recipients if asked to
        if context.get('mail_post_autofollow') and thread_id and partner_ids:
            partner_to_subscribe = partner_ids
            if context.get('mail_post_autofollow_partner_ids'):
                partner_to_subscribe = filter(lambda item: item in context.get('mail_post_autofollow_partner_ids'), partner_ids)
            self.message_subscribe(cr, uid, [thread_id], list(partner_to_subscribe), context=context)
        # _mail_flat_thread: automatically set free messages to the first posted message
        if self._mail_flat_thread and not parent_id and thread_id:
            message_ids = mail_message.search(cr, uid, ['&', ('res_id', '=', thread_id), ('model', '=', model)], context=context, order="id ASC", limit=1)
            parent_id = message_ids and message_ids[0] or False
        # we want to set a parent: force to set the parent_id to the oldest ancestor, to avoid having more than 1 level of thread
        elif parent_id:
            message_ids = mail_message.search(cr, SUPERUSER_ID, [('id', '=', parent_id), ('parent_id', '!=', False)], context=context)
            # avoid loops when finding ancestors
            processed_list = []
            if message_ids:
                message = mail_message.browse(cr, SUPERUSER_ID, message_ids[0], context=context)
                while (message.parent_id and message.parent_id.id not in processed_list):
                    processed_list.append(message.parent_id.id)
                    message = message.parent_id
                parent_id = message.id
        
        values = kwargs
        values.update({
            'author_id': author_id,
            'model': model,
            'res_id': thread_id or False,
            'body': body,
            'subject': subject or False,
            'type': type,
            'parent_id': parent_id,
            'attachment_ids': attachment_ids,
            'subtype_id': subtype_id,
            'partner_ids': [(4, pid) for pid in partner_ids],
            'email_cc_ids':[(4, ccid) for ccid in email_cc_ids],
            'email_bcc_ids':[(4, bccid) for bccid in email_bcc_ids],
        })
        # Avoid warnings about non-existing fields
        for x in ('from', 'to', 'cc'):
            values.pop(x, None)
        # Create and auto subscribe the author
        msg_id = mail_message.create(cr, uid, values, context=context)
        message = mail_message.browse(cr, uid, msg_id, context=context)
        if message.author_id and thread_id and type != 'notification' and not context.get('mail_create_nosubscribe'):
            self.message_subscribe(cr, uid, [thread_id], [message.author_id.id], context=context)
        return msg_id

mail_thread()
class mail_mail(osv.Model):
    _inherit = 'mail.mail'
    _columns = {
        'email_bcc': fields.char('Bcc', help='Black Carbon copy message recipients'),
    }
    
    def send(self, cr, uid, ids, auto_commit=False, raise_exception=False, recipient_ids=None, context=None):
    
        """ Sends the selected emails immediately, ignoring their current
            state (mails that have already been sent should not be passed
            unless they should actually be re-sent).
            Emails successfully delivered are marked as 'sent', and those
            that fail to be deliver are marked as 'exception', and the
            corresponding error mail is output in the server logs.

            :param bool auto_commit: whether to force a commit of the mail status
                after sending each mail (meant only for scheduler processing);
                should never be True during normal transactions (default: False)
            :param list recipient_ids: specific list of res.partner recipients.
                If set, one email is sent to each partner. Its is possible to
                tune the sent email through ``send_get_mail_body`` and ``send_get_mail_subject``.
                If not specified, one email is sent to mail_mail.email_to.
            :return: True
        """
        ir_mail_server = self.pool.get('ir.mail_server')
        for mail in self.browse(cr, uid, ids, context=context):
            try:
                # handle attachments
                attachments = []
                for attach in mail.attachment_ids:
                    attachments.append((attach.datas_fname, base64.b64decode(attach.datas)))
                # specific behavior to customize the send email for notified partners
                email_list = []
                if recipient_ids:
                    partner_obj = self.pool.get('res.partner')
                    existing_recipient_ids = partner_obj.exists(cr, SUPERUSER_ID, recipient_ids, context=context)
                    for partner in partner_obj.browse(cr, SUPERUSER_ID, existing_recipient_ids, context=context):
                        email_list.append(self.send_get_email_dict(cr, uid, mail, partner=partner, context=context))
                else:
                    email_list.append(self.send_get_email_dict(cr, uid, mail, context=context))

                # build an RFC2822 email.message.Message object and send it without queuing
                res = None
                temp_mail= ''
                for email in email_list:
                    temp_mail += email.get('email_to')[0] + ','
                msg = ir_mail_server.build_email(
                    email_from = mail.email_from,
                    email_to = [temp_mail],
                    subject = email.get('subject'),
                    body = email.get('body'),
                    body_alternative = email.get('body_alternative'),
                    email_cc = tools.email_split(mail.email_cc),
                    email_bcc = tools.email_split(mail.email_bcc),
                    reply_to = email.get('reply_to'),
                    attachments = attachments,
                    message_id = mail.message_id,
                    references = mail.references,
                    object_id = mail.res_id and ('%s-%s' % (mail.res_id, mail.model)),
                    subtype = 'html',
                    subtype_alternative = 'plain')
                res = ir_mail_server.send_email(cr, uid, msg,
                    mail_server_id=mail.mail_server_id.id, context=context)
        
                if res:
                    mail.write({'state': 'sent', 'message_id': res})
                    mail_sent = True
                else:
                    mail.write({'state': 'exception'})
                    mail_sent = False

                # /!\ can't use mail.state here, as mail.refresh() will cause an error
                # see revid:odo@openerp.com-20120622152536-42b2s28lvdv3odyr in 6.1
                if mail_sent:
                    self._postprocess_sent_message(cr, uid, mail, context=context)
            except Exception:
                _logger.exception('failed sending mail.mail %s', mail.id)
                mail.write({'state': 'exception'})

            if auto_commit == True:
                cr.commit()
        return True
mail_mail()

class email_template(osv.osv):
    "Templates for sending email"
    _inherit = "email.template"
    _columns = {
        'email_bcc': fields.char('Bcc', help="Carbon copy recipients (placeholders may be used here)"),
    }
    def generate_email(self, cr, uid, template_id, res_id, context=None):

        """Generates an email from the template for given (model, res_id) pair.

           :param template_id: id of the template to render.
           :param res_id: id of the record to use for rendering the template (model
                          is taken from template definition)
           :returns: a dict containing all relevant fields for creating a new
                     mail.mail entry, with one extra key ``attachments``, in the
                     format expected by :py:meth:`mail_thread.message_post`.
        """
        if context is None:
            context = {}
        report_xml_pool = self.pool.get('ir.actions.report.xml')
        template = self.get_email_template(cr, uid, template_id, res_id, context)
        values = {}
        for field in ['subject', 'body_html', 'email_from',
                      'email_to', 'partner_to', 'email_cc','email_bcc', 'reply_to']:
            values[field] = self.render_template(cr, uid, getattr(template, field),
                                                 template.model, res_id, context=context) \
                                                 or False
        if template.user_signature:
            signature = self.pool.get('res.users').browse(cr, uid, uid, context).signature
            values['body_html'] = tools.append_content_to_html(values['body_html'], signature)

        if values['body_html']:
            values['body'] = tools.html_sanitize(values['body_html'])

        values.update(mail_server_id=template.mail_server_id.id or False,
                      auto_delete=template.auto_delete,
                      model=template.model,
                      res_id=res_id or False)

        attachments = []
        
        if template.report_template:
            ctx = context.copy()
            report_name = self.render_template(cr, uid, template.report_name, template.model, res_id, context=ctx)
            report = report_xml_pool.browse(cr, uid, template.report_template.id, context)
            report_service = report.report_name
            
            if report.report_type in ['qweb-html', 'qweb-pdf']:
                result, format = self.pool['report'].get_pdf(cr, uid, [res_id], report_service, context=ctx), 'pdf'
            else:
                result, format = openerp.report.render_report(cr, uid, [res_id], report_service, {'model': template.model}, ctx)
    
            # TODO in trunk, change return format to binary to match message_post expected format
            result = base64.b64encode(result)
            if not report_name:
                report_name = 'report.' + report_service
            ext = "." + format
 
            if not report_name.endswith(ext):
                report_name += ext
            attachments.append((report_name, result))

        attachment_ids = []
        # Add template attachments
        for attach in template.attachment_ids:
            attachment_ids.append(attach.id)

        values['attachments'] = attachments
        values['attachment_ids'] = attachment_ids
        return values
email_template()

