openerp.ob_po_to_so = function(instance){
  	instance.mail.RecordThread.include({
		render_value: function () {
			this._super();
			if(this.options.purchase_id){
				this.node.context['purchase_id'] = this.options.purchase_id
			}
			if(this.options.mo_id){
				this.node.context['mo_id'] = this.options.mo_id
			}
		}
	});
}