openerp.ob_purchase_order_tracking = function(instance){
   instance.web.fields_view_get = function(args) {
    function postprocess(fvg) {
        var doc = $.parseXML(fvg.arch).documentElement;
        fvg.arch = instance.web.xml_to_json(doc, (doc.nodeName.toLowerCase() !== 'kanban'));
        console.log("values >>>>>>>>>>>>>>>>>>>>>>>>>>>>>.fields",fvg,args);
        if ('id' in fvg.fields) {
            // Special case for id's
            var id_field = fvg.fields['id'];
            id_field.original_type = id_field.type;
            id_field.type = 'id';
        }
        _.each(fvg.fields, function(field) {
            _.each(field.views || {}, function(view) {
                postprocess(view);
            });
        });
        return fvg;
    }
    args = _.defaults(args, {
        toolbar: false,
    });
    var model = args.model;
    if (typeof model === 'string') {
        model = new instance.web.Model(args.model, args.context);
    }
    
   // console.log("ARGS >>>>>>>>>>>>>>>>",model);
    add_context = args.context.__context
    console.log("ARGS >>>>>>>>>>>>>>>>",add_context);
    if (add_context){
        add_context = add_context.__contexts[0];
    }else {
        add_context = args.model._context
    }
    return args.model.call('fields_view_get', {
        view_id: args.view_id,
        view_type: args.view_type,
        context: add_context,
        toolbar: args.toolbar
    }).then(function(fvg) {
        return postprocess(fvg);
    });
};

	instance.mail.RecordThread.include({
		render_value: function () {
			this._super();
			// if(this.options.from_po_msg){
				
			// 	this.node.context['po_flag'] = true
			// }
			//if(this.options.custom_flag){
			//	this.node.context['flag_post_message'] = true
			//}
                        if(this.options.custom_flag && this.node.context){
                               this.node.context['flag_post_message'] = true;
                        }
			if(this.options.from_so_msg){
				this.node.context['so_flag'] = true
			}
			if(this.options.sale_id){
				this.node.context['sale_id'] = this.options.sale_id
			}
		}
	});
}
