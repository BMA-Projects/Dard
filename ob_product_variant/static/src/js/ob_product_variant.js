/*global openerp, _, $ */

openerp.ob_product_variant = function (instance) {

var QWeb = instance.web.qweb,
_t = instance.web._t;
	
instance.web.form.FieldMany2One.include({
    render_value: function(no_recurse) {
        var self = this;
        this._super.apply(this, arguments);
        var value = false;
        var product_tmpl_id = false;
        if (this.name == 'imprint_method' && this.get('value')!=false){
            value = this.display_value;
            $('.product_variant_child_attributes').each(function (index) {
                $(this).removeClass('oe_form_visible').addClass('oe_form_invisible');
                $(this).parent().prev().children().removeClass('oe_form_visible').addClass('oe_form_invisible');
                $(this).parent().parent('tr').children().removeClass('oe_form_visible').addClass('oe_form_invisible');
            });
            var product_id = _.keys(this.field_manager.fields.product_id.display_value)[0];
            var prod_data = new instance.web.DataSetSearch(this,'product.product', self.build_context(), [['id','=', product_id]]);
            prod_data.read_slice(['product_tmpl_id'], {}).then(function (records) {
                if (records.length) {
                    product_tmpl_id = records[0]['product_tmpl_id'][0];
                    var ds_data = new instance.web.DataSetSearch(this, 'product.dimension.type', self.build_context(), ['&','&',
                        ['product_dim_id', '=', product_tmpl_id],
                        ['attribute_field_type', '!=', 'none'],['attribute_field_type', '!=', 'false']]);
                    ds_data.read_slice([], {}).then(function (records) {
                        for (var rec in records) {
                            var name = records[rec]['product_dimension_id2'][1].toLowerCase();
                            var find = name.split(" ");
                            var field_name = find.join('_');
                            var int_obj = (field_name.match(/\d+/))
                            if (int_obj){
                            	var word = toWords(int_obj);
                            	var word = word.trim()
                            	var space_removed = word.split(' ').join('_')
                            	var whole_word = space_removed.split('-').join('_')
                            	var field_name = field_name.replace(int_obj, whole_word.trim())
                            }
                            var check_child_ids = _.contains(records[rec]['product_dimension_child_ids'], parseInt(_.keys(value)[0]));
                            
                            var field_name = field_name.split('-').join('_')
//                            var field_name = field_name.split('__').join('_')
                            if (check_child_ids) {
                                $('.' + field_name).each(function (index) {
                                    $(this).removeClass('oe_form_invisible').addClass('oe_form_visible');
                                    $(this).parent().prev().children().removeClass('oe_form_invisible').addClass('oe_form_visible');
                                    $(this).parent().parent('tr').children().removeClass('oe_form_invisible').addClass('oe_form_visible');
                                });
                            }
                        }
                    });
                 }
            });
        }
        if (this.name == 'imprint_method' && this.get('value')==false){
            $('.product_variant_child_attributes').each(function (index) {
                $(this).removeClass('oe_form_visible').addClass('oe_form_invisible');
                $(this).parent().prev().children().removeClass('oe_form_visible').addClass('oe_form_invisible');
                $(this).parent().parent('tr').children().removeClass('oe_form_visible').addClass('oe_form_invisible');
            });
        }
    }

});
instance.web.form.FieldMany2ManyTags.include({
    add_id: function(id) {
        var self = this;
        if(this.options.custom_field && (this.options.is_color || this.options.is_pms_code)){
        	var attr_max_val = this.field_manager.fields.line_attr_max_val.get('value');
        	if(attr_max_val!==0){
	        	var tot_color = 0;
	        	if(this.options.is_pms_code){
	        		tot_color = this.field_manager.fields.line_no_of_color.get('value') + this.get('value').length + 1;
	        	}
	        	else{
	        		tot_color = this.field_manager.fields.line_no_of_pms_code.get('value') + this.get('value').length + 1;
	        	}
	        	if(tot_color > attr_max_val){
	        		return new instance.web.Dialog(this, {
	                    size: 'medium',
	                    title: "Warning",
	                    buttons: [
	                        {text: _t("Ok"), click: function() { this.parents('.modal').modal('hide');}},
	                    ],
	                }, $('<div/>').text("Unable to process, You cannot select more then  " + attr_max_val + " option(s).")).open();
	        	}else{
	        		this._super(id);
	        	}
        	}else{
        		this._super(id);
        	}
        }else if(this.options.my_custom_field && this.options.is_color){
            var attr_max_val = this.field_manager.fields.line_attr_max_val.get('value');
            var attr_field_type = this.field_manager.fields.attribute_field_type.get('value');
            if(attr_field_type == 'dropdown'){
                attr_max_val = 1;
            }
            if(attr_max_val!==0){
                var tot_color = 0;
                tot_color = this.get('value').length + 1;
                if(tot_color > attr_max_val){
                    return new instance.web.Dialog(this, {
                        size: 'medium',
                        title: "Warning",
                        buttons: [
                            {text: _t("Ok"), click: function() { this.parents('.modal').modal('hide');}},
                        ],
                    }, $('<div/>').text("Unable to process, You cannot select more then  " + attr_max_val + " option(s).")).open();
                }else{
                    this._super(id);
                }
            }else{
                this._super(id);
            }
        }else{
        	this._super(id);
        }
    },
});




};
