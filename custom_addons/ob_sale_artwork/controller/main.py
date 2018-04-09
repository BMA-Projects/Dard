# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import http, pooler
from openerp.http import request
import base64
import openerp
from psycopg2._psycopg import OperationalError
from openerp.addons.web.controllers.main import ensure_db

class ArtworkVerification(http.Controller):
    @http.route('/ArtworkVerification', type='http', auth="none")
    def artwork_verification(self, s_action=None, **kw):
        msg = " "
        vals = request.params.copy()
        uid = openerp.SUPERUSER_ID
        context = {}
        kwargs = {}
        verified = False
        if vals.get('message',False):
            return request.render('ob_sale_artwork.veri_done',vals)
        uid = openerp.SUPERUSER_ID
        res_id = vals.get("res_id")
        data_key = vals.get("data_key")
        dbname = vals.get("db")
        virtual_state = vals.get("virtual_state")
        try:
            registry = openerp.modules.registry.Registry(dbname)
            request.session.db = dbname
        except OperationalError,e:
            r_data = {
                'massage1': e.message,
                'massage2': "Please contact Administrator with this json data.",
                'massage3': str(vals)
            }
            return request.render('ob_sale_artwork.veri_done',r_data)
        with registry.cursor() as cr:
            try:
                pool = openerp.modules.registry.RegistryManager.get(dbname)
                sale_order_line_img_obj = pool.get('sale.order.line.images')
                cr = registry.cursor()
                with registry.cursor() as cr:
                    if type(res_id) != type(1):
                        res_id = int(res_id)
                    cr.execute("""SELECT sent_for_verification 
                                  FROM sale_order_line_images 
                                  WHERE id = %s""", (res_id,))
                    rows = cr.fetchall()
                    update = False
                    for row in rows:
                        if row[0]:
                            update = True
                            break
                    if update:
                        vals['msg'] = 'You have successfully verified the virtual.'
                    else:
                        state = sale_order_line_img_obj.browse(cr, uid, res_id).state
                        state_dict = {'sent_for_approval' : 'Sent for Approval', 'confirmed' : 'Approved', 'semi_confirmed' : 'Approved with Changes','cancel':'Cancel'}
                        msg = "You have already verified this virtual with '" + state_dict.get(state, '') + "'."
                        return request.render('ob_sale_artwork.veri_done',{'message':msg})
#                 sale_order_line_img_obj = pool.get('sale.order.line.images')
#                 
#                 rec_id = sale_order_line_img_obj.search(cr, uid,  [['id','=',int(res_id)],['data_key','=',data_key]])
#                 
#                 if not rec_id or virtual_state not in ['confirmed','semi_confirmed','cancel']:
#                     return request.render('ob_sale_artwork.veri_done',{'massage':'Unable to verify the artwork. Some wrong thing happen with URL, Please contact your Administrator.'})
#                 
#                 record = sale_order_line_img_obj.browse(cr, uid, rec_id)[0]
            except:
                return request.render('ob_sale_artwork.veri_done',{'message':'You have already verified this virtual.'})
