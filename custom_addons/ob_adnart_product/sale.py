# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_compare
        
class sale_line_attachment(models.Model):
    _name="sale.line.attachemnt"
    
    _rec_name = 'att_product_id'

    att_product_id = fields.Many2one('product.product', string="Product", )
    prod_uom_qty = fields.Float(string="Quantity")
    prod_uom = fields.Many2one('product.uom', string="UOM")
    prod_unit_price = fields.Float(string="Unit price")
    prod_discount = fields.Float(string="Discount (%)" ,digits_compute= dp.get_precision('Discount'))
    prod_tax_id = fields.Many2many("account.tax","sale_line_atta_tax", 'sale_line_tax_id','tax_id',string="Taxes")
    sale_prod_att_id = fields.Many2one('sale.order.line', string="Product Attachment")
    
    def att_product_id_change(self, cr, uid, ids, product, pricelist, qty=0, discount=0.0 ,uom=False, date_order=False, partner_id=False, update_tax=True,fiscal_position = False, packaging=False, warehouse_id=False, context=None):
        result = {}
        if not product:
            return result
        context = context or {}
        lang = context.get('lang', False)
#         if not partner_id:
#             raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
        warning = False
        warehouse_obj = self.pool['stock.warehouse']
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        sol_obj = self.pool.get('sale.order.line')
        context = {'lang': lang, 'partner_id': partner_id}
        partner = partner_obj.browse(cr, uid, partner_id)
        lang = partner.lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)
        result.update({'prod_uom_qty':qty,'prod_uom' :uom, 'prod_discount' :discount})

        fpos = False
        if not fiscal_position:
            fpos = partner.property_account_position or False
        else:
            fpos = self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position)
        if update_tax: #The quantity only have changed
            result['prod_tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)
# 

        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                    'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        })[pricelist]
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")
  
                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                result.update({'prod_unit_price': price})

        result.update({'product_tmpl_id': product_obj.product_tmpl_id.id, 'delay': (product_obj.sale_delay or 0.0)})

        # Calling product_packaging_change function after updating UoM
        res_packing = sol_obj.product_packaging_change(cr, uid, ids, pricelist, product, qty, uom, partner_id, packaging, context=context)
        result.update(res_packing.get('value', {}))
        warning_msgs = res_packing.get('warning') and res_packing['warning']['message'] or ''

        if product_obj.type == 'product':
            #determine if the product is MTO or not (for a further check)
            isMto = False
            if warehouse_id:
                warehouse = warehouse_obj.browse(cr, uid, warehouse_id, context=context)
                for product_route in product_obj.route_ids:
                    if warehouse.mto_pull_id and warehouse.mto_pull_id.route_id and warehouse.mto_pull_id.route_id.id == product_route.id:
                        isMto = True
                        break
            else:
                try:
                    mto_route_id = warehouse_obj._get_mto_route(cr, uid, context=context)
                except:
                    # if route MTO not found in ir_model_data, we treat the product as in MTS
                    mto_route_id = False
                if mto_route_id:
                    for product_route in product_obj.route_ids:
                        if product_route.id == mto_route_id:
                            isMto = True
                            break

            #check if product is available, and if not: raise a warning, but do this only for products that aren't processed in MTO
            if not isMto:
                uom_record = False
                if uom:
                    uom_record = product_uom_obj.browse(cr, uid, uom, context=context)
                    if product_obj.uom_id.category_id.id != uom_record.category_id.id:
                        uom_record = False
                if not uom_record:
                    uom_record = product_obj.uom_id
                compare_qty = float_compare(product_obj.virtual_available, qty, precision_rounding=uom_record.rounding)
                if compare_qty == -1:
                    warn_msg = _('You plan to sell %.2f %s but you only have %.2f %s available !\nThe real stock is %.2f %s. (without reservations)') % \
                        (qty, uom_record.name,
                         max(0,product_obj.virtual_available), uom_record.name,
                         max(0,product_obj.qty_available), uom_record.name)
                    warning_msgs += _("Not enough stock ! : ") + warn_msg + "\n\n"

        #update of warning messages
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        return {'value': result, 'warning': warning}
#         return {'value': result, 'domain': domain, 'warning': warning}

class sale_line_packaging(models.Model):
    _name="sale.line.packaging"
    
    _rec_name = 'pack_product_id'
    
    pack_product_id = fields.Many2one('product.product', string="Product")
    prod_uom_qty = fields.Float(string="Quantity")
    prod_uom = fields.Many2one('product.uom', string="UOM")
    prod_unit_price = fields.Float(string="Unit price")
    prod_discount = fields.Float(string="Discount")
    prod_tax_id = fields.Many2many("account.tax","sale_line_pack_tax", 'sale_line_pack_id','tax_id',string="Taxes")
    sale_prod_pack_id = fields.Many2one('sale.order.line', string="Product Packaging")

    def pack_product_id_change(self, cr, uid, ids, product, pricelist, qty=0, discount=0.0 ,uom=False, date_order=False, partner_id=False, update_tax=True,fiscal_position = False,  packaging=False, warehouse_id=False,  context=None):
        result = {}
        if not product:
            return result
        context = context or {}
        lang = context.get('lang', False)
        warehouse_obj = self.pool['stock.warehouse']
#         if not partner_id:
#             raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
        warning = False
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        sol_obj = self.pool.get('sale.order.line')
        context = {'lang': lang, 'partner_id': partner_id}
        partner = partner_obj.browse(cr, uid, partner_id)
        lang = partner.lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)
        result.update({'prod_uom_qty':qty,'prod_uom' :uom, 'prod_discount' :discount})
