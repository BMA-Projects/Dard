# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp.osv import fields, osv, orm
from datetime import datetime

class res_traceback(osv.osv):
    _name = "res.traceback"
    _description = "Res Traceback"

    _columns = {
        'code': fields.integer('Code'),
        'message': fields.char('Message'),
        'date': fields.date('Date'),
        'model': fields.char('Model')
    }
    
    _defaults={
        'date': lambda *a:datetime.now().strftime('%Y-%m-%d')
    }
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        traceback_id = False
        to_send = []
        mail_mail_obj = self.pool.get('mail.mail')
        traceback_notifiers_obj = self.pool.get('res.traceback.notifiers')
        traceback_id = self.search(cr, uid, ['&','&',('message','ilike', vals.get('message')),('code','=', vals.get('code')), ('date', '=', datetime.now().strftime('%Y-%m-%d')), ('model', '=', vals.get('model'))])
        
        body_email = "<b>Code</b> : " + str(vals.get('code')) + \
                     "<br/><br/> <b>IP</b> : " + str(vals.get('client_ip')) + \
                     "<br/><br/> <b>URL</b> : " + str(vals.get('location')) + \
                     "<br/><br/> <b>User</b> : " + str(self.pool.get('res.users').browse(cr, uid, uid, context=context).name)
        trace_type = vals.get('trace_type') if vals.get('trace_type') else 'error' 
        #if trace_type == 'error':
        body_email += "<br/><br/>  <b>Message</b> : " + str(vals.get('message')) + \
                     "<br/><br/> <b>Source of Error</b> : " + str(vals.get('error_msg')) +"<br/><br/>" + str(vals.get('debug'))
        if vals.get('code') == 200 and vals.get('model'):
            body_email += "<br/><br/><b>Model name</b> : " + str(vals.get('model'))
#         if not traceback_id:
        new_traceback_id = super(res_traceback, self).create(cr, uid, vals, context=context)
        
        if new_traceback_id:
            notifiers_ids = traceback_notifiers_obj.search(cr, uid, [('is_active', '=', 1)], context=context)
            for email in traceback_notifiers_obj.browse(cr, uid, notifiers_ids, context=context):
                to_send.append(email.email)
            to_send_str = ','.join(str(e) for e in to_send)
            user_name = str(self.pool.get('res.users').browse(cr, uid, uid, context=context).name)
            email_vals = {
                'email_to': to_send_str,
                'subject':  trace_type.capitalize() + " in OfficeBrainBMA",
                'body_html': "<p>Hello Team,<br/><br/>" + body_email + "</p><br/>----<br/>Thanks,<br/>"+ user_name +"."
            }
            mail_id = mail_mail_obj.create(cr, uid, email_vals, context=context)
            status = mail_mail_obj.send(cr, uid, [mail_id], context=context)
            if status:
                print "Mail sent successfully"
        return new_traceback_id
        #return False
        
class res_traceback_notifier(osv.osv):
    _name = "res.traceback.notifiers"
    _description = "Res Traceback Notifiers"
    
    _columns = {
        'name': fields.char('Name', size=128, help="Name of email receiver."),
        'email': fields.char('Email', size=128, help="These people will receive email.", required=True),
        'is_active': fields.boolean('Active', help="If It is set to False, he/she will not be notified about traceback emails.")
     }
    
    _defaults = {
        'is_active': True
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
