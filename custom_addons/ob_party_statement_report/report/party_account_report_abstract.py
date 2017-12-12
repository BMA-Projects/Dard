# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import fields, osv
from openerp.report import report_sxw


class party_account_report_template(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(party_account_report_template, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
        })
        self.context = context

class party_account_margin(osv.AbstractModel):
    _name = 'report.ob_party_statement_report.account_party_statement_report_template'
    _inherit = 'report.abstract_report'
    _template = 'ob_party_statement_report.account_party_statement_report_template'
    _wrapped_report_class = party_account_report_template

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