# 
        fpos = False
        if not fiscal_position:
            fpos = partner.property_account_position or False
        else:
            fpos = self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position)
        if update_tax: #The quantity only have changed
            result['prod_tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)
# 
        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                    'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        })[pricelist]
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")
  
                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                result.update({'prod_unit_price': price})
        result.update({'product_tmpl_id': product_obj.product_tmpl_id.id, 'delay': (product_obj.sale_delay or 0.0)})

        # Calling product_packaging_change function after updating UoM
        res_packing = sol_obj.product_packaging_change(cr, uid, ids, pricelist, product, qty, uom, partner_id, packaging, context=context)
        result.update(res_packing.get('value', {}))
        warning_msgs = res_packing.get('warning') and res_packing['warning']['message'] or ''

        if product_obj.type == 'product':
            #determine if the product is MTO or not (for a further check)
            isMto = False
            if warehouse_id:
                warehouse = warehouse_obj.browse(cr, uid, warehouse_id, context=context)
                for product_route in product_obj.route_ids:
                    if warehouse.mto_pull_id and warehouse.mto_pull_id.route_id and warehouse.mto_pull_id.route_id.id == product_route.id:
                        isMto = True
                        break
            else:
                try:
                    mto_route_id = warehouse_obj._get_mto_route(cr, uid, context=context)
                except:
                    # if route MTO not found in ir_model_data, we treat the product as in MTS
                    mto_route_id = False
                if mto_route_id:
                    for product_route in product_obj.route_ids:
                        if product_route.id == mto_route_id:
                            isMto = True
                            break

            #check if product is available, and if not: raise a warning, but do this only for products that aren't processed in MTO
            if not isMto:
                uom_record = False
                if uom:
                    uom_record = product_uom_obj.browse(cr, uid, uom, context=context)
                    if product_obj.uom_id.category_id.id != uom_record.category_id.id:
                        uom_record = False
                if not uom_record:
                    uom_record = product_obj.uom_id
                compare_qty = float_compare(product_obj.virtual_available, qty, precision_rounding=uom_record.rounding)
                if compare_qty == -1:
                    warn_msg = _('You plan to sell %.2f %s but you only have %.2f %s available !\nThe real stock is %.2f %s. (without reservations)') % \
                        (qty, uom_record.name,
                         max(0,product_obj.virtual_available), uom_record.name,
                         max(0,product_obj.qty_available), uom_record.name)
                    warning_msgs += _("Not enough stock ! : ") + warn_msg + "\n\n"                

        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        return {'value': result, 'warning': warning}
#         return {'value': result, 'domain': domain, 'warning': warning}

class sale_order(models.Model):
    _inherit = "sale.order"
    
#     def create(self, cr, uid, vals, context=None):
#         print 'sale order method callll'
#         if not context: context = {}
#         sol_obj = self.pool.get('sale.order.line')
#         so_id = super(sale_order, self).create(cr, uid, vals, context=context)
#         
#         att_vals={}
#         
#         sale_data = self.browse(cr, uid, so_id, context=context)
# #         for att_rec in self.browse(cr, uid, so_id, context).order_line[0].sale_prod_att_ids:
# # #             print 'line reccccccccc',line_rec.sale_prod_att_ids
# # #             for att_rec in line_rec.sale_prod_att_ids:
# #             att_vals.update({
# #                     'product_id':att_rec.att_product_id.id,
# #                     'sale_prod_att_id' : att_rec.id,
# #                     'name' : '',
# #                     'product_uom_qty' : att_rec.prod_uom_qty ,
# #                     'product_uom' : att_rec.prod_uom.id,
# #                     'price_unit' : att_rec.prod_unit_price,
# #                     'tax_id' : att_rec.prod_tax_id,
# #                     'discount' : att_rec.prod_discount,
# #                     'line_ship_dt' : False,
# #                     'line_sc_date' : False,
# #                     'sale_prod_att_ids':False,
# #                     'order_id' : so_id,
# #                 })
# #         temp_dic =  {'sale_prod_att_id': 13, 'product_uom': 1, 'order_id': so_id, 
# #                      'price_unit': 0.0, 'product_uom_qty': 1.0, 'discount': 0.0, 
# #                      'line_sc_date': False, 'product_id': 2734,
# #                       'sol_seq': u'SOL000086', 'line_ship_dt': False,
# #                        'sale_prod_att_ids': False, 'name': ''}
# #         sol_obj.create(cr, uid, temp_dic, context=context)
# #             for pack_rec in  line_rec.sale_prod_pack_ids:
# #                 pack_vals = {
# #                         'product_id':pack_rec.pack_product_id.id,
# #                         'sale_prod_pack_id' : pack_rec.id,
# #                         'name' : '',
# #                         'product_uom_qty' : pack_rec.prod_uom_qty ,
# #                         'product_uom' : pack_rec.prod_uom.id,
# #                         'price_unit' : pack_rec.prod_unit_price,
# #                         'tax_id' : pack_rec.prod_tax_id,
# #                         'discount' : pack_rec.prod_discount,
# #                         'line_ship_dt' : False,
# #                         'line_sc_date' :  False,
# #                         'sale_prod_pack_ids':False,
# #                         'order_id' : so_id,
# #                     }
# #                 sol_obj.create(cr, uid, pack_vals, context=context)
#         return so_id

    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}
        update_id = []
        appended_list = []
        sale_line_obj = self.pool.get('sale.order.line')
        for sol_data in vals.get('order_line',[]):
            if len(sol_data)>2:
                if sol_data[2]:
                    for att_data in sol_data[2].get('sale_prod_att_ids',[]):
                        if att_data[0] in (2,3,5):
                            rem_id = sale_line_obj.search(cr, uid, [('sale_prod_att_id','=',att_data[1])], context=context)
                            if rem_id:
                                appended_list.append([2,rem_id[0],False])
                    for att_data in sol_data[2].get('sale_prod_pack_ids',[]):
                        if att_data[0] in (2,3,5):
                            rem_id = sale_line_obj.search(cr, uid, [('sale_prod_pack_id.id','=',att_data[1])], context=context)
                            if rem_id:
                                appended_list.append([2,rem_id[0],False])
        for a in appended_list:
            vals['order_line'].append(a)
        a_list = []
        for order_line in self.browse(cr, uid, ids, context=context).order_line:
            if order_line.sale_prod_att_id.id:
                a_list.append(order_line.sale_prod_att_id.id)
            if order_line.sale_prod_pack_id.id:
                a_list.append(order_line.sale_prod_pack_id.id)
        res = super(sale_order, self).write(cr, uid, ids, vals, context=context)
        
        for order_line in self.browse(cr, uid, ids, context=context).order_line:
            if order_line.sale_prod_att_ids:
                for sale_att_data in order_line.sale_prod_att_ids:
                    tax_ids = [x.id for x in sale_att_data.prod_tax_id]
                    if sale_att_data.id in a_list:
                        att_vals = {
                            'product_id':sale_att_data.att_product_id.id,
                            'sale_prod_att_id' : sale_att_data.id,
                            'name' : sale_att_data.att_product_id.name,
                            'product_uom_qty' : sale_att_data.prod_uom_qty ,
                            'standard_price' : sale_att_data.att_product_id.standard_price,
                            'product_uom' : sale_att_data.prod_uom.id,
                            'price_unit' : sale_att_data.prod_unit_price,
                            'tax_id' : [(6,0,tax_ids)],
                            'discount' : sale_att_data.prod_discount,
                            'line_ship_dt' : order_line.line_ship_dt or False,
                            'line_sc_date' : order_line.line_sc_date or False,
                            'sale_prod_att_ids':False,
                        }
                        sol_id = sale_line_obj.search(cr, uid, [('sale_prod_att_id.id','=',sale_att_data.id)])
                        sale_line_obj.write(cr, uid, sol_id, att_vals, context=context)
                        a_list.remove(sale_att_data.id)
                    else:
                        att_vals = {
                            'product_id':sale_att_data.att_product_id.id,
                            'sale_prod_att_id' : sale_att_data.id,
                            'name' : sale_att_data.att_product_id.name,
                            'product_uom_qty' : sale_att_data.prod_uom_qty ,
                            'product_uom' : sale_att_data.prod_uom.id,
                            'price_unit' : sale_att_data.prod_unit_price,
                            'standard_price' : sale_att_data.att_product_id.standard_price,
                            'tax_id' : [(6,0,tax_ids)],
                            'discount' : sale_att_data.prod_discount,
                            'line_ship_dt' : order_line.line_ship_dt or False,
                            'line_sc_date' : order_line.line_sc_date or False,
                            'sale_prod_att_ids':False,
                            'order_id' : order_line.order_id.id
                        }
                        sale_line_obj.create(cr, uid, att_vals, context=context)
            if order_line.sale_prod_pack_ids:
                for sale_pack_data in order_line.sale_prod_pack_ids:
                    tax_ids = [x.id for x in sale_att_data.prod_tax_id]
                    if sale_pack_data.id in a_list:
                        pack_vals = {
                            'product_id':sale_pack_data.pack_product_id.id,
                            'sale_prod_pack_id' : sale_pack_data.id,
                            'name' : sale_pack_data.pack_product_id.name,
                            'product_uom_qty' : sale_pack_data.prod_uom_qty ,
                            'product_uom' : sale_pack_data.prod_uom.id,
                            'standard_price' : sale_pack_data.pack_product_id.standard_price,
                            'price_unit' : sale_pack_data.prod_unit_price,
                            'tax_id' : [(6,0,tax_ids)],
                            'discount' : sale_pack_data.prod_discount,
                            'line_ship_dt' : order_line.line_ship_dt or False,
                            'line_sc_date' : order_line.line_sc_date or False,
                            'sale_prod_att_ids':False,
                        }
                        sol_id = sale_line_obj.search(cr, uid, [('sale_prod_pack_id.id','=',sale_pack_data.id)])
                        sale_line_obj.write(cr, uid, sol_id, pack_vals, context=context)
                        a_list.remove(sale_pack_data.id)
                    else:
                        pack_vals = {
                            'product_id':sale_pack_data.pack_product_id.id,
                            'sale_prod_pack_id' : sale_pack_data.id,
                            'name' : sale_pack_data.pack_product_id.name,
                            'product_uom_qty' : sale_pack_data.prod_uom_qty ,
                            'product_uom' : sale_pack_data.prod_uom.id,
                            'price_unit' : sale_pack_data.prod_unit_price,
                            'standard_price' : sale_pack_data.pack_product_id,
                            'tax_id' : [(6,0,tax_ids)],
                            'discount' : sale_pack_data.prod_discount,
                            'line_ship_dt' : order_line.line_ship_dt or False,
                            'line_sc_date' : order_line.line_sc_date or False,
                            'sale_prod_att_ids':False,
                            'order_id' : order_line.order_id.id
                        }
                        sale_line_obj.create(cr, uid, pack_vals, context=context)
        return res

