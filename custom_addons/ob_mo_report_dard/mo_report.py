from openerp import models, fields, api, _
from openerp.report import report_sxw
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import datetime


class mo_production_report(report_sxw.rml_parse):
    _name = 'mo.production.report'


    def __init__(self, cr, uid, name, context):
        super(mo_production_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_line_ref': self._get_line_ref,
            'get_date_planned':self._get_date_planned,
            'get_so_ref':self._get_so_ref,
            'get_image':self.get_image,
            'get_specs_ids':self._get_specs_ids,
            'get_date_create':self._get_date_create,
            'get_dimension_field':self._get_dimension_field,
            'get_so_line_obj_ref':self._get_so_line_obj_ref,
        })
        self.context = context


    def _get_dimension_field(self,sub_origin):
        field_dict = {}
        content = []
        sale_line_obj = self.pool.get('sale.order.line')
        if sub_origin:
            sale_line_id = sale_line_obj.search(self.cr, self.uid, [('sol_seq','=', sub_origin)], context=self.context)
            obj = sale_line_obj.browse(self.cr, self.uid, sale_line_id)
            if obj.imprint_data:
                imprint = obj.imprint_data.split(", '")
                for field in imprint:
                    field = field.replace("(","")
                    field = field.replace(")","")
                    field = field.replace("\'","")
                    field = field.replace("\"","")
                    field = field.replace("{","")
                    field = field.replace("}","")
                    field = field.replace("[","")
                    field = field.replace("]","")
                    field = field.replace(":","")
                    field = field.replace(";","")
                    field = field.replace("_"," ")
                    
                    new_string = field.split(',')
                    final_field = new_string[0].replace('6','').strip().title()
                    final_id = []
                    for j in new_string[2:]:
                        final_id.append(j.strip())
                    if final_id:
                        vari_list= []
                        for i in final_id:
                            if i != '':
                                id = i.strip()
                                varient_obj = self.pool.get('product.variant.dimension.option').browse(self.cr, self.uid, int(id))
                                vari_list.append(varient_obj)
                        final_dict = {'field':final_field,
                                   'value':vari_list,
                                    }
                    else:
                        final_dict = {'field':final_field,
                                   'value':''
                                    }
                    content.append(final_dict)
        return content
        
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
                return False
        else:
            return False

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

    def get_image(self,origin):
        res= 1
        if origin.id:
            so_order_images_ids = self.pool.get('sale.order.line.images').search(self.cr, self.uid, [('state','ilike', 'confirmed'),('mrp_id','=', origin.id)], context=self.context)
            if so_order_images_ids:            
                final_rec_image = self.pool.get('sale.order.line.images').browse(self.cr, self.uid, so_order_images_ids[0]).virtual_file_name_url
                if final_rec_image:
                    return str(final_rec_image)
                else:
                    return res
            else:
                return res
        else:
            return res

    def _get_date_planned(self, date_planned):
        if date_planned:
            date_plan = datetime.datetime.strptime(date_planned, '%Y-%m-%d').strftime('%d / %B / %Y')
            return date_plan

    def _get_specs_ids(self,line_specs_ids):
        value = ''
        if line_specs_ids:
            for specs in line_specs_ids:
                if value:
                    value = value + " , "+ specs.name
                else:
                    value = specs.name

        return value

    def _get_date_create(self, date_planned):
        if date_planned:
            date_planned = date_planned.split(" ")
            date_plan = datetime.datetime.strptime(date_planned[0], '%Y-%m-%d').strftime('%d / %B / %Y')
            return date_plan

    def _get_line_ref(self, product_id, origin):
        line_obj = self.pool.get('sale.order.line')
        sale_obj = self.pool.get('sale.order')
        if origin:
            origin = origin.split(':')
            res=''
            sale_id = sale_obj.search(self.cr, self.uid, [('name','ilike', origin[0])], context=self.context)
            if sale_id:
                line_rec_id = line_obj.search(self.cr, self.uid,[('product_id','=', product_id.id),('order_id','=', sale_id[0])], context=self.context)
                if line_rec_id:
                    line_rec= line_obj.browse(self.cr, self.uid,line_rec_id[0])
                    return line_rec
                else:
                    return res
            else:
                return res
        else:
            return res



class report_production_mo(models.AbstractModel):

    _name = 'report.ob_mo_report_dard.report_production_mo'
    _inherit = 'report.abstract_report'
    _template = 'ob_mo_report_dard.report_production_mo'
    _wrapped_report_class = mo_production_report


