from openerp import models, fields, osv, api, _
from openerp.exceptions import Warning
from datetime import datetime, timedelta

class oe_wizard(models.TransientModel):
    _name = "oe.wizard"

    count = fields.Integer('Count', default=1)
    grp_1 = fields.Boolean('G1', default=True)
    grp_2 = fields.Boolean('G2', default=False)
    grp_3 = fields.Boolean('G3', default=False)
    grp_4 = fields.Boolean('G4', default=False)
    grp_5 = fields.Boolean('G5', default=False)
    grp_6 = fields.Boolean('G4', default=False)
    grp_7 = fields.Boolean('G5', default=False)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    client_order_ref = fields.Char(string='Customer PO Number')
    user_id = fields.Many2one('res.users', string='Salesperson')
    section_id = fields.Many2one('crm.case.section', string='Sales Team')
    date_order = fields.Datetime(string='Order Date', required=True, default=datetime.today())
    rush_order = fields.Boolean(string='Rush Order')
    is_sample = fields.Boolean(string='Sample')
    sample_type_id = fields.Many2one('sample.type', string='Sample Type')
    is_repeat_order = fields.Boolean(string='Repeat Order')
    is_repeat_art = fields.Boolean(string='Repeat Art')
    so_id = fields.Many2one('sale.order', string='Sales Orders')
    cust_po_ref_id = fields.Many2one('sale.order', string='Customer PO Number')
    prod_tmpl_id = fields.Many2one('product.template', string='Product Template')
    prod_tmpl_id1 = fields.Many2one('product.template', string='Product Template')
    prod_tmpl_id2 = fields.Many2one('product.template', string='Product Template')
    prod_tmpl_id3 = fields.Many2one('product.template', string='Product Template')
    product_details_ids = fields.One2many('product.details', 'order_wizard_id', string='Variation Details')
    product_details_ids1 = fields.One2many('product.details', 'order_wizard_id', string='Variation Details')
    product_details_ids2 = fields.One2many('product.details', 'order_wiz_id', string='Variation Details')
    product_details_ids3 = fields.One2many('product.details', 'order_wiz_id', string='Variation Details')
    printing_note = fields.Text(string='Printing Instruction', translate=True, help="To be printed on Manufacturing order.")
    packing_note = fields.Text(string='Packing Instruction', translate=True, help="To be printed on Delivery order.")
    shipping_note = fields.Text(string='Shipping Instruction', translate=True, help="To be printed on Delivery order.")
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, help="Pricelist for current order.")
    carrier_id = fields.Many2one('delivery.carrier', string='Carrier', ondelete='cascade')
    in_hand_date = fields.Datetime(string='In Hand Date', required=True, default=datetime.today())
    is_add_in_quote = fields.Boolean(string='Add in Quote')
    partner_shipping_id = fields.Many2one('res.partner', string='Ship To')
    vals_id = fields.Many2one('sale.wizard.vals', string='Sales Team')

    @api.multi
    def update_data(self):
        cnt_range = range(1,8)
        count_number = cnt_range.pop(cnt_range.index(self.count))
        keys = ['grp_' + str(x) for x in cnt_range]
        values = [False,False,False,False,False,False,False]
        write_grp = dict(zip(keys, values))
        write_grp.update({'grp_' + str(count_number): True})
        self.write(write_grp)

    @api.multi
    def get_wiz_name(self):
        name = 'OE Wizard'
        if self.grp_1:
            name = 'Customer Details'
        if self.grp_2:
            name = 'Repeat Order'
        if self.grp_3:
            name = 'Product Details'
        if self.grp_4:
            name = 'Proof Details'
        if self.grp_5:
            name = 'Special Instruction'
        if self.grp_6:
            name = 'Shipping Details'
        if self.grp_7:
            name = 'Order Preview'
        return name

    @api.multi
    def plus_wiz(self):
        name = 'Customer Details'
        context = self._context.copy()
        product_details_obj = self.env['product.details']
        prod_dim_type_obj = self.env['product.variant.dimension.type']
        #Proof Details: Set previously selected products
        if self.grp_3 and self.prod_tmpl_id:
            self.prod_tmpl_id1 = self.prod_tmpl_id
        #Set customer to select repeat order based on customer
        if self.grp_1 and self.partner_id:
            context.update({'partner_id': self.partner_id.id})
        #Check whether user selected any product or not
        # flag = 0
        # if self.grp_3:
        #     for pro_details_id in self.product_details_ids:
        #         if pro_details_id.quantity > 0:
        #             flag += 1
        #     if flag == 0:
        #         raise Warning (_('Warning!'), _('You should select at least one product before going further.'))
        self.count += 1
        self.update_data()
        #Repeat Order
        if self.is_repeat_order and (self.so_id or self.cust_po_ref_id):
            if self.grp_3:
                self.write({'grp_1': False, 'grp_2': False, 'grp_3': False, 'grp_4': False, 'grp_5': True, 'grp_6': False, 'grp_7': False})
                self.count += 2
        view_id = self.env.ref('ob_oe_through_wizard.ob_wiz_form').id
        context.update({'active_id': self.id})
        #In Hand Date should be after Order Date
        if self.grp_7 and self.in_hand_date and self.date_order and self.in_hand_date < self.date_order:
            raise Warning (_('Warning!'), _('In Hand Date should be after or equal to Order Date'))
        #Variant Details - Add new product
        if self.grp_7:
            final_products = []
            for pro_details_id in self.product_details_ids:
                if pro_details_id.quantity > 0:
                    final_products.append(pro_details_id.id)
            for pro_details_id in context.get('line_ids', []):
                if product_details_obj.browse(pro_details_id).quantity > 0:
                    final_products.append(pro_details_id)
            self.product_details_ids2 = product_details_obj.browse(final_products)
            self.product_details_ids3 = product_details_obj.browse(final_products)
            #Display Product Details while Repeat Order is selected
            if self.is_repeat_order:
                oline_ids = []
                pro_details_rec = []
                order_lines = self.so_id.order_line or self.cust_po_ref_id.order_line or []
                for oline in order_lines:
                    pro_details_rec.append(product_details_obj.create({'product_id': oline.product_id.id, 'quantity': oline.product_uom_qty, 'price': oline.price_unit, \
                        'has_imprint_method': oline.has_imprint_method, 'imprint_method': oline.imprint_method.id, 'imprint_data': oline.imprint_data,\
                        'imprint_data_fields': oline.imprint_data_fields, 'is_variant': oline.is_variant}).id)
                    # , 'imprint_details_ids': [(0, 0, {'dim_option_ids': [(6, 0, [])]})]
                    # key = oline.imprint_data_fields[0] or False
                    # if key and key in oline.imprint_data:
                    #     dim_type_id = prod_dim_type_obj.search([('name','=')])
                    # dim_option_ids
                self.product_details_ids = [(6, 0, pro_details_rec)]
                self.product_details_ids1 = [(6, 0, pro_details_rec)]
                self.product_details_ids2 = [(6, 0, pro_details_rec)]
                self.product_details_ids3 = [(6, 0, pro_details_rec)]
                    # 'order_line_image_ids': [(6, False, [artwork_id.id])],

        #Set wizard name
        name = self.get_wiz_name()
        return {
            'name': name or 'OE WIZARD',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'oe.wizard',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'res_id': self.id,
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        
    @api.multi
    def minus_wiz(self):
        self.count -= 1
        self.update_data()
        #Repeat Order
        if self.is_repeat_order and (self.so_id or self.cust_po_ref_id):
            if self.grp_4:
                self.write({'grp_1': False, 'grp_2': True, 'grp_3': False, 'grp_4': False, 'grp_5': False, 'grp_6': False, 'grp_7': False})
                self.count -= 2
        view_id = self.env.ref('ob_oe_through_wizard.ob_wiz_form').id
        #Set wizard name
        name = self.get_wiz_name()
        return {
            'name': name or 'OE WIZARD',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'oe.wizard',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'context': self._context,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }

    @api.multi
    def add_new_product(self):
        view_id = self.env.ref('ob_oe_through_wizard.ob_wiz_form').id
        context = self._context.copy()
        details_ids = []
        for details_id in self.product_details_ids:
            details_ids.append(details_id.id)
        if 'line_ids' in context and context['line_ids']:
            context['line_ids'].extend(details_ids)
        else:
            context.update({'line_ids': details_ids})
        self.prod_tmpl_id = False
        self.product_details_ids = False
        self.count -= 1
        self.write({'grp_1': False, 'grp_2': False, 'grp_3': True, 'grp_4': False, 'grp_5': False, 'grp_6': False, 'grp_7': False})
        #Set wizard name
        name = self.get_wiz_name()
        return {
            'name': name or 'OE WIZARD',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'oe.wizard',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'context': context,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }


    @api.onchange('is_sample')
    def _onchange_is_sample(self):
        self.sample_type_id = False

    @api.onchange('is_repeat_order')
    def _onchange_is_repeat_order(self):
        if not self.is_repeat_order:
            self.so_id = False
            self.cust_po_ref_id = False

    @api.onchange('is_add_in_quote', 'carrier_id', 'partner_shipping_id')
    def _onchange_is_add_in_quote(self):
        carrier_obj = self.pool.get('delivery.carrier')
        if self.is_add_in_quote and self.carrier_id and self.partner_shipping_id:
            grid_id = self.carrier_id.grid_get(self.partner_shipping_id.id)
            if not grid_id:
                raise Warning(_('No grid matching for this carrier!'))


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.pricelist_id = self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False
        self.so_id = False
        self.cust_po_ref_id = False
        self.is_repeat_order = False

    @api.onchange('prod_tmpl_id')
    def _onchange_prod_tmpl_id(self):
        product_obj = self.env['product.product']
        product_details_obj = self.env['product.details']
        variation = product_obj.search([('product_tmpl_id','=',self.prod_tmpl_id.id)])
        pd_ids = []
        active_id = 'active_id' in self._context and self._context['active_id'] or False
        for variation_id in variation:
            vals = {}
            vals.update({'product_id': variation_id.id, 'is_variant': variation_id.is_variant, 'is_proof_required': True})
            if active_id:
                pricelist = self.pricelist_id
                if not pricelist:
                    raise Warning(_('You have to select a pricelist or a customer in the Customer Details form !\n'
                            'Please set one before choosing a product.'))
                else:
                    cntxt = self._context.copy()
                    cntxt.update({'uom': variation_id.uom_id.id or False, 'date': self.date_order})
                    price = pricelist.price_get(variation_id.id, 1.0, self.partner_id.id, context=cntxt)[pricelist.id]
                    if price is False:
                        raise Warning(_("Cannot find a pricelist line matching this product and quantity.\n"
                                "You have to change either the product, the quantity or the pricelist."))
                    else:
                        vals.update({'price': price})
            pd_ids.append((0,0, vals))
            self.product_details_ids = pd_ids

    @api.multi
    def save_order(self):
        ir_model_data = self.env['ir.model.data']
        sale_obj = self.env['sale.order']
        view_id = ir_model_data.get_object_reference('sale', 'view_order_form')[1]
        search_view_id = ir_model_data.get_object_reference('sale', 'view_sales_order_filter')[1]
        cntx = self._context.copy()
        rec = self.browse(self._context['active_id'])
        sale_vals = {'partner_id': self.partner_id.id or False,
        'client_order_ref': self.client_order_ref or False,
        'user_id': self.user_id.id or False,
        'section_id': self.section_id.id or False,
        'date_order': self.date_order or False,
        'pricelist_id': self.pricelist_id.id or False,
        'is_sample': self.is_sample or False,
        'sample_type_id': self.sample_type_id.id or False,
        'carrier_id': self.carrier_id.id or False,
        'partner_shipping_id': self.partner_shipping_id.id or self.partner_id.id or False,
        'rush_order': self.rush_order or False,
        'printing_note': self.printing_note or False,
        'packing_note': self.packing_note or False,
        'shipping_note': self.shipping_note or False,
        'in_hand_date': self.in_hand_date or False,
        }

        #Product Variant Data
        prod_imp_details_obj = self.env['prod.imp.details']
        prod_details_obj = self.env['product.details']
        prod_vari_dim_type_obj = self.env['product.variant.dimension.type']
        sale_line_obj = self.env['sale.order.line']
        images_obj = self.env['sale.order.line.images']
        prod_imp_details_ids = []
        line_ids2 = []
        imprint_data = {}
        has_imprint_method = False

        #In Hand Date should be after Order Date
        if self.grp_7 and self.in_hand_date and self.date_order and self.in_hand_date < self.date_order:
            raise Warning (_('Warning!'), _('In Hand Date should be after or equal to Order Date'))
        if self.is_repeat_order:
            oline_ids = []
            order_lines = self.so_id.order_line or self.cust_po_ref_id.order_line or []
            for oline in order_lines:
                new_line = oline.copy()
                oline_ids.append((new_line).id)
            sale_vals.update({'order_line': [(6, 0, oline_ids)]})
        sale_id = sale_obj.create(sale_vals)
        if not self.is_repeat_order:
            #For Add New Porduct
            for pro_detail_id in self.product_details_ids:
                line_ids2.append(pro_detail_id.id)  
            if 'line_ids' in cntx and cntx['line_ids']:
                line_ids2.extend(cntx['line_ids'])
            #To set Imprint Data and Imprint Data Fields
            for pro_detail_id in prod_details_obj.browse(line_ids2):
                res = prod_imp_details_obj.search([('pro_details_id','=', pro_detail_id.id)])
                if pro_detail_id.imprint_method.attribute_field_type == 'none':
                    has_imprint_method = True
                prod_vari_dim_type_rec = prod_vari_dim_type_obj.browse(res.dim_type_id.id)
                field_name = str(prod_vari_dim_type_rec.name).lower().replace(" ", "_")
                field_string = prod_vari_dim_type_rec.name
                if pro_detail_id.imprint_details_ids:#or if res:
                    options_ids = []
                    dim_type_id = False
                    for imp_details_id in pro_detail_id.imprint_details_ids:
                        dim_type_id = imp_details_id.dim_type_id
                        for dim_option_id in imp_details_id.dim_option_ids:
                            options_ids.append(dim_option_id.id)
                    if dim_type_id.attribute_field_type == 'dropdown':
                        imprint_data = {str(field_name): options_ids}
                    elif dim_type_id.attribute_field_type == 'multiselection':
                        imprint_data = {str(field_name): [(6, False, options_ids)]}
                pro_detail_id.write({'imprint_data_fields':[field_name], 'imprint_data': imprint_data or {}})
                #Create Artwork Lines
                artwork_id = images_obj.create({'art_image_name': 'art image'+ str(pro_detail_id.id) or '', \
                    'art_image': pro_detail_id.art_image, 'description': 'art image'+ str(pro_detail_id.id) or ''})
                #Create Order Lines
                if pro_detail_id.quantity > 0:
                    sale_line_obj.create({
                    'order_id': sale_id.id,
                    'product_id': pro_detail_id.product_id.id,
                    'product_uom_qty': pro_detail_id.quantity,
                    'price_unit': pro_detail_id.price,
                    'has_imprint_method': has_imprint_method,
                    'imprint_method': pro_detail_id.imprint_method.id,
                    'imprint_data_fields': pro_detail_id.imprint_data_fields,
                    'imprint_data': pro_detail_id.imprint_data,
                    'is_variant': pro_detail_id.is_variant,
                    'order_line_image_ids': [(6, False, [artwork_id.id])],
                    })

        # sale_id = sale_obj.create(sale_vals)
        if sale_id.carrier_id and self.is_add_in_quote:
            sale_id.delivery_set()
        cntx.update({'search_default_my_sale_orders_filter': 1})

        return {
            'name': 'Quotations',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree,calendar,graph',
            'res_model': 'sale.order',
            'res_id': sale_id.id,
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'context': cntx,
            'search_view_id': search_view_id,
        }

class prod_imp_details(models.TransientModel):
    _name = 'prod.imp.details'

    dim_type_id = fields.Many2one('product.variant.dimension.type', string='Dimension Type')
    dim_option_ids = fields.Many2many('product.variant.dimension.option', string='Dimension Option Value')
    pro_details_id = fields.Many2one('product.details', string='Product Details')
    line_attr_max_val = fields.Integer(string='Line Attribute Max Value')
    attribute_field_type = fields.Selection([
            ('none', 'None'),
            ('dropdown', 'DropDown'),
            ('multiselection', 'Multi Selection')], 'Attribute Field Type')

class wiz_artwork(models.TransientModel):
    _name = 'wiz.artwork'

    art_image = fields.Text("Image")

    @api.multi
    def upload_art(self):
        ir_model_data = self.env['ir.model.data']
        view_id = ir_model_data.get_object_reference('ob_oe_through_wizard', 'ob_wiz_form')[1]
        cntx = self._context.copy()
        prod_details_obj = self.env['product.details']
        prod_details_obj.browse(cntx.get('active_id', False)).write({'art_image': self.art_image, 'upload_id': self.id})
        return {
            'name': 'Proof Details',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'oe.wizard',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'res_id': cntx.get('wizard_id',False),
            'context': cntx,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
    
    @api.multi
    def display_wizard(self):
        ir_model_data = self.env['ir.model.data']
        view_id = ir_model_data.get_object_reference('ob_oe_through_wizard', 'ob_wiz_form')[1]
        return {
            'name': 'Proof Details',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'oe.wizard',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'res_id': self._context.get('wizard_id',False),
            'context': self._context,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }    

class product_details(models.TransientModel):
    _name = 'product.details'

    product_id = fields.Many2one('product.product', string='Product Variant', readonly=True)
    quantity = fields.Float(string='Quantity')
    price = fields.Float(string='Price')
    imprint_method = fields.Many2one('product.variant.dimension.type', string='Imprint Method')
    is_proof_required = fields.Boolean(string='Proof Required', default=True)
    order_wizard_id = fields.Many2one('sale_order_wizard', string='Order Wizard', readonly=True)
    order_wiz_id = fields.Many2one('sale_order_wizard', string='Order Wizard', readonly=True)
    imprint_data_fields = fields.Char(string='Imprint Data Key')
    imprint_data = fields.Char(string='Imprint Data')
    is_variant = fields.Boolean(string='Is Variant')
    has_imprint_method = fields.Boolean(string='Has Imprint Method')
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    email = fields.Char(string='Email')
    proof_date = fields.Datetime(string='Proof Date')
    imprint_details_ids = fields.One2many('prod.imp.details', 'pro_details_id', string='Imprint Details')
    virtual_proofing_required = fields.Boolean('Art Proofing Required')
    manual_approval = fields.Boolean('Manual Approval')
    art_image = fields.Text("Image")
    upload_id = fields.Integer("Upload Wizard ID")

    @api.multi
    def upload_artwork(self):
        ir_model_data = self.env['ir.model.data']
        view_id = ir_model_data.get_object_reference('ob_oe_through_wizard', 'ob_wiz_artwork_form')[1]
        cntx = self._context.copy()
        return {
            'name': 'Upload ArtWork',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wiz.artwork',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'context': cntx,
            'res_id': self.upload_id or False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.onchange('imprint_method')
    def onchange_imprint_method(self):
        vals = {}
        imprint_method = self.imprint_method.id
        product_id = self.product_id.id
        prod_imp_details_obj = self.env['prod.imp.details']
        product_obj = self.env['product.product']
        product_rec = product_obj.browse([product_id])[0]
        dim_type_ids = []
        if not imprint_method:
            self.imprint_data_fields = False
        for product_dimension_type_rec in product_rec.product_tmpl_id.product_dimension_type_ids:
            if product_dimension_type_rec.product_dimension_id2.attribute_field_type != 'none' \
                and imprint_method in [child_id.id for child_id in product_dimension_type_rec.product_dimension_child_ids]:
                # dim_type_ids.append(prod_imp_details_obj.create({'dim_type_id': product_dimension_type_rec.product_dimension_id2.id}).id)
                dim_type_ids.append((0, 0, {'dim_type_id': product_dimension_type_rec.product_dimension_id2.id, \
                    'line_attr_max_val': product_dimension_type_rec.attribute_max_value, 'attribute_field_type': product_dimension_type_rec.attribute_field_type}))
        # self.imprint_details_ids = [(6, 0, dim_type_ids)]
        self.imprint_details_ids = dim_type_ids


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: