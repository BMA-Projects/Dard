#!/usr/bin/env python
# coding: utf-8
import xmlrpclib
import xlrd
import xlwt
from xlwt import Workbook
import datetime# 2014-11-06 16:21:13#2014-11-06 16:22:31 - 1.18
import sys
print "Start Time = ", datetime.datetime.now()
args = sys.argv


dbname = 'dard_import_new'
username = 'admin'
pwd = 'admin'
 
#sock_common = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/common')
#sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

sock_common = xmlrpclib.ServerProxy ('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')

uid = sock_common.login(dbname, username, pwd)

workbook = xlrd.open_workbook('DARD Product Data All Items 032816.xls')
worksheet = workbook.sheet_by_name('Active Items')

num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = 1

my_data = {}
run_charge_cols = [15, 22, 24, 26]
color_attribute_id = sock.execute(dbname, uid, pwd, 'product.attribute', 'search', [('name','=','Color')])
if color_attribute_id:
    color_attribute_id = color_attribute_id[0]

size_attribute_id = sock.execute(dbname, uid, pwd, 'product.attribute', 'search', [('name','=','Size')])
if size_attribute_id:
    size_attribute_id = size_attribute_id[0]


while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    prod_tmpl_name = row[5].value.strip().title()

    #4 Imprint Methods
    imprint_method = []
    if row[9].value and row[9].value.strip().title() not in imprint_method and row[9].value != 'N/A':
        imprint_method.append(row[9].value.strip().title())
    if row[10].value and row[10].value.strip().title() not in imprint_method and row[10].value != 'N/A':
        imprint_method.append(row[10].value.strip().title())
    if row[11].value and row[11].value.strip().title() not in imprint_method and row[11].value != 'N/A':
        imprint_method.append(row[11].value.strip().title())
    if row[12].value and row[12].value.strip().title() not in imprint_method and row[12].value != 'N/A':
        imprint_method.append(row[12].value.strip().title())

    #4 Imprint Positions
    imprint_position = []
    if row[17].value and row[17].value.strip().title() not in imprint_position and row[17].value != 'N/A':
        imprint_position.append(row[17].value.strip().title())
    if row[18].value and row[18].value.strip().title() not in imprint_position and row[18].value != 'N/A':
        imprint_position.append(row[18].value.strip().title())
    if row[19].value and row[19].value.strip().title() not in imprint_position and row[19].value != 'N/A':
        imprint_position.append(row[19].value.strip().title())
    if row[20].value and row[20].value.strip().title() not in imprint_position and row[20].value != 'N/A':
        imprint_position.append(row[20].value.strip().title())
    
    color = []
    size = []
    if row[29].value.strip() and row[29].value.strip() != 'N/A':
        color = sock.execute(dbname, uid, pwd, 'product.attribute.value', 'search', [('name','=',row[29].value.strip().title()), ('attribute_id','=',color_attribute_id)])
        if not color:
            color = [sock.execute(dbname, uid, pwd, 'product.attribute.value', 'create', {'name': row[29].value.strip().title(), 'attribute_id':color_attribute_id})]
            
    if row[27].value.strip() and row[27].value.strip() != 'N/A':
        size = sock.execute(dbname, uid, pwd, 'product.attribute.value', 'search', [('name','=',row[27].value.strip().title()), ('attribute_id','=',size_attribute_id)])
        if not size:
            size = [sock.execute(dbname, uid, pwd, 'product.attribute.value', 'create', {'name': row[27].value.strip().title(), 'attribute_id': size_attribute_id})]

    if prod_tmpl_name in my_data.keys():
        prod_tmpl_data = my_data.get(prod_tmpl_name)

        #Append Color, Size, SKU, Description
        variant_list = prod_tmpl_data.get("variant",[])

        variant_list.append({
            'desc': row[6].value and row[6].value.strip(),
            'sku': row[2].value and row[2].value.strip(),
            'color': color,
            'size': size
        })

        
        prod_tmpl_data.update({'variant': variant_list})

        #Append Imprint Method
        imprint_method_lst = prod_tmpl_data.get("imprint_method",[])
        for imp_met in imprint_method:
            if imp_met not in imprint_method_lst:
                imprint_method_lst.append(imp_met)
        prod_tmpl_data.update({'imprint_method': imprint_method_lst})
        if row[13].value:
             prod_tmpl_data.update({'setup_charge': row[13].value})
        #Attribute Max Value/Run charge Available
        max_free_att = 0
        run_charge = 0
        for col in run_charge_cols:
            if row[col].value and isinstance(row[col].value, unicode) and row[col].value.strip() == 'FREE':
                max_free_att += 1
            elif row[col].value and isinstance(row[col].value, unicode) and row[col].value.strip() == 'N/A':
                continue
            elif row[col].value and not isinstance(row[col].value, unicode):
                run_charge = row[col].value
                break
        
        prod_tmpl_data.update({'attribute_max_value': row[16].value})
        prod_tmpl_data.update({'run_charge': run_charge})
        prod_tmpl_data.update({'max_free_attributes': max_free_att})
        #Append Imprint Position
        imprint_position_lst = prod_tmpl_data.get("imprint_position",[])
        for imp_pos in imprint_position:
            if imp_pos not in imprint_position_lst:
                imprint_position_lst.append(imp_pos)
        prod_tmpl_data.update({'imprint_position': imprint_position_lst})
        
            # print "prod_tmpl_data=================>>>>>>>>>>>>>>",prod_tmpl_data
        #LTM details will be updated if LTM Charge and LTM Quantity exists.
        #if row[28].value and row[29].value:
        #    prod_tmpl_data.update({'min_qty_ltm': row[28].value, 'ltm_charge': row[29].value})

        my_data.update({prod_tmpl_name: prod_tmpl_data})

    else:
        #Attribute Max Value/Run charge Available
        max_free_att = 0
        run_charge = 0
        for col in run_charge_cols:
            if row[col].value and isinstance(row[col].value, unicode) and row[col].value.strip() == 'FREE':
                max_free_att += 1
            elif row[col].value and isinstance(row[col].value, unicode) and row[col].value.strip() == 'N/A':
                continue
            elif row[col].value and not isinstance(row[col].value, unicode):
                run_charge = row[col].value
                break
                
        categ_id = sock.execute(dbname, uid, pwd, 'product.category', 'search', [('name','=',row[7].value.strip().title())])
        if not categ_id:
            categ_id = [sock.execute(dbname, uid, pwd, 'product.category', 'create', {'name': row[7].value.strip().title()})]
        my_data.update({
            prod_tmpl_name:{
                'categ_id': categ_id and categ_id[0] or False,
                'imprint_method': imprint_method,
                'imprint_position': imprint_position,
                'setup_charge': row[13].value,
                'run_charge': run_charge,
                'attribute_max_value': row[16].value,
                'max_free_attributes': max_free_att,
                #'ltm_charge': row[29].value,
                #'min_qty_ltm': row[28].value,
                'variant': [
                    {
                        'desc': row[6].value and row[6].value.strip(),
                        'sku': row[2].value and row[2].value.strip(),
                        'color': color,
                        'size': size,
                    }
                ] 
            }
        })
        
