openerp.ob_account_check_writing_extend = function(instance){
    var _t = instance.web._t;
    instance.web.Sidebar.include({
        on_item_action_clicked: function(item) {
            var self = this;
            self.self1 = this._super;
            var ids = self.getParent().get_selected_ids();
            var func = new instance.web.Model("account.voucher").get_func("read");
            var ret = self.alive(func(ids,['line_dr_ids','number'])).then(function(res){
                var flag = false
                _.each(res, function(rec){
                    if(rec.line_dr_ids.length>10){
                        flag=true
                        new instance.web.Dialog(this, { title: _t("Warning"), size: 'medium',}, $("<div />").text(_t("Unable to print report due to more then 10 lines in the selected record(s). "))).open();
                        return;
                    }
                });
                if(!flag){
                    self.self1(item);
                }
            });
        }
    });
}
