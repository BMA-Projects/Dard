from openerp import models, fields, api, _
from openerp.report import report_sxw
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

class work_order_report(report_sxw.rml_parse):
    _name = 'work.order.report'


    def __init__(self, cr, uid, name, context):
        super(work_order_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_so_ref': self._get_so_ref,
            'get_line_ref': self._get_line_ref,
            'get_date_planned':self._get_date_planned,
            'get_plating_date':self._get_plating_date,
            'get_metal_ids':self._get_metal_ids,
            'get_specs_ids':self._get_specs_ids,
            'get_image_ref':self._get_image_ref,
            'get_partner_rec':self._get_partner_rec,
            'get_shipping_rec':self._get_shipping_rec,
            'get_onhand_qty':self._get_onhand_qty,
            'get_entered_date':self._get_entered_date,
            'get_so_line_obj_ref':self._get_so_line_obj_ref,

        })
        self.context = context

    def _get_entered_date(self,create_date):
        entered_date = ''
        if create_date:
            create_date = datetime.strptime(create_date,DEFAULT_SERVER_DATETIME_FORMAT)
            entered_date = create_date.date()
        return entered_date

    def _get_onhand_qty(self,product_id,origin):
        product_onhand_qty = ''
        if product_id:
            sale_obj = self.pool.get('sale.order')
            product_obj = self.pool.get('product.product')
            origin = origin.split(':')
            if origin:
                sale_id = sale_obj.search(self.cr, self.uid, [('name','ilike', origin[0])], context=self.context)
                if sale_id:
                    sale_order_company = sale_obj.browse(self.cr, self.uid, sale_id[0])[0].company_id
                    if sale_order_company:
                        product_rec = product_obj.search(self.cr, self.uid,[('name','=',product_id.name),('company_id','=',sale_order_company.id)],context=self.context)
                        if product_rec:
                            product_onhand_qty = product_obj.browse(self.cr, self.uid,[product_rec[0]],context=self.context)[0].qty_available
        return product_onhand_qty

    def _get_so_line_obj_ref(self,sub_origin):

        sale_obj = self.pool.get('sale.order.line')
        
        res= ''
        if sub_origin:
            sale_line_id = sale_obj.search(self.cr, self.uid, [('sol_seq','=', sub_origin)], context=self.context)
            if sale_line_id:
                so_line_client_order_ref = sale_obj.browse(self.cr, self.uid, sale_line_id[0])
                return so_line_client_order_ref
            else:
                return False
        else:
            return False

    def _get_shipping_rec(self,origin):
        sale_obj = self.pool.get('sale.order')
        origin = origin.split(':')
        shipping_id= ''
        if origin:
            sale_id = sale_obj.search(self.cr, self.uid, [('name','ilike', origin[0])], context=self.context)
            if sale_id:
                so_client_order_ref = sale_obj.browse(self.cr, self.uid, sale_id[0])
                shipping_id = so_client_order_ref.partner_shipping_id
                return shipping_id
            else:
                return shipping_id
        else:
            return shipping_id

    def _get_partner_rec(self,origin):
        sale_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        origin = origin.split(':')
        partner_country= ''
        if origin:
            sale_id = sale_obj.search(self.cr, self.uid, [('name','ilike', origin[0])], context=self.context)
            if sale_id:
                so_client_order_ref = sale_obj.browse(self.cr, self.uid, sale_id[0])
                # print "create_uid=-=-==-====",so_client_order_ref.create_uid.name
                partner_id = so_client_order_ref.partner_id
                # print "partner_id=-=-=====",partner_id.country_id
                if partner_id.country_id:
                    partner_country = partner_id.country_id.name
                    return partner_country
                # return so_client_order_ref
            else:
                return partner_country
        else:
            return partner_country

    def _get_specs_ids(self,line_specs_ids):
        value = ''
        if line_specs_ids:
            for specs in line_specs_ids:
                if value:
                    value = value + " , "+ specs.name
                else:
                    value = specs.name

        return value

    def _get_metal_ids(self,metal_ids):
        value = ''
        metal_obj = self.pool.get('metal.master')
        if metal_ids:
            for metal_rec in metal_ids:
                if value:
                    value = value+'/'+metal_rec.name
                else:
                    value = metal_rec.name
        return value

    def _get_so_ref(self,origin):

        sale_obj = self.pool.get('sale.order')
        
        res= ''
        if origin:
            origin = origin.split(':')
            sale_id = sale_obj.search(self.cr, self.uid, [('name','ilike', origin[0])], context=self.context)
            if sale_id:
                so_client_order_ref = sale_obj.browse(self.cr, self.uid, sale_id[0])
                return so_client_order_ref
            else:
                return res
        else:
            return res

    def _get_line_ref(self, product_id, origin):
        line_obj = self.pool.get('sale.order.line')
        sale_obj = self.pool.get('sale.order')
        origin = origin.split(':')
        res=''
        sale_id = sale_obj.search(self.cr, self.uid, [('name','ilike', origin[0])], context=self.context)
        if sale_id:
            line_rec_id = line_obj.search(self.cr, self.uid,[('product_id','=', product_id.id),('order_id','=', sale_id)], context=self.context)
            if line_rec_id:
                line_rec= line_obj.browse(self.cr, self.uid,line_rec_id[0])
                return line_rec
            else:
                return res
        else:
            return res

    def _get_date_planned(self, date_planned):
        date_planned = datetime.strptime(date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
        new_date_planned = datetime.date(date_planned)
        date_planned = new_date_planned.strftime('%d/%m/%Y')
        return date_planned

    def _get_plating_date(self, plating_ids):
        plating_date = ''
        for plating_id in plating_ids:
            if plating_id.plating_ship_date:
               if plating_id.plating_ship_date > plating_date:
                   plating_date = plating_id.plating_ship_date
        return plating_date

    def _get_image_ref(self, origin, product_id):
        line_obj = self.pool.get('sale.order.line')
        sale_obj = self.pool.get('sale.order')
        line_images_obj = self.pool.get('sale.order.line.images')
        origin = origin.split(':')
        res=''
        sale_id = sale_obj.search(self.cr, self.uid, [('name','ilike', origin[0])], context=self.context)

        if sale_id:
            line_rec_id = line_obj.search(self.cr, self.uid,[('product_id','=', product_id.id),('order_id','=', sale_id)], context=self.context)
            if line_rec_id:
                line_rec= line_obj.browse(self.cr, self.uid,line_rec_id[0])
                if line_rec.order_line_image_ids:
                    for image_id in line_rec.order_line_image_ids:
                        if image_id.state== 'approved':
                            return image_id.virtual_file_name_url

                    return line_rec.order_line_image_ids[0].virtual_file_name_url
                else:
                    return res
            else:
                return res
        else:
            return res

# class report_agedpartnerbalance(models.AbstractModel):
#     _name = 'report.partner.report_agedpartnerbalance'
#     _inherit = 'report.abstract_report'
#     _template = 'ob_partner_ageing.report_agedpartnerbalance'
#     _wrapped_report_class = aged_trial_report_inherit

class report_workorder(models.AbstractModel):

    _name = 'report.ob_work_order_report.report_workorder'
    _inherit = 'report.abstract_report'
    _template = 'ob_work_order_report.report_workorder'
    _wrapped_report_class = work_order_report





