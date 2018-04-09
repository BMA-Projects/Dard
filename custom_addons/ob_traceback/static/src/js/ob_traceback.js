/*---------------------------------------------------------
 * OB Traceback suppress errors in ERP
 *---------------------------------------------------------*/
openerp.ob_traceback = function(instance) {
    var QWeb = instance.web.qweb,
    _t = instance.web._t;
    
    instance.web.CrashManager.include({
        show_warning: function(error) {
            if (!this.active) {
                return;
            }
            cur_model = false;
            if (self.action)
                cur_model = self.action.res_model;
            this.custom_error_handles(error, cur_model);
            
            if (error.data.fault_code){
                error.data.fault_code = error.data.fault_code.replace(/odoo/ig, "OfficeBrainBMA");
            }
            new instance.web.Dialog(this, {
                size: 'medium',
                title: "OfficeBrainBMA " + (_.str.capitalize(error.type) || "Warning"),
                buttons: [
                    {text: _t("Ok"), click: function() { this.parents('.modal').modal('hide'); }}
                ],
            }, $('<div>' + QWeb.render('CrashManager.warning', {error: error}) + '</div>')).open();
        },
        show_error: function(error) {
            var self = this;
            if (!self.active) {
                return;
            }
            cur_model = false;
            if (self.action)
                cur_model = self.action.res_model;
            self.custom_error_handles(error, cur_model);
            error.message = _t("The application has encountered an unknown error.");
            error.data.debug = _t("It doesn't appear to have affected your data,\nbut our technical staff have been automatically notified and \nwill be looking into this with the utmost urgency.");
            var buttons = {};
            
            var dialog = new instance.web.Dialog(self, {
                title: "OfficeBrainBMA " + _.str.capitalize(error.type),
                width: '545px',
                height: '250px',
                position: ['center',220],
                buttons: [{ text: "Ok", click: function() { this.parents('.modal').modal('hide');}}],
            }).open();
            
            dialog.$el.html(QWeb.render('CrashManager.error', {session: instance.session, error: error}));
        },
        custom_error_handles: function(error, cur_model){
            var self = this;
            var model = new instance.web.Model("res.traceback");
            var message = error.data.fault_code || error.message;
            
            err_code = error.code || 300;
            cur_model = (err_code == 300) ? null : cur_model;
            
            message = message.replace(/odoo/ig, "OfficeBrainBMA");
            error_msg = error.data.name + ":" + error.data.arguments[0]
            $.getJSON('http://jsonip.com/?callback=?', function(r){ 
                var vals = {
                        'code': err_code,
                        'message': message,
                        'model': cur_model,
                        'error_msg':error_msg,
                        'debug': error.data.debug,
                        'location': window.location.href,
                        'trace_type': error.type,
                        'client_ip': r.ip
                    }
                $.when(model.call("create", [vals]).done(function(result) {})); 
            });
        },
    });

};