#         if verified:
#             return request.render('ob_sale_artwork.veri_done',{'message':'You have already verified this virtual.'})
        return request.render('ob_sale_artwork.verification',vals)

    @http.route('/Artapprove/submit', type='json', auth="none")
    def Artapprove_submit(self, data):
        uid = openerp.SUPERUSER_ID
        res_id = data.get("res_id")
        dbname = data.get("db")
        virtual_state = data.get("virtual_state")
        cmnt  = data.get("cmnt")
        uname  = data.get("uname")
        attach = data.get("attach") or False
        name = data.get("name")
        kwargs = {}
        context = {}
        status = False
        registry = openerp.modules.registry.Registry(dbname)
        request.session.db = dbname
        with registry.cursor() as cr:
                pool = openerp.modules.registry.RegistryManager.get(dbname)
                sale_order_line_img_obj = pool.get('sale.order.line.images')
                rec_id = sale_order_line_img_obj.search(cr, uid,  [['id','=',int(res_id)]])
                record = sale_order_line_img_obj.browse(cr, uid, rec_id)[0]
                is_verify = record.state
                state_dict = ['confirmed', 'semi_confirmed','cancel']
                if is_verify not in state_dict:
                    ol_seq = record.order_line_id.sol_seq or ''
                    partner_id = record.order_line_id.order_id.partner_id.id
                    context.update({'partner_id': partner_id})
                    if is_verify:
                        status = True
                        kwargs['body'] = "Hello, <br/> Here is an information provided regarding virtual, <br/><br/> <b>Order Line</b> : " + ol_seq + "<br/><b>Commenter </b>: " + uname + "<br/><b>Comment </b>: " + cmnt + "<br/><br/>---<br/>Thanks & Regards"
                        kwargs['subject'] = "Response for OrderLine - %s" % ol_seq
                        if attach:
                            ir_vals = {
                                'name' : name,
                                'datas_fname': name,
                                'res_model': 'sale.order.line.images',
                                'datas': attach,
                                'res_id': int(res_id)
                            }
                            attachment_id = pool.get('ir.attachment').create(cr, uid, ir_vals)
                            kwargs['attachment_ids'] = [attachment_id]
                        #request.registry['sale.order.line.images'].message_post(cr, uid, int(rec_id[0]), type="email", subtype='mt_comment', context=context, **kwargs)
                        sale_order_line_img_obj.write(cr,uid, rec_id,{'state':virtual_state,'sent_for_verification': False}, context)
                        return status
                return status
        return True
        
    @http.route('/Verification/submit', type='json', auth="none")
    def artwork_verification123(self, data):
        uid = openerp.SUPERUSER_ID
        res_id = data.get("res_id")
        data_key = data.get("data_key")
        dbname = data.get("db")
        virtual_state = data.get("virtual_state")
        cmnt  = data.get("cmnt")
        uname  = data.get("uname")
        attach = data.get("attach")
        kwargs = {}
        context = {}
        status = False
        registry = openerp.modules.registry.Registry(dbname)
        request.session.db = dbname
        with registry.cursor() as cr:
            pool = openerp.modules.registry.RegistryManager.get(dbname)
            sale_order_line_img_obj = pool.get('sale.order.line.images')
            rec_id = sale_order_line_img_obj.search(cr, uid,  [['id','=',int(res_id)],['data_key','=',data_key]])
            record = sale_order_line_img_obj.browse(cr, uid, rec_id)[0]
            is_verify = record.sent_for_verification
            ol_seq = record.order_line_id.sol_seq or ''
            partner_id = record.order_line_id.order_id.partner_id.id
            context.update({'partner_id': partner_id})
            if is_verify:
                status = True
                kwargs['body'] = "Hello, <br/> Here is an information provided regarding virtual, <br/><br/> <b>Order Line</b> : " + ol_seq + "<br/><b>Commenter </b>: " + uname + "<br/><b>Comment </b>: " + cmnt + "<br/><br/>---<br/>Thanks & Regards"
                kwargs['subject'] = "Response for OrderLine - %s" % ol_seq
                if data.get('attach'):
                    encode_data = data.get('attach')
                    ir_vals = {
                        'name' : data.get('name'),
                        'datas_fname': data.get('name'),
                        'res_model': 'sale.order.line.images',
                        'datas': encode_data,
                        'res_id': int(res_id)
                    }
                    attachment_id = pool.get('ir.attachment').create(cr, uid, ir_vals)
                    kwargs['attachment_ids'] = [attachment_id]
                #request.registry['sale.order.line.images'].message_post(cr, uid, int(rec_id[0]), type="email", subtype='mt_comment', context=context, **kwargs)
                sale_order_line_img_obj.write(cr,uid, rec_id,{'state':virtual_state,'sent_for_verification': False}, context)
                return status
            return status
    
    @http.route('/Verification/submitresponse', type='http', auth="none")
    def display_message(self, s_action=None, **kw):
         return request.render('ob_sale_artwork.veri_done',{'message':'You have successfully verified the virtual.'})
     
