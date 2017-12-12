# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Solaris, Inc. (<http://www.solarismed.com>)
#    Copyright (C) 2004-2013 OpenERP SA (<http://www.openerp.com>)
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

from openerp.osv import osv, fields
from lxml import etree
import string
from openerp import netsvc
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    _columns = {
        'transId': fields.char('Transaction ID', size=128, readonly=True, help="The transaction ID returned by Authorize.net.  Used for voiding a transaction."),
        'is_approved': fields.boolean('Approved', readonly=True),
        'state': fields.selection(
        [('draft','Draft'),
        ('dispute','Error'),
        ('cancel','Cancelled'),
        ('proforma','Pro-forma'),
        ('posted','Posted'),
        ], 'Status', readonly=True, size=32, track_visibility='onchange',),
        'cim_id': fields.many2one('account.authnet.cim', 'Customer Profile', domain="[('partner_id','=',partner_id)]"),
        'cim_payment_id': fields.many2one('account.authnet.cim.payprofile', 'Card on File', domain="[('cim_id','=',cim_id)]"),
        'transaction_ids': fields.one2many('credit.card.transaction','payment_id', string='CC Transaction', readonly=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice ref'),
        }


    def default_get(self, cr, uid, fields, context=None):
        if not context: context = {}
        res = super(account_voucher,self).default_get(cr, uid, fields, context)
        if context.get('active_ids'):
            res.update({'invoice_id': context.get('active_ids')[0]})
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        """
                Add domain on journal_id field and remove 'widget = selection' on the same
                field because the dynamic domain is not allowed on such widget
        """
        if not context: context = {}
        res = super(account_voucher, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            old_domain = ''
            nodes = doc.xpath("//field[@name='journal_id']")
            if (context.get('invoice_type','') not in ('out_invoice')) or (context.get('type', '') in ('payment')):
                for node in nodes:
                    if node.get('domain'):
                        #Improve code for domain
                         old_domain = node.get('domain')
                         old_domain = old_domain[:old_domain.rfind("]")] + ","
                         new_domain = "('type','in',['bank', 'cash']),'|',('cc_processing','=',False),('cc_refunds','=',False)]"
                    else:
                            new_domain = "[('type','in',['bank', 'cash']),'|',('cc_processing','=',False),('cc_refunds','=',False)]"
                    node.set('domain', old_domain+new_domain)
                    node.set('widget', '')
            else:
                for node in nodes:
                    if node.get('domain'):
                        #Improve code for domain
                        old_domain = node.get('domain')
                        old_domain = old_domain[:old_domain.rfind("]")] + ","
                        new_domain = "('type','in',['bank', 'cash'])]"
                    else:
                        new_domain = "[('type','in',['bank', 'cash'])]"
                    node.set('domain', old_domain+new_domain)
                    node.set('widget', '')
            res['arch'] = etree.tostring(doc)
        return res  

    def get_cc_profile(self, cr, uid, partner_id, context=None):
        partner_rec = self.pool['res.partner'].browse(cr, uid, partner_id, context)
        value = {}
        if partner_rec.cim_id:
            value['cim_id'] = partner_rec.cim_id.id
            # Grab the default payment profile
            if partner_rec.cim_id.default_payprofile_id:
                value['cim_payment_id'] = partner_rec.cim_id.default_payprofile_id.id
                value['new_card'] = False
            # If no default, grab the first profile we find
            elif partner_rec.cim_id.payprofile_ids:
                value['cim_payment_id'] = partner_rec.cim_id.payprofile_ids[0].id
                value['new_card'] = False
            else:
                value['new_card'] = True
        else:
            value['new_card'] = True
        return value

    # If partner is changed, the customer and payment profile is reloaded.
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
        res = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)
        journal_rec = journal_id and self.pool['account.journal'].browse(cr, uid, journal_id) or False
        if journal_rec and journal_rec.cc_processing and partner_id:
            res['value'].update(self.get_cc_profile(cr, uid, partner_id, context=context))
        # If it's not using CC payments, erase any previously filled CIM data
        else:
            if res.get('value', False):
                res['value']['cim_id'] = False
                res['value']['cim_payment_id'] = False
                res['value']['new_card'] = False
        return res
    
    # Set the CC flag to hide/unhide stuff
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
        if not journal_id:
            return False
        res = super(account_voucher, self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context)
        
        # Make sure we only show CIM options if we're really paying with a CC
        if res['value'].get('use_cc', False) and partner_id:
            res['value'].update(self.get_cc_profile(cr, uid, partner_id, context=context))
        
        # If it's not using CC payments, erase any previously filled CIM data
        elif not res['value'].get('use_cc', True):
            res['value']['cim_id'] = False
            res['value']['cim_payment_id'] = False
        return res
    
    
    # Prepare an XML request to send validating the transaction
    def _prepare_transaction_request(self, cr, uid, ids, voucher_rec, context=None):
        ctx = dict(context)
        ctx['unmask'] = True
        ref_orders = ''
        ref_credit_memos = ''
        cust_info = {}
        cc_read_fields = ['cc_number', 'cc_cvv', 'cc_exp_month', 'cc_exp_year']
        
        ref_orders = str(voucher_rec.invoice_id.number)
        for dr_line in voucher_rec.line_dr_ids:
            if ref_credit_memos:
                ref_credit_memos += ',' + dr_line.move_line_id.move_id.ref
            else:
                ref_credit_memos = dr_line.move_line_id.move_id.ref
        
        
        # ------------------------
        # Begin the XML generation
        # ------------------------
        # Format will vary based on if it's a card on file or one-time use local card
        authnet_obj = self.pool['account.authnet']
        # Card on file
        if voucher_rec.cim_payment_id:
            refId = voucher_rec.id
            # authnet_obj = self.pool['account.authnet']
            root = authnet_obj._get_xml_header(cr, uid, 'createCustomerProfileTransactionRequest', refId, context)
            
            # order_ref = etree.SubElement(transaction_req, 'order')
            # Transaction type and amount
            transaction = etree.SubElement(root, 'transaction')

            if context.get('trans_refund'):
                auth_capture = etree.SubElement(transaction, 'profileTransRefund')
                etree.SubElement(auth_capture, 'amount').text = str(abs(context.get('refund_amount')))
            else:
                auth_capture = etree.SubElement(transaction, 'profileTransAuthCapture')
                etree.SubElement(auth_capture, 'amount').text = str(voucher_rec.amount)
            etree.SubElement(auth_capture, 'customerProfileId').text = voucher_rec.cim_id.profile_id
            etree.SubElement(auth_capture, 'customerPaymentProfileId').text = voucher_rec.cim_payment_id.payprofile_id
            order = etree.SubElement(auth_capture, 'order')
            etree.SubElement(order, 'invoiceNumber').text = ref_orders
            if voucher_rec.cc_cvv:
                etree.SubElement(auth_capture, 'cardCode').text = voucher_rec.cc_cvv
            if context.get('trans_refund'):
                etree.SubElement(auth_capture, 'transId').text = context.get('trans_refund').trans_id

            
        # One-time use card
        else:
            # Need to gather additional data about the payment first
            # If the invoice address isn't filled in or is missing data, get the company instead
            cust_info['id'] = voucher_rec.invoice_addr_id.id or voucher_rec.partner_id.id
            cust_info['email'] = voucher_rec.invoice_addr_id.email or voucher_rec.partner_id.email or ''
            
            namepart = voucher_rec.invoice_addr_id.name.rpartition(' ')
            cust_info['firstName'] = namepart[0]
            cust_info['lastName'] = namepart[2]
            cust_info['company'] = voucher_rec.partner_id.name
            cust_info['address'] = voucher_rec.invoice_addr_id.street or voucher_rec.partner_id.street or ''
            cust_info['city'] = voucher_rec.invoice_addr_id.city or voucher_rec.partner_id.city or ''
            cust_info['state'] = voucher_rec.invoice_addr_id.state_id.code or voucher_rec.partner_id.state_id.code or ''
            cust_info['zip'] = voucher_rec.invoice_addr_id.zip or voucher_rec.partner_id.zip or ''
            cust_info['country'] = voucher_rec.invoice_addr_id.country_id.name or voucher_rec.partner_id.country_id.name or ''
            
            full_str = string.maketrans('','')
            nodigs = full_str.translate(full_str, string.digits)
            phone_num = voucher_rec.invoice_addr_id.phone or voucher_rec.partner_id.phone or ''
            if phone_num:
                cust_info['phoneNumber'] = str(phone_num).translate(full_str, nodigs)
            fax_num = voucher_rec.invoice_addr_id.fax or voucher_rec.partner_id.fax or ''
            if fax_num:
                cust_info['faxNumber'] = str(fax_num).translate(full_str, nodigs)
            
            
            # Start generating the XML
            refId = voucher_rec.id
            root = self.pool['account.authnet']._get_xml_header(cr, uid, 'createTransactionRequest', refId, context)
            
            # Transaction type and amount
            transaction_req = etree.SubElement(root, 'transactionRequest')
            etree.SubElement(transaction_req, 'transactionType').text = 'authCaptureTransaction'
            etree.SubElement(transaction_req, 'amount').text = str(voucher_rec.amount)
            
            # Payment info
            # Prep info dictionary for the XML tree
            cc_info = self.read(cr, uid, [voucher_rec.id], cc_read_fields, ctx)[0]
            
            pay_type = etree.SubElement(transaction_req, 'payment')
            cc = etree.SubElement(pay_type, 'creditCard')
            etree.SubElement(cc, 'cardNumber').text = voucher_rec.cc_number
            etree.SubElement(cc, 'expirationDate').text = voucher_rec.cc_exp_month + '/' + voucher_rec.cc_exp_year
            if voucher_rec.cc_cvv:
                etree.SubElement(cc, 'cardCode').text = voucher_rec.cc_cvv
            del cc_info
            
            # Reference info
            order_ref = etree.SubElement(transaction_req, 'order')
            etree.SubElement(order_ref, 'invoiceNumber').text = ref_orders
            if ref_credit_memos:
                etree.SubElement(order_ref, 'description').text = 'Credit memo(s) applied from: ' + ref_credit_memos
            
            # Customer record, using partner ID as custom id (contact/partner IDs don't overlap anymore in 7.0!)
            cust = etree.SubElement(transaction_req, 'customer')
            etree.SubElement(cust, 'id').text = str(cust_info['id'])
            if cust_info['email']: etree.SubElement(cust, 'email').text = cust_info['email']
            
            # Bill To info
            billto = etree.SubElement(transaction_req, 'billTo')
            etree.SubElement(billto, 'firstName').text = cust_info['firstName']
            if cust_info['lastName']: etree.SubElement(billto, 'lastName').text = cust_info['lastName']
            etree.SubElement(billto, 'company').text = cust_info['company']
            if cust_info['address']: etree.SubElement(billto, 'address').text = cust_info['address']
            if cust_info['city']: etree.SubElement(billto, 'city').text = cust_info['city']
            if cust_info['state']: etree.SubElement(billto, 'state').text = cust_info['state']
            etree.SubElement(billto, 'zip').text = cust_info['zip']
            if cust_info['country']: etree.SubElement(billto, 'country').text = cust_info['country']
            if cust_info.get('phoneNumber', False): etree.SubElement(billto, 'phoneNumber').text = cust_info['phoneNumber']
            if cust_info.get('faxNumber', False): etree.SubElement(billto, 'faxNumber').text = cust_info['faxNumber']
            
            # Define as ecommerce transaction (card not present)
            retail = etree.SubElement(transaction_req, 'retail')
            etree.SubElement(retail, 'marketType').text = '0'
        auth_ids = authnet_obj.search(cr, uid, [('active','=',True)], limit=1, context=context) 
        auth_rec = authnet_obj.browse(cr, uid, auth_ids[0],context)
        
        if auth_rec:
            if auth_rec[0].create_profile:
                extraOptions = "x_currency_code=USD"
                etree.SubElement(root, 'extraOptions').text = etree.CDATA(extraOptions)
                return root
            else:
                return root
    
    # Override the original proforma_voucher method and insert Authorize.net validation code
    def proforma_voucher_cc(self, cr, uid, ids, context=None):
        ctx = dict(context)
        ctx['unmask'] = True

        if context is None: context = {}
        credit_transaction_obj = self.pool.get('credit.card.transaction')
        trans_vals = {}
        valid_ids = []
        voucher_vals = {}

        try:
            for record in self.browse(cr, uid, ids):
                # Make sure there's an amount, $0 payments are worthless!
                if not record.amount:
                    raise osv.except_osv("Error", "Paid Amount is $0, please enter a payment amount.")
                
                if record.new_card:
                    if not (record.cc_number and record.cc_exp_month and record.cc_exp_year):
                        raise osv.except_osv(_('Warning'), _('Provide credit card details for Transaction'))
                if record.use_cc:
                    if not record.cim_payment_id and not record.new_card:
                        raise osv.except_osv(_('Warning'),_('Select or create a Payment profile'))
                    # When 'Always create profile' boolean field is selected at API credential configuration, the customer profile and payment profile is created before sending info to authorize.net
                    cim_config_object = self.pool.get('account.authnet')
                    auth_ids = cim_config_object.search(cr, uid, [('active','=',True)], limit=1, context=context) 
                    if auth_ids:
                        if not record.cim_id:
                            self.create_customer_profile(cr, uid, ids, context)
                        if record.new_card:
                            if record.cc_number and len(record.cc_number) > 4:
                                context.update({'last_four_digit_cc': record.cc_number[-4:]})
                            self.create_payment_profile(cr, uid, ids, context=context)

            for voucher_rec in self.browse(cr, uid, ids):
                valid_ids.append(voucher_rec.id)
                # If this is a CC payment, authenticate with Authorize.net
                if voucher_rec.use_cc:
                    # Prepare documents required for transaction processing

                    self.write(cr, uid, [voucher_rec.id], {'last_four': voucher_rec.cim_payment_id.last_four}, context)

                    # Transaction object record is created here
                    invoice_id = context.get('record_id')
                    cr.execute("select order_id from sale_order_invoice_rel where invoice_id=%s", (invoice_id, ))
                    sale_list = map(lambda x: x[0], cr.fetchall())
                    sale_id=False
                    if sale_list:
                        sale_id = sale_list[0] 
                    trans_vals = {
                        'cim_id': voucher_rec.cim_id.id,
                        'pim_id': voucher_rec.cim_payment_id.id,
                        'amount': voucher_rec.amount,
                        'invoice_id': invoice_id,
                        'sale_id': sale_id,
                        'payment_id': voucher_rec.id
                    }
                    
                    created_id = credit_transaction_obj.create(cr, uid, trans_vals, context=context)
                    # Prepare the XML request
                    req_xml_obj = self._prepare_transaction_request(cr, uid, ids, voucher_rec, context)
                    
                    # Send the XML object to Authorize.net and return an XML object of the response
                    authnet_obj = self.pool['account.authnet']
                    ctx= context
                    ctx['from_transaction'] = voucher_rec.id
                    res = authnet_obj._send_request(cr, uid, req_xml_obj, ctx)

                    if not res.xpath('//transactionResponse') and not res.xpath('//directResponse'):
                        errorcode = res.xpath('//messages/message/code')[-1].text 
                        errordesc = res.xpath('//messages/message/text')[-1].text
                        errormsg = "Code - "+errorcode+"\n"+errordesc
                        raise osv.except_osv('There seems to be an error !', errormsg)
                    
                    # Parsing will vary depending on if it's a card on file or one-time card
                    if voucher_rec.cim_payment_id:
                        res_dict = authnet_obj._parse_payment_gateway_response(cr, uid, res, 'directResponse', context=context)
                        approval_code = res_dict['Response Code']
                        transId = res_dict['Transaction ID']
                        errordesc = res_dict['Response Reason Text']
                        errorid = res_dict['Response Reason Code']
                        card_type = res_dict['Card Type']
                        authCode = res_dict['Authorization Code']
                        avsResultCode = res_dict['AVS Response']
                        cvvResultCode = res_dict['Card Code Response']
                    else:
                        # Get the transaction approval code
                        approval_code = res.xpath('//responseCode')[0].text
                        transId_loc = res.xpath('//transId')
                        transId = transId_loc and transId_loc[0].text or False
                        errorcode_loc = res.xpath('//errorcode')
                        errorid = errorcode_loc and errorcode_loc[0].text or False
                        error_loc = res.xpath('//errorText')
                        errordesc = error_loc and error_loc[0].text or False
                        card_type_loc = res.xpath('//accountType')
                        card_type = card_type_loc and card_type_loc[0].text or False
                        auth_code_loc = res.xpath('//authCode')
                        authCode = auth_code_loc and auth_code_loc[0].text or False
                        avs_response_loc = res.xpath('//avsResponse')
                        if not avs_response_loc:
                            avs_response_loc = res.xpath('//avsResultCode')
                        avsResultCode = avs_response_loc and avs_response_loc[0].text or False
                        card_code_loc = res.xpath('//cardCode')
                        if not card_code_loc:
                            card_code_loc = res.xpath('//cvvResultCode')
                        cvvResultCode = card_code_loc and card_code_loc[0].text or False

                    
                    CARD_CODE_RESPONSE = {
                        'M': 'Match',
                        'N': 'No Match',
                        'P': 'Not Processed',
                        'S': 'Should have been present',
                        'U': 'Issuer unable to process request',
                        }
                    AVS_RESPONSE = {
                        'A':'Address (Street) matches, ZIP does not', 
                        'B':'Address information not provided for AVS check',
                        'E':'AVS error',
                        'G':'Non-U.S. Card Issuing Bank',
                        'N':'No Match on Address (Street) or ZIP',
                        'P':'AVS not applicable for this transaction',
                        'R':'Retry – System unavailable or timed out',
                        'S':'Service not supported by issuer',
                        'U':'Address information is unavailable',
                        'W':'Nine digit ZIP matches, Address (Street) does not',
                        'X':'Address (Street) and nine digit ZIP match',
                        'Y':'Address (Street) and five digit ZIP match',
                        'Z':'Five digit ZIP matches, Address (Street) does not',
                        }    
                    if cvvResultCode in ['M','N','P','S','U']:
                        cvvResultCode = CARD_CODE_RESPONSE[cvvResultCode]
                    if avsResultCode in ['A','B','E','G','N','P','R','S','U','W','X','Y','Z']:
                        avsResultCode = AVS_RESPONSE[avsResultCode]
                    trans_update = {'trans_id': transId, 'message': errordesc, 'card_type': card_type, 'authCode': authCode, 'avsResultCode': avsResultCode, 'cvvResultCode': cvvResultCode}
                    trans_vals.update(trans_update)
                    
                    # If the record had one-time-use CC data, we can clear it now.  It should have
                    # already validated/failed from the proforma_voucher function, so we don't have
                    # to worry about deleting CC data prematurely.
                    # Used a CC and there is a cc_number (wasn't in some way on file)
                    if voucher_rec.use_cc:
                        voucher_vals = {
                            'cc_number': False,
                            'cc_cvv': False,
                            'cc_exp_month': False,
                            'cc_exp_year': False,
                        }
                    if approval_code == '1' :

                        voucher_vals['is_approved'] = True
                        self.action_move_line_create(cr, uid, valid_ids, context=context)
                        voucher_vals['transId'] = transId
                        self.write(cr, uid, [voucher_rec.id], voucher_vals, context)
                        credit_transaction_obj.write(cr, uid, [created_id], trans_update, context)
                        cr.commit()
                    else:
                        cr.rollback()
    #                     new_error_transaction = self.pool.get('credit.card.transaction').create(cr, uid, trans_vals, context=context)
                        voucher_vals['is_approved'] = False 
                        voucher_vals['last_four'] = ''
                        self.write(cr, uid, [voucher_rec.id], voucher_vals, context)
                       
                        message_to_display = 'Error code - '+errorid+"\n"+errordesc
                        if approval_code == '2':
                            message_header = 'Credit card was declined '
                        elif approval_code == '3':
                            message_header = 'There was an error '
                        else:
                            message_header = 'The transaction was held for review '
                        raise osv.except_osv(message_header, message_to_display)
                else:
                    res = super(account_voucher, self).proforma_voucher(cr, uid, ids, context=context)
        except ValueError:
            cr.rollback()
            pass
            # To remove the credit card info if any error arises
        voucher_vals = {
                        'cc_number': False,
                        'cc_cvv': False,
                        'cc_exp_month': False,
                        'cc_exp_year': False,
        }
        self.write(cr, uid, ids, voucher_vals, context=context)
        #cr.commit()
        return True
    
    def create_customer_profile(self, cr, uid, ids, context=None):
        if context is None: context = {}
        recs = self.browse(cr, uid, ids)
        cust_profile = self.pool.get('cim.create.customer.profile')
        for record in recs:
            new_cim_id = cust_profile.create(cr, uid, {'name': record.partner_id.name, 'partner_id': record.partner_id.id, 'invoice_addr_id': record.invoice_addr_id.id})
            cim_id = cust_profile.send_request(cr, uid, new_cim_id, context=context)
            if cim_id:
                self.write(cr, uid, ids, {'cim_id':cim_id}, context=context)
                cr.commit()
        return True
    
    def create_payment_profile(self, cr, uid, ids, context=None):
        if context is None: context = {}
        recs = self.browse(cr, uid, ids)
        
        vals = {}
        pay_profile = self.pool.get('cim.create.payment.profile')
        for record in recs:    
            vals['name']= record.partner_id.name
            vals['partner_id']= record.partner_id.id
            vals['alt_invoice_addr_id']= record.invoice_addr_id.id
            vals['cc_number']= record.cc_number
    #        vals['cc_cvv']= fields.char('CVV', size=512)
            vals['cc_exp_month']= record.cc_exp_month
            vals['cc_exp_year']= record.cc_exp_year
            vals['bill_firstname']= record.bill_firstname
            vals['bill_lastname']= record.bill_lastname
            vals['bill_street']= record.bill_street
            vals['city_state_zip']= record.city_state_zip
            vals['cim_id']= record.partner_id.cim_id.id
            new_profile_id = pay_profile.create(cr, uid, vals)
            profile_id = pay_profile.send_request(cr, uid, new_profile_id, context=context)
            if profile_id:
                self.write(cr, uid, ids, {'cim_payment_id':profile_id, 'new_card': False}, context=context)
                cr.commit()
        return True
    
    
    def do_refund(self, cr, uid, ids, context=None):
        if not context: context = {}
        transaction_obj = self.pool.get('credit.card.transaction')
        authnet_obj = self.pool.get('account.authnet')
        invoice_obj = self.pool.get('account.invoice')
        invoice_rec = invoice_obj.browse(cr, uid, context.get('active_id'), context)
        if invoice_rec.partner_id.cim_id:
            if not invoice_rec.refund_invoice_id:
                raise osv.except_osv("Error", "No Authorize.net Transaction found for Customer refund",)
        transaction_ids = transaction_obj.search(cr, uid, [('invoice_id','=',invoice_rec.refund_invoice_id.id)])
        res = None
        for transaction_rec in transaction_obj.browse(cr, uid, transaction_ids, context=context):
            if invoice_rec.partner_id.cim_id:
                if not transaction_rec.trans_id:
                    raise osv.except_osv("Error", "No Authorize.net Transaction found for Customer refund",)
            for rec in self.browse(cr, uid, ids, context):
                context.update({'trans_refund':transaction_rec, 'refund_amount': rec.amount})
#                 refund_request = self._prepare_transaction_request(cr, uid, ids, transaction_rec.payment_id, context= context)
                context['from_transaction'] = transaction_rec.payment_id.id
#                 res = authnet_obj._send_request(cr, uid, refund_request, context)
        return True
                        
    # Override payment function for direct payment from the invoice popup window
    def button_proforma_voucher(self, cr, uid, ids, context=None):
        context = context or {}
        if context.get('invoice_type') == 'out_refund':
            refund_vals = self.do_refund(cr, uid, ids, context=context)
        mod_obj = self.pool.get('ir.model.data')
        curr_object = self.browse(cr, uid, ids, context=context)
        #---Start code for advance payment--
        record = self.browse(cr, uid, ids, context=context)[0]

        # Just call the default proforma_voucher function above, will handle non-CC payments too, have to use the workflow...
        if record.cim_payment_id or record.new_card:
            self.proforma_voucher_cc(cr, uid, ids, context)
        else:
            super(account_voucher, self).button_proforma_voucher(cr, uid, ids, context=context)
        #if we don't use the workflow we need to call send auto email manually.
        self.action_send_confirm(cr, uid, context=context)
        res = mod_obj.get_object_reference(cr, uid, 'sod_account_payment_cc_authorizenet', 'view_account_voucher_pay')
        res_id = res and res[1] or False
        ref_obj_id = []

        message_obj = self.pool.get('account.voucher.pay')
        for record in curr_object:
            if record.use_cc:
                ref_obj_id = message_obj.search(cr, uid, [('name','=','The transaction was successful')], context=context)
            else:
                ref_obj_id = message_obj.search(cr, uid, [('name','=','The payment was processed')], context=context)
        
        return{
        'name':_('Successful!'),
        'view_type': 'form',
        'view_mode': 'form',
        'view_id': [res_id],
        'res_model': 'account.voucher.pay',
        'type': 'ir.actions.act_window',
        'target': 'new',
        'context': "{'record_id': %d,'from_sales': %d}" % (context.get('record_id'),context.get('from_sales') or False),
        'res_id': ref_obj_id[0],
        }
    
    def cancel_voucher(self, cr, uid, ids, context=None):
        voucher_rec = self.browse(cr, uid, ids, context=context)[0]
        if voucher_rec.use_cc and voucher_rec.cc_number:
            voucher_vals = {
                'cc_number': False,
                'cc_cvv': False,
                'cc_exp_month': False,
                'cc_exp_year': False,
            }
            self.write(cr, uid, ids, voucher_vals, context=context)
        res = super(account_voucher, self).cancel_voucher(cr, uid, ids, context=context)
        return res
    
    def _prepare_void_request(self, cr, uid, ids, voucher_rec, context=None):
        # Start root tag and add credentials
        refId = voucher_rec.id
        root = self.pool['account.authnet']._get_xml_header(cr, uid, 'createTransactionRequest', refId, context)
        
        # Void request, adding transaction ID to void
        transaction_req = etree.SubElement(root, 'transactionRequest')
        etree.SubElement(transaction_req, 'transactionType').text = 'voidTransaction'
        etree.SubElement(transaction_req, 'refTransId').text = voucher_rec.transId
        
        return root
        
    
    # Void a transaction
    # TODO: Ask about CC settlement process 
    def void_voucher(self, cr, uid, ids, context=None):
        if not isinstance(ids, list):
            ids = [ids]
        vouchers = self.browse(cr, uid, ids, context)
        trans_recs = self.pool.get('credit.card.transaction')
        wf_service = netsvc.LocalService("workflow")
        
        for voucher_rec in vouchers:
            if voucher_rec.state == 'posted' and voucher_rec.is_approved:
                
                #Preparing documents before sending request to Authorize.net
                self.cancel_voucher(cr, uid, [voucher_rec.id], context)
                
                trans_ids = trans_recs.search(cr, uid, [('trans_id','=',voucher_rec.transId)])
                trans_recs.write(cr, uid, trans_ids, {'message': 'This transaction has been voided.'}, context)
                
                req_xml_obj = self._prepare_void_request(cr, uid, ids, voucher_rec, context)
                
                # Send the XML object to Authorize.net and return the XML string
                res = self.pool['account.authnet']._send_request(cr, uid, req_xml_obj, context)
                
                # Get the transaction approval code
                approval_code = res.xpath('//responseCode')[0].text
                
                if approval_code == '1':
                    vals = {
                        'is_approved': False,
                        'transId': False,
                        'last_four': False
                    }
                    self.write(cr, uid, [voucher_rec.id], vals, context)

                # If the transaction is already voided on authorize.net but not the ERP, 
                # walk through the same steps
                elif res.xpath('//transactionResponse/messages/message/code')[0].text == '310':
                    vals = {
                        'is_approved': False,
                        'transId': False,
                        'last_four': False
                    }
                    self.write(cr, uid, [voucher_rec.id], vals, context)
                    
                # TODO: If the transaction is already settled, generate a refund here
                
                # If something else went wrong, update the error text and do nothing else
                else:
                    cr.rollback()
                    errordesc = res.xpath('//errorText')
                    
                    # Auth.net may have sent an error message or a regular message 
                    if errordesc:
                        errordesc = errordesc[0].text
                    else:
                        errordesc = res.xpath('//transactionResponse/messages/message/description')[0].text
        return False

    def action_send_confirm(self, cr, uid, context=None):

        record_id=context.get('active_id')
        model=context.get('active_model')
        active_model = self.pool.get(model)
        template_obj = self.pool.get('email.template')

        if model=='account.invoice' and  active_model.browse(cr,uid,record_id,context=context).type in ('in_invoice','out_refund','in_refund'):
            return True
        if model=='account.voucher' and  active_model.browse(cr,uid,record_id,context=context).type=='payment':
            return True
        ir_model= self.pool.get('ir.model')
        mail_compose=self.pool.get('mail.compose.message')
        ir_model_id = ir_model.search(cr, uid, [('model','=',model)])
        template_id=template_obj.search(cr,uid,[('model_id','=',ir_model_id)])
                
        record = active_model.browse(cr,uid,record_id,context=context)
        partner = record.partner_id
        #make sure we need to send email for that partner and that the partner has email.
        # record_send= partner.send_email and partner.email
        record_send= partner.email
        if  record_send and template_id:
            values=mail_compose.generate_email_for_composer(cr,uid,template_id[0],record_id,context=context)
            subtype = 'mail.mt_comment'    
            is_log = context.get('mail_compose_log', False)
            if is_log:
                subtype = False
            active_model.message_post(cr, uid, [record_id], type='email', subtype=subtype, context=context,**values)
            mail_obj = self.pool.get('mail.mail')
            mail_ids = mail_obj.search(cr, uid, [('subject','=',values['subject']),('model','=',model),('res_id','=',record_id)], context=context)    
            for data in mail_obj.browse(cr,uid,mail_ids,context):
                if not data.email_to :
                    email=active_model.browse(cr,uid,record_id,context=context).partner_id.email
                    mail_obj.write(cr,uid,data.id,{'state': 'outgoing','email_to':email})                
        return True