for prod_tmpl_name in my_data.keys():
    
    prod_tmpl_id = sock.execute(dbname, uid, pwd, 'product.template', 'search', [('name', '=', prod_tmpl_name), ('purchase_ok', '=', True)])
    if prod_tmpl_id:
        print "\nexisng product:",prod_tmpl_name,prod_tmpl_id

    tmpl_data = my_data[prod_tmpl_name]
    
    # print "\nltm_charge:",tmpl_data.get('ltm_charge', False),tmpl_data.get('min_qty_ltm', False)
    if not prod_tmpl_id:
    # if prod_tmpl_id and product_color and product_size:
        print '\n prod_tmpl_name-------------------',tmpl_data['categ_id']
        template_vals = {
            'name': prod_tmpl_name,
            'is_variant': False,
            'categ_id': tmpl_data['categ_id'],
            'type': 'product',
            'cost_method': 'average',
            'valuation': 'real_time',
            'list_price': 0,#Sale list_price
            'standard_price': 0,#Cost Price
            'sale_ok': False,
            'purchase_ok': True,
            'route_ids': [(6, 0, [6])],
            #'ltm_charge': tmpl_data.get('ltm_charge', False),
            #'min_qty_ltm': tmpl_data.get('min_qty_ltm', False),
        }

        #Import Color and Size attributes
        if '--color_size' in args:
            color = []
            size = []
            for variant in tmpl_data['variant']:
                color.extend(variant.get('color'))
                size.extend(variant.get('size'))
            template_vals.update({'attribute_line_ids': []})
            if color:
                template_vals['attribute_line_ids'].append(
                        (0, 0, {
                            'attribute_id': color_attribute_id, 
                            'value_ids': [(6, 0, list(set(color)))]
                        }))
            if size:
                template_vals['attribute_line_ids'].append(
                    (0, 0, {
                        'attribute_id': size_attribute_id, 
                        'value_ids': [(6, 0, list(set(size)))]
                    }))
        

        #Import Imprint Method, Imprint Color dimensions and Setup Charge
        if '--imprint_method_position' in args:
            product_dim_type_vals = []
            setup_charge_id = sock.execute(dbname, uid, pwd, 'product.charges', 'search', [('name', '=', 'Setup Charge')])
            imp_ids = []
            for imprint_method in tmpl_data.get('imprint_method',[]):
                imprint_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=' ,imprint_method)])
                if not imprint_id:
                    imprint_id = [sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'create', {'name': imprint_method.strip().title(), 'attribute_field_type': 'none'})]
                imp_ids.append(imprint_id[0])

                imp_meth = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'read', imprint_id[0], ['attribute_field_type'])
                product_dim_type_vals.append((0, 0, {'product_dimension_id2': imprint_id[0], 'attribute_field_type': imp_meth.get('attribute_field_type', 'none')}))
                imprint_color_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=' , imprint_method + ' Color')])
                if not imprint_color_id:
                    imprint_color_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=' , imprint_method + ' Imprint Color')])
                if imprint_color_id:
                    imp_meth_color = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'read', imprint_color_id[0], ['attribute_field_type'])
                    product_dimension_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', 
                        [('dimension_id','in',imprint_color_id)])
                    color_vals = {'product_dimension_id2': imprint_color_id[0], 'attribute_max_value': tmpl_data['attribute_max_value'] or 0,
                        'product_dimension_option_id': [(6, 0, product_dimension_option_id)], 'product_dimension_child_ids': [(6, 0, imprint_id)], 
                        'attribute_field_type': imp_meth_color.get('attribute_field_type', 'multiselection'), 'dimension_type': 'color'}

                    if '--setup_charge' in args and tmpl_data.get('setup_charge', False) and setup_charge_id:
                        color_vals.update({'attribute_to_charge_ids': [(0, 0, {'product_charges_id': setup_charge_id[0], 'amount_charge': tmpl_data.get('setup_charge', False), 
                            'per_dim_value': True, 'attribute_field_type': 'multiselection'})]})
                        # print "\nSet Up Charge :D"
                    product_dim_type_vals.append((0, 0, color_vals))
            # print "\nImprint Method Over :P"

            #Import Imprint Position and Run Charge
            product_imp_pos_vals = []
            run_charge_id = sock.execute(dbname, uid, pwd, 'product.charges', 'search', [('name', '=', 'Run Charge')])
            imprint_pos_dim_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'Imprint Position')])
            product_dimension_option_id = []

            if tmpl_data.get('imprint_method',[]):
                for imprint_position in tmpl_data.get('imprint_position',[]):
                    imp_pos_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', imprint_position.title()), 
                        ('dimension_id', 'in', imprint_pos_dim_id)])
                    if not imp_pos_id:
                        imp_pos_id = [sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': imprint_position.strip().title(), 'dimension_id': imprint_pos_dim_id[0]})]
                    product_dimension_option_id.append(imp_pos_id[0])
                # print "\ntmpl_data.get('imprint_method',[]):",imp_ids
                pos_value = {'product_dimension_id2': imprint_pos_dim_id[0], 'product_dimension_option_id': [(6, 0, product_dimension_option_id)], 
                    'product_dimension_child_ids': [(6, 0, imp_ids)], 'attribute_field_type': 'multiselection', 'dimension_type': 'side'}

                if '--run_charge' in args and tmpl_data.get('run_charge') and run_charge_id:
                    pos_value.update({'attribute_to_charge_ids': [(0, 0, {'product_charges_id': run_charge_id[0], 'amount_charge': tmpl_data.get('run_charge', 0.0), 
                        'attribute_field_type': 'multiselection', 'max_free_attributes': tmpl_data.get('max_free_attributes', 0), 'per_dim_value': True, 'per_qty': True})]})#'product_dimension_type_id':
                    # print "\nRun Charge :D"
                product_dim_type_vals.append((0, 0, pos_value))
                # print "\nImprint Position Over :P"

            template_vals.update({'product_dimension_type_ids': product_dim_type_vals})
        # print "\ntem valsd:::::::",template_vals
        print "\ntemplate vals:",template_vals
        sock.execute(dbname, uid, pwd, 'product.template', 'create', template_vals)
    else:
        #Update LTM charge and quantity
        if tmpl_data.get('ltm_charge') and tmpl_data.get('min_qty_ltm'):
            sock.execute(dbname, uid, pwd, 'product.template', 'write', prod_tmpl_id, {'ltm_charge': tmpl_data.get('ltm_charge'), 
                'min_qty_ltm': tmpl_data.get('min_qty_ltm')})
        #Update product Attributes
        product = sock.execute(dbname, uid, pwd, 'product.template', 'read', prod_tmpl_id[0], ['attribute_line_ids'])
        template_vals = {}
        color = []
        size = []
        color_exists = False
        color_vals = False
        size_exists = False
        size_vals = False
        for variant in tmpl_data['variant']:
            color.extend(variant.get('color'))#Colors from given sheet
            size.extend(variant.get('size'))
        attribute_line_ids = product.get('attribute_line_ids')
        attribute_datalist = sock.execute(dbname, uid, pwd, 'product.attribute.line', 'read', attribute_line_ids, ['attribute_id', 'value_ids'])
        for attribute_data in attribute_datalist:
            if color_attribute_id == attribute_data.get('attribute_id')[0]:
                color_exists = attribute_data.get('id')
                color_vals = attribute_data.get('value_ids')#Colors already there in system
            if size_attribute_id == attribute_data.get('attribute_id')[0]:
                size_exists = attribute_data.get('id')
                size_vals = attribute_data.get('value_ids')
        template_vals['attribute_line_ids'] = []
        if color:#Colors from given sheet
            if color_exists:
                colors_to_create = list(set(color) - set(color_vals))
                # print "\ncolors_to_create:",colors_to_create,prod_tmpl_name
                for c in colors_to_create:
                    sock.execute(dbname, uid, pwd, 'product.attribute.line', 'write', color_exists, {'value_ids': [(4, c)]})
                    attr_line = sock.execute(dbname, uid, pwd, 'product.template', 'read', prod_tmpl_id, ['attribute_line_ids'])
                    aline_to_write = []
                    for aline in attr_line[0].get('attribute_line_ids'):
                        aline_to_write.append([4, aline, False])
                    sock.execute(dbname, uid, pwd, 'product.template', 'write', prod_tmpl_id, {'attribute_line_ids': aline_to_write})
            else:
                template_vals['attribute_line_ids'].append(
                        (0, 0, {
                            'attribute_id': color_attribute_id,
                            'value_ids': [(6, 0, list(set(color)))]
                        }))
                # print "\nelsweeee:template_vals['attribute_line_ids']:",template_vals['attribute_line_ids'],prod_tmpl_id
                sock.execute(dbname, uid, pwd, 'product.template', 'write', prod_tmpl_id, {'attribute_line_ids': template_vals['attribute_line_ids']})
        template_vals['attribute_line_ids'] = []
        if size:
            if size_exists:
                size_to_create = list(set(size) - set(size_vals))

                for s in size_to_create:
                    sock.execute(dbname, uid, pwd, 'product.attribute.line', 'write', size_exists, {'value_ids': [(4, s)]})
                    attr_line = sock.execute(dbname, uid, pwd, 'product.template', 'read', prod_tmpl_id, ['attribute_line_ids'])
                    aline_to_write = []
                    for aline in attr_line[0].get('attribute_line_ids'):
                        aline_to_write.append([4, aline, False])
                    sock.execute(dbname, uid, pwd, 'product.template', 'write', prod_tmpl_id, {'attribute_line_ids': aline_to_write})
            else:
                template_vals['attribute_line_ids'].append(
                    (0, 0, {
                        'attribute_id': size_attribute_id, 
                        'value_ids': [(6, 0, list(set(size)))]
                }))
                # print "\nelsee sizxe: template: ",template_vals['attribute_line_ids'],prod_tmpl_name
                sock.execute(dbname, uid, pwd, 'product.template', 'write', prod_tmpl_id, {'attribute_line_ids': template_vals['attribute_line_ids']})
print "\nProduct Template Over :P :D"

#Update SKU on product

for prod_tmpl_name in my_data.keys():
    for variant in my_data[prod_tmpl_name]['variant']:
        color_id = variant.get('color')
        size_id = variant.get('size')
        product_id = False
        # color_id = sock.execute(dbname, uid, pwd, 'product.attribute.value', 'search', [('id','=',color[0])]) or False
        # size_id = sock.execute(dbname, uid, pwd, 'product.attribute.value', 'search', [('id','=',size[0])]) or False
        if color_id and size_id:
            product_id = sock.execute(dbname, uid, pwd, 'product.product', 'search', [('name','=',prod_tmpl_name.strip().title()), 
                ('attribute_value_ids', 'in', [color_id[0]]) , ('attribute_value_ids', 'in', [size_id[0]]), ('purchase_ok', '=', True) ])
        elif color_id and not size_id:
            product_id = sock.execute(dbname, uid, pwd, 'product.product', 'search', [('name','=',prod_tmpl_name.strip().title()), 
                ('attribute_value_ids', 'in', color_id), ('purchase_ok', '=', True)])
        elif not color_id and size_id:
            product_id = sock.execute(dbname, uid, pwd, 'product.product', 'search', [('name','=',prod_tmpl_name.strip().title()), 
                ('attribute_value_ids', 'in', size_id), ('purchase_ok', '=', True)])
        elif not color_id and not size_id:
            product_id = sock.execute(dbname, uid, pwd, 'product.product', 'search', [('name','=',prod_tmpl_name.strip().title()), ('purchase_ok', '=', True)])
            if len(product_id) > 1:
                product_id = False

        if product_id:
            sock.execute(dbname, uid, pwd, 'product.product', 'write', product_id,{'default_code': variant['sku'],'description': variant['desc'], 
                    'description_sale': variant['desc']})


# product_attribute_list = {}
# for product_id in sock.execute(dbname, uid, pwd, 'product.product', 'search', []):
#     pro_data = sock.execute(dbname, uid, pwd, 'product.product', 'read', product_id, ['attribute_value_ids', 'route_ids'])
#     if pro_data.has_key('attribute_value_ids') and pro_data.get('attribute_value_ids', False):
#         # sock.execute
#         product_attribute_list.update({pro_data.get('id'): pro_data.get('attribute_value_ids', [])})

# for prod_tmpl_name in my_data.keys():
#     for variant in my_data[prod_tmpl_name]['variant']:
#         attribute_value = variant['color']
#         attribute_value.extend(variant['size'])
#         for product_id, product_attribute in product_attribute_list.items():
#             actual_len = len(attribute_value)
#             output_len = len(list(set(attribute_value).intersection(product_attribute)))
#             if actual_len == output_len:
#                 sock.execute(dbname, uid, pwd, 'product.product', 'write', product_id, {'description': variant['desc'], 
#                     'description_sale': variant['desc']})

print "\nUpdated SKU :D :P"

print "\nEnd Time:", datetime.datetime.now()
