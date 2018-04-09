# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api, _

class ResUser(models.Model):
    
    _inherit = "res.users"
    
    reply_to = fields.Char('Reply-To', help='Reply email address. Setting the reply_to bypasses the automatic thread creation.')

class MailMessage(models.Model):
    
    _inherit = "mail.message"
        
    reply_to = fields.Char('Reply-To', help='Reply email address. Setting the reply_to bypasses the automatic thread creation.',default = lambda self: self.env.user.reply_to or '')
    
    @api.model
    def create(self, values):
        if 'reply_to' not in values:
            reply_to_email = self.env.user.reply_to or False
            if reply_to_email:
                values['reply_to'] = reply_to_email
        return super(MailMessage, self).create(values)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 