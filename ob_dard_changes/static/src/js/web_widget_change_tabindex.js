/*global openerp, _, $ */

openerp.ob_dard_changes = function (instance) {
    var QWeb = instance.web.qweb,
    _t  = instance.web._t,
    _lt = instance.web._lt;
    
   instance.web.form.FieldMany2One.include({
	   initialize_content: function() {
		   console.log('call on float field focusout');
	        if (!this.get("effective_readonly"))
	            this.render_editable();
	        $("input[name='price_unit']").on('focusout',function() {
	        	$( "input[name='imprint_method']" ).focus();
	        });
	    },
   })
    
   instance.web.form.FieldMany2ManyTags.include({   
        initialize_content: function() {
        	this._super();
    		self.$text = this.$("textarea");
            self.$text.focusout(function() {
            	$('.oe_form_visible:last').focusout(function(){
              	  $( "input[name='setup_charge']" ).focus();
                  });
            });
        }
    });
   
    instance.web.form.widgets = instance.web.form.widgets.extend({
        'change_float_tabindex' : 'instance.web.form.changetabindex',
    });
    
};