class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    sale_prod_att_ids = fields.One2many('sale.line.attachemnt','sale_prod_att_id',string='Attachments')
    sale_prod_pack_ids = fields.One2many('sale.line.packaging','sale_prod_pack_id',string='Packages')
    temp_price_list_id = fields.Many2one('product.pricelist',string='Temp Price list')
    temp_date_order = fields.Datetime('Temp date order')
    temp_partner_id = fields.Many2one('res.partner',string="Temp partner id")
    temp_fiscal_position =  fields.Many2one('account.fiscal.position', string ='Fiscal Position')
    temp_warehouse_id = fields.Many2one('stock.warehouse', string = "Temp warehouse id")
    sale_prod_att_id = fields.Many2one('sale.line.attachemnt', string="Parent sale prod id")
    sale_prod_pack_id = fields.Many2one('sale.line.packaging', string="Parent sale prod id")
   
   
#     def create(self, cr, uid, vals, context=None):
#         print '=====>>> ', vals
#         import inspect
#         for i in inspect.stack():
#             print "====>>",i
#         return super(sale_order_line, self).create(cr, uid, vals, context)
       
    def product_id_change_with_wh(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, warehouse_id=False, context=None):
        res =  super(sale_order_line, self).product_id_change_with_wh( cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, warehouse_id=warehouse_id, context=context)
        if warehouse_id:
            res['value'].update({'temp_warehouse_id': warehouse_id})
        return res
   
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        res = super(sale_order_line,self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        if not res :
            res['value'] = {}
        if pricelist:
            res['value'].update({'temp_price_list_id': pricelist})
        if date_order:
            res['value'].update({'temp_date_order': date_order})
        if partner_id:
            res['value'].update({'temp_partner_id': partner_id})
        if fiscal_position:
            res['value'].update({'temp_fiscal_position': fiscal_position})
        if qty:
            new_sale_atta_id = []
            new_sale_pack_id = []
            if 'sale_prod_att_ids' in context:
                new_sale_atta_id = context.get('sale_prod_att_ids',[])
                appended_list = []
                for rec in new_sale_atta_id:
                    if rec[0] in [0,1]:
                        rec[2].update({
                            'prod_uom_qty': qty
                        })
                    if rec[0] in [4]:
                        appended_list.append((1,rec[1],{'prod_uom_qty':qty}))
                new_sale_atta_id += appended_list
            if 'sale_prod_pack_ids' in context:
                new_sale_pack_id = context.get('sale_prod_pack_ids',[])
                appended_list2 = []
                for rec in new_sale_pack_id:
                    if rec[0] in [0,1]:
                        rec[2].update({
                            'prod_uom_qty': qty
                        })
                    if rec[0] in [4]:
                        appended_list2.append((1,rec[1],{'prod_uom_qty':qty}))
                new_sale_pack_id += appended_list2
            res['value'].update({'sale_prod_att_ids': new_sale_atta_id, 'sale_prod_pack_ids' : new_sale_pack_id})
        return res 
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: