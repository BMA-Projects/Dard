/*---------------------------------------------------------
 * OpenERP so_partners (module)
 *---------------------------------------------------------*/
openerp.so_partners = function(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    instance.web.form.FieldChar.include({
        render_value : function() {
            this._super.apply(this, arguments);
            if (this.name == 'asi_number' || this.name == 'pppc_number' || this.name == 'sage_number') {
                if (!this.get("effective_readonly")) {
                    this.$el.show(); this.$label.show();
                } else {
                    if (!this.get('value')) { this.$el.hide(); this.$label.hide();}
                    else{ this.$el.show(); this.$label.show(); }
                }
            }
        }
    });
}
