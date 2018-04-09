from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from datetime import date
import datetime
import time
class stock_picking(osv.osv):
    
    ## getting carrier total amount .......
    def _get_carrier_total(self, cr, uid, ids, fields, arg, context=None):
        res ={}
        
        for line in self.browse(cr, uid, ids):
            total = 0.0
            for o in line.response_usps_ids:
                if o.is_label_genrated:
                    total += float(o.rate)
            res[line.id] = total
        return res
    
    _inherit = 'stock.picking'
    
    _columns = {
                    'invoice_ids':fields.many2one('account.invoice','Invoice id'),
                    'carrier_rate_total':fields.function(_get_carrier_total, string="Carrier Total", type='integer', store=False),
                    'invoice_id': fields.one2many('account.invoice','picking_id','Invoices'),
                }


    ## create supplier invoice using carrier information of shipping services ..........................
    def create_supplier_invoice(self, cr, uid, ids, context=None):
        
            ## required object for creting invoice shipping service vice
            invoice_obj = self.pool.get('account.invoice')
            currency_obj = self.pool.get('res.currency')
            account_obj = self.pool.get('account.account')
            pro_obj = self.pool['product.product']
            response_obj = self.pool['shipping.response']
            
            
            account_id = None
            partner_id = None
            invoice_id = None
            inv_list = []
            taday_date = datetime.datetime.now()
            invoice_lines = []
            dup_product_list = []
            flag = False
            
            for shipp_record in self.browse(cr, uid, ids):
                if shipp_record.pack_weight_ids:
                    for pack_line in  shipp_record.pack_weight_ids:
                        if pack_line.carrier_id:
                            partner_id = pack_line.carrier_id.partner_id.id
                            response_id = response_obj.search(cr, uid,[('sequence','=',pack_line.sequence),('is_label_genrated','=',True),('picking_id','=',shipp_record.id)])
                            response_record = response_obj.browse(cr, uid, response_id)
                            for o in response_record:
                                if pack_line.carrier_id.product_id.id not in dup_product_list:
                                    product_id = pro_obj.browse(cr, uid, pack_line.carrier_id.product_id.id)
                                    acc_id = product_id.product_tmpl_id.categ_id.property_account_income_categ.id
                                    if acc_id :
                                        invoice_lines.append(( 0,0,{
                                                            'product_id':pack_line.carrier_id.product_id.id,
                                                            'quantity':'1.0',
                                                            'name':pack_line.carrier_id.product_id.name,
                                                            'account_id':acc_id,
                                                            'price_unit':o.rate,
                                                             
                                                            } ))
                                        dup_product_list.append(pack_line.carrier_id.product_id.id)
                                        flag = False
                                    else:
                                        raise osv.except_osv('Warning', 'please configure income account in product category')
                                else:
                                    flag = True
                                    for inv_record in invoice_obj.browse(cr, uid, inv_list):
                                        for inv_lines in inv_record.invoice_line:
                                            if inv_lines.product_id.id == pack_line.carrier_id.product_id.id:
                                                invoice_lines.append(( 1,inv_lines.id,{
                                                        'price_unit':float(o.rate) + inv_lines.price_unit,
                                                        } ))
                                                invoice_obj.write(cr, uid, inv_record.id, {'invoice_line':invoice_lines})
                                            
                                                    
                                account_id = account_obj.search(cr, uid, [('company_id','=',shipp_record.company_id.id),('type','=','payable')])
                                journal_ids = self.pool.get('account.journal').search(cr, uid,[('type', '=', 'purchase'), ('company_id', '=', shipp_record.company_id.id)],limit=1)
                                currency_id = currency_obj.browse(cr, uid, shipp_record.company_id.id).id
                                if flag == False:
                                    if invoice_lines:
                                        invoice_id = invoice_obj.create(cr, uid, {
                                                                            'partner_id':partner_id ,
                                                                            'type':'in_invoice',
                                                                            'journal_id':journal_ids[0],
                                                                            'currency_id':currency_id,
                                                                            'account_id':account_id[0],
                                                                            'company_id':shipp_record.company_id.id,
                                                                            'date_invoice':taday_date,
                                                                            'invoice_line':invoice_lines,
                                                                            'reference_type':'none',
                                                                            'picking_id':shipp_record.id
                                                                          },context={})
                                    else:
                                        raise osv.except_osv('Warning', 'we can not create invoice without invoice line')
                                
                                if invoice_id:
                                    inv_list.append(invoice_id)
                                    self.write(cr, uid, ids, {'invoice_ids':invoice_id})
                                    invoice_lines = []
                                    invoice_id = None
                else:
                    raise osv.except_osv('Warning', 'Please Enter Carrier Details')
                            
            return True
                        
    ## view supplier invoice.......................
    def view_supplier_invoice(self, cr, uid, ids, context=None):
          
        for o in self.browse(cr, uid, ids):
            mod_obj = self.pool.get('ir.model.data')
            act_obj = self.pool.get('ir.actions.act_window')
            result = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree1')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = o.invoice_id.id or False
        return result
stock_picking()



# class stock_picking(osv.osv):
#     
#     _inherit = 'stock.picking'
#     
#     ## getting carrier total amount .......
#     def _get_carrier_total(self, cr, uid, ids, fields, arg, context=None):
#         res ={}
#         for line in self.browse(cr, uid, ids):
#             total = 0.0
#             for o in line.response_usps_ids:
#                 if o.is_label_genrated:
#                     total += float(o.rate)
#             res[line.id] = total
#         return res
#     
#     
#     _columns = {
#                     'invoice_ids':fields.many2one('account.invoice','Invoice id'),
#                     'carrier_rate_total':fields.function(_get_carrier_total, string="Carrier Total", type='integer', store=False),
#                     'invoice_id': fields.one2many('account.invoice','picking_id','Invoices'),
#                 }
# stock_picking()


class account_invoice(osv.osv):
    
    _inherit = 'account.invoice'
    _columns = {
                    'picking_id' : fields.many2one('stock.picking','Picking'),
                
                }
account_invoice()






