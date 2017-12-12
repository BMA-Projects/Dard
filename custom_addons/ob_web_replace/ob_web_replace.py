# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import osv, fields
from openerp.osv.orm import except_orm
from openerp import tools
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import append_content_to_html
from urllib import urlencode
from urlparse import urljoin

class ir_translation(osv.osv):
    _inherit = "ir.translation"
    
    def translate_fields(self, cr, uid, model, id, field=None, context=None):
        langs_ids = self.pool.get('res.lang').search(cr, uid, [('code', '!=', 'en_US')], context=context)
        if not langs_ids:
            raise osv.except_osv(_('Error'), _("Translation features are unavailable until you install an extra officebrain translation."))
        res = super(ir_translation, self).translate_fields(cr, uid, model, id, field=field, context=context)
        return res


class mail_message(osv.osv):
    """Replace 'Odoo' with 'officebrain' in message_id """
    _inherit = 'mail.message'

    def create(self, cr, uid, values, context=None):
        if values.get('subject'):
            subject = values.get('subject').replace('Odoo', 'OfficeBrain')
            values.update({'subject': subject})
        res = super(mail_message, self).create(cr, uid, values, context=context)
        message_id = self.browse(cr, uid, res, context=context).message_id or False
        message_id = message_id and message_id.replace('odoo', 'officebrain') or False
        if message_id:
            self.write(cr, uid, res, {'message_id': message_id}, context=context)
        return res

mail_message()

class mail_mail(osv.osv):
    """Replace 'Odoo' with 'officebrain' in body """
    _inherit = 'mail.mail'

    def create(self, cr, uid, values, context=None):
        if values.get('body_html'):
            body = values.get('body_html').replace('Odoo', 'OfficeBrain')
            values.update({'body_html': body})
        return super(mail_mail, self).create(cr, uid, values, context=context)

mail_mail()

class mail_notification(osv.Model):
    _inherit = 'mail.notification'

    def get_signature_footer(self, cr, uid, user_id, res_model=None, res_id=None, context=None, user_signature=True):
        footer = super(mail_notification, self).get_signature_footer(cr, uid, user_id, res_model, res_id, context, user_signature)
        footer = ""
        if not user_id:
            return footer

        # add user signature
        user = self.pool.get("res.users").browse(cr, SUPERUSER_ID, [user_id], context=context)[0]
        if user_signature:
            if user.signature:
                signature = user.signature
            else:
                signature = "--<br />%s" % user.name
            footer = tools.append_content_to_html(footer, signature, plaintext=False)

        # add company signature
        if user.company_id.website:
            website_url = ('http://%s' % user.company_id.website) if not user.company_id.website.lower().startswith(('http:', 'https:')) \
                else user.company_id.website
            company = "<a style='color:inherit' href='%s'>%s</a>" % (website_url, user.company_id.name)
        else:
            company = user.company_id.name
        sent_by = _('Sent by %(company)s using %(odoo)s')

        signature_company = '<br /><small>%s</small>' % (sent_by % {
            'company': company,
            'odoo': "<a style='color:inherit' href='https://bma8.officebrain.com/'>OfficeBrainBMA</a>"
        })
        footer = tools.append_content_to_html(footer, signature_company, plaintext=False, container_tag='div')

        return footer

mail_notification()
