from openerp.osv import fields, osv


class CalculateCharge(osv.osv):

    _name = "calculate.charge"

    def line_calculate_charges(self, cr, user, ids, product_id, line_no_of_pms_code, line_no_of_color, line_no_of_position, line_no_of_free_color, line_no_of_free_side, charges_data, imprint_method, qty, context=None):
        value = {}
        if product_id:
            is_there_dp = False
            product_obj = self.pool.get('product.product')
            product_rec = product_obj.browse(cr, user, [product_id], context=context)[0]
            for dimension_type in product_rec.product_tmpl_id.product_dimension_type_ids:
                if dimension_type.dimension_type == 'side':
                    if charges_data:
                        c_data = eval(charges_data)
                        option_id = c_data.get(dimension_type.product_dimension_id2.id,False)
                        if option_id and isinstance(option_id, int):
                            is_there_dp = True

            if is_there_dp:
                res = self.line_calculate_run_setup_charge_for_dropdown(cr, user, ids, product_rec, line_no_of_color, line_no_of_pms_code, line_no_of_free_side, charges_data, qty, option_id, context=context)
                positions = res.get('positions', 0)
                setup_charge = self.line_calculate_setup_charge(cr, user, ids, product_id, line_no_of_pms_code, line_no_of_color, positions, line_no_of_free_color, charges_data, imprint_method, qty, context=context)
                run_charge = res.get('run_charge', 0)
                value.update({'setup_charge': setup_charge, 'run_charge': run_charge})
            else:
                setup_charge = self.line_calculate_setup_charge(cr, user, ids, product_id, line_no_of_pms_code, line_no_of_color, line_no_of_position, line_no_of_free_color, charges_data, imprint_method, qty, context=context)
                run_charge = self.line_calculate_run_charge(cr, user, ids, product_id, line_no_of_pms_code, line_no_of_color, line_no_of_position, line_no_of_free_side, charges_data, imprint_method, qty, context=context)
                value.update({'setup_charge': setup_charge, 'run_charge': run_charge})
        return {'value': value}

    def line_calculate_setup_charge(self, cr, user, ids, product_id, line_no_of_pms_code, line_no_of_color, line_no_of_position, line_no_of_free_color, charges_data, imprint_method, qty, context=None):
        final_charge = 0
        if product_id:
            amt_charge = 0
            per_qty = False
            consider_all_color = True
            if charges_data:
                c_data = eval(charges_data)
            product_obj = self.pool.get('product.product')
            setup_charge_id = self.pool.get('ir.model.data').get_object_reference(cr, user, 'ob_product_variant', 'product_variant_setup_charge')[1]
            product_rec = product_obj.browse(cr, user, [product_id], context=context)[0]
            for dimension_type in product_rec.product_tmpl_id.product_dimension_type_ids:
                child_ids = [child.id for child in dimension_type.product_dimension_child_ids]
                if imprint_method in child_ids and dimension_type.dimension_type == 'color':
                    for charge in dimension_type.attribute_to_charge_ids:
                        if charge.product_charges_id.id == setup_charge_id:
                            dim_ids = [dim.id for dim in charge.product_dim_op_id]
                            if len(dim_ids) > 0:
                                consider_all_color = False
                                selected_ids = c_data.get(dimension_type.product_dimension_id2.id, [])
                                no_of_filtered_dim = len(list(set(dim_ids) & set(selected_ids)))
                            amt_charge = charge.amount_charge
                            per_qty = charge.per_qty
                            if qty:
                                for q_charge in charge.charges_id:
                                    if qty >= q_charge.from_qty and qty <= q_charge.to_qty:
                                        amt_charge = q_charge.charge_amount
            if line_no_of_position:
                if consider_all_color:
                    if line_no_of_position:
                        chargable_dim = (((line_no_of_pms_code + line_no_of_color) * line_no_of_position) - line_no_of_free_color)
                    else:
                        chargable_dim = ((line_no_of_pms_code + line_no_of_color) - line_no_of_free_color)
                else:
                    if line_no_of_position:
                        chargable_dim = (((line_no_of_pms_code + no_of_filtered_dim) * line_no_of_position) - line_no_of_free_color)
                    else:
                        chargable_dim = ((line_no_of_pms_code + no_of_filtered_dim) - line_no_of_free_color)
                if chargable_dim > 0:
                    if per_qty:
                        final_charge = chargable_dim * amt_charge * qty
                    else:
                        final_charge = chargable_dim * amt_charge
        return final_charge

    def line_calculate_run_charge(self, cr, user, ids, product_id, line_no_of_pms_code, line_no_of_color, line_no_of_position, line_no_of_free_color, charges_data, imprint_method, qty, context=None):
        final_charge = 0
        if product_id:
            data_list = []
            consider_all_color = True
            if charges_data:
                c_data = eval(charges_data)
            product_obj = self.pool.get('product.product')
            run_charge_id = self.pool.get('ir.model.data').get_object_reference(cr, user, 'ob_product_variant', 'product_variant_run_charge')[1]
            product_rec = product_obj.browse(cr, user, [product_id], context=context)[0]
            for dimension_type in product_rec.product_tmpl_id.product_dimension_type_ids:
                child_ids = [child.id for child in dimension_type.product_dimension_child_ids]
                if imprint_method in child_ids and dimension_type.dimension_type == 'side':
                    for charge in dimension_type.attribute_to_charge_ids:
                        if charge.product_charges_id.id == run_charge_id:
                            dim_ids = [dim.id for dim in charge.product_dim_op_id]
                            if dim_ids > 0:
                                consider_all_color = False
                            selected_ids = c_data.get(dimension_type.product_dimension_id2.id, [])
                            if not isinstance(selected_ids, list):
                                selected_ids = [selected_ids]
                            chargable_dim = len(list(set(dim_ids) & set(selected_ids)))
                            if not dim_ids:
                                chargable_dim = len(selected_ids)
                            amt_charge = charge.amount_charge
                            per_qty = charge.per_qty
                            if qty:
                                for q_charge in charge.charges_id:
                                    if qty >= q_charge.from_qty and qty <= q_charge.to_qty:
                                        amt_charge = q_charge.charge_amount

                            if consider_all_color:
                                if len(selected_ids) > 0:
                                    data_list.append([len(selected_ids), amt_charge, per_qty, charge.benefit])
                            else:
                                if chargable_dim > 0:
                                    data_list.append([chargable_dim, amt_charge, per_qty, charge.benefit])
            free_attr_considered = False
            for data_lst in data_list:
                if data_lst[3]:
                    free_attr_considered = True

            for data_lst in data_list:
                if data_lst[3]:
                    c_dim = (((line_no_of_pms_code + line_no_of_color) * data_lst[0]) - line_no_of_free_color)
                    if c_dim > 0:
                        if data_lst[2]:
                            final_charge += c_dim * data_lst[1] * qty
                        else:
                            final_charge += c_dim * data_lst[1]
                else:
                    if not free_attr_considered:
                        c_dim = (((line_no_of_pms_code + line_no_of_color) * data_lst[0]) - line_no_of_free_color)
                        if c_dim > 0:
                            if data_lst[2]:
                                final_charge += c_dim * data_lst[1] * qty
                            else:
                                final_charge += c_dim * data_lst[1]
                    else:
                        c_dim = ((line_no_of_pms_code + line_no_of_color) * data_lst[0])
                        if data_lst[2]:
                            final_charge += c_dim * data_lst[1] * qty
                        else:
                            final_charge += c_dim * data_lst[1]
        return final_charge

    def line_calculate_run_setup_charge_for_dropdown(self, cr, uid, ids, product_rec, line_no_of_color, line_no_of_pms_code, line_no_of_free_color, charges_data, qty, option_id, context=None):
        run_charge = 0
        positions = 1
        data_list = []
        for dimension_type in product_rec.product_tmpl_id.product_dimension_type_ids:
            if dimension_type.dimension_type == 'side' and dimension_type.product_dimension_id2.attribute_field_type == 'dropdown':
                consider_both_side = True
                for charge in dimension_type.attribute_to_charge_ids:
                    d_value_ids = [x.id for x in charge.product_dim_op_id]
                    amt_charge = charge.amount_charge
                    for r_charge in charge.charges_id:
                        if qty >= r_charge.from_qty and qty <= r_charge.to_qty:
                            amt_charge = r_charge.charge_amount
                    if option_id in d_value_ids:
                        if charge.is_both_side:
                            positions = 2
                        else:
                            consider_both_side = False
                            data_list.append([charge.benefit, amt_charge, charge.per_qty])
                    if consider_both_side:
                        data_list.append([charge.benefit, amt_charge, charge.per_qty])
                consider_free_attr = False
                for data_lst in data_list:
                    if data_lst[0]:
                        consider_free_attr = True
                for data_lst in data_list:
                    chargable_data = (line_no_of_color + line_no_of_pms_code)
                    if chargable_data > 0:
                        if data_lst[0]:
                            if data_lst[2]:
                                run_charge += (chargable_data - line_no_of_free_color) * data_lst[1] * qty
                            else:
                                run_charge += (chargable_data - line_no_of_free_color) * data_lst[1]
                        else:
                            if not consider_free_attr:
                                if data_lst[2]:
                                    run_charge += (chargable_data - line_no_of_free_color) * data_lst[1] * qty
                                else:
                                    run_charge += (chargable_data - line_no_of_free_color) * data_lst[1]
                            else:
                                if data_lst[2]:
                                    run_charge += chargable_data * data_lst[1] * qty
                                else:
                                    run_charge += chargable_data * data_lst[1]
        return {'positions': positions, 'run_charge': run_charge}