openerp.ob_sale_order_tracking = function(instance){
    instance.web.fields_view_get = function(args) {
        function postprocess(fvg) {
            var doc = $.parseXML(fvg.arch).documentElement;
            fvg.arch = instance.web.xml_to_json(doc, (doc.nodeName.toLowerCase() !== 'kanban'));
            if ('id' in fvg.fields) {
                // Special case for id's
                var id_field = fvg.fields['id'];
                id_field.original_type = id_field.type;
                id_field.type = 'id';
            };
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

        add_context = args.context.__context;
        if (add_context){
            add_context = add_context.__contexts[0];
        }else {
            add_context = args.model._context;
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

    instance.web.form.FieldStatus.include({

        on_click_stage: function (ev) {
            console.log('onclick stage....');
            var self = this;
            var $li = $(ev.currentTarget);
            var val;
            if (self.field.type == "many2one") {
                val = parseInt($li.data("id"), 10);
            }else {
                val = $li.data("id");
            }

            if (self.view.model == 'so.tracking'){
                var template_id = false;
                var sale_obj = new instance.web.DataSetSearch(self,'sale.order');
                var log_obj = new instance.web.DataSetSearch(self,'mail.message');
                var sale_order_line_obj = new instance.web.DataSetSearch(self,'sale.order.line');
                var allow ='';
                new instance.web.Model('so.tracking.stage').call('read', [self.get('value')]).done(function(result) {
                    if (result.user_allow_ids.length == 0){
                        allow = true;
                    } else {
                        for (i = 0; i < result.user_allow_ids.length; i++) {
                            if(self.session.uid == result.user_allow_ids[i]){
                                allow = true;
                            }
                        }
                    }
                    
                }).done(function(){
                    if (val != self.get('value')) {
                        new instance.web.Model('so.tracking.stage').call('read', [val]).done(function(result) {
                            console.log('',allow);
                            if (allow == true){
                                var sale_order_id = self.view.datarecord.sale_order_id[0];
                                var track_id = self.view.datarecord.id;

                                sale_obj.call("search_read", [[['id','=',sale_order_id]]],[]).then(function (data) {
                                    var context = {
                                          'track_id': track_id,
                                          'sale_order_id':sale_order_id,
                                          'active_model':'so.tracking.stage',
                                          'default_model':'sale.order',
                                          'so_stage_id':result.id,
                                          'stage_id':val,
                                    };
                                    var action = {
                                            name: 'Change Stage',
                                            type: 'ir.actions.act_window',
                                            res_model: 'sale.order.allow.wizard',
                                            view_mode: 'form',
                                            view_type: 'form',
                                            action_from: 'ob_sale_order_tracking.action_sale_stage_change_allow',
                                            views: [[false, 'form']],
                                            target: 'new',
                                            context: context,
                                    };

                                    self.do_action(action,{on_close: function(result){
                                        self.view.reload();
                                        // self.view.recursive_save().done(function() {
                                        //     var change = {};
                                        //     change[self.name] = val;
                                        //     console.log('sadassssssssssss',change);
                                        //     self.view.dataset.write(self.view.datarecord.id, change).done(function() {
                                        //         self.view.reload();
                                        //     });
                                        // });
                                    }});
                                });
                            }else {
                                return new instance.web.Dialog(this, {
                                    size: 'medium',
                                    title: "Access Denied !!",
                                    buttons: [{
                                        text: _t("Ok"),
                                        click: function() {
                                            this.parents('.modal').modal('hide');
                                        }
                                    }, ],
                                }, $('<div/>').text("You Have Not Permission To change this State. Please Contact Your Administrator..")).open();
                            }
                        });
                    }
                });
            }else {
                self.view.dataset.call('write', [self.view.datarecord.id, {'mail_sent':false}]);
                self.view.recursive_save().done(function() {
                    var change = {};
                    change[self.name] = val;
                    self.view.dataset.write(self.view.datarecord.id, change).done(function() {
                        self.view.reload();
                    });
                });
            }
        },
    });

    instance.web_kanban.KanbanView.include({

        on_record_moved: function(record, old_group, old_index, new_group, new_index){
            console.log('on record moved....');
            var self = this;
            var sale_obj = new instance.web.DataSetSearch(this,'sale.order');
            var sale_order_line_obj = new instance.web.DataSetSearch(this,'sale.order.line');
            var track_id = record.values.id['value'];

            if (record.view.dataset.model === 'so.tracking' && record.values.stage_id['value'] ){
                if (old_group != new_group) {
                    record.$el.find('[title]').tooltip('destroy');
                    var allow;
                    $(old_group.$el).add(new_group.$el).find('.oe_kanban_aggregates, .oe_kanban_group_length').hide();
                    new instance.web.Model('so.tracking.stage').call('read', [old_group.value]).done(function(result) {
                        if (result.user_allow_ids.length == 0){
                            allow = true;
                        } else {
                            for (i = 0; i < result.user_allow_ids.length; i++) {
                                if(self.session.uid == result.user_allow_ids[i]){
                                    allow = true;
                                }
                            }
                        }
                    }).done(function(){
                        new instance.web.Model('so.tracking.stage').call('read', [new_group.value]).done(function(result) {
                        if (result){
                            console.log('',allow);
                            console.log('',result);
                            if (allow == true){
                                if (result && record.values.sale_order_id['value'][0]){
                                    var sale_order_id = record.values.sale_order_id['value'][0];
                                    track_id = record.values.id['value'];
                                    sale_obj.call("search_read", [[['id','=',sale_order_id]]],[]).then(function (data) {
                                        if (data){
                                            var context = {
                                                  'track_id': track_id,
                                                  'sale_order_id':sale_order_id,
                                                  'active_model':'so.tracking.stage',
                                                  'default_model':'sale.order',
                                                  'so_stage_id':result.id,
                                            };
                                            var action = {
                                                    name: 'Change Stage',
                                                    type: 'ir.actions.act_window',
                                                    res_model: 'sale.order.allow.wizard',
                                                    view_mode: 'form',
                                                    view_type: 'form',
                                                    action_from: 'ob_sale_order_tracking.action_sale_stage_change_allow',
                                                    views: [[false, 'form']],
                                                    target: 'new',
                                                    context: context,
                                            };
                                            self.do_action(action,{on_close:function(){
                                                self.do_reload();
                                            }});
                                        }
                                    });
                                }else {
                                    self.dataset.call('write', [track_id, {'mail_sent':false}]);
                                    console.log("valuess of self >>>>>>",self);
                                    old_group.records.splice(old_index, 1);
                                    new_group.records.splice(new_index, 0, record);
                                    record.group = new_group;
                                    var data = {};
                                    data[self.group_by] = new_group.value;
                                    self.dataset.write(record.id, data, {}).done(function() {
                                        record.do_reload();
                                        new_group.do_save_sequences();
                                        if (new_group.state.folded) {
                                            new_group.do_action_toggle_fold();
                                            record.prependTo(new_group.$records.find('.oe_kanban_column_cards'));
                                        }
                                    }).fail(function(error, evt) {
                                        evt.preventDefault();
                                        alert(_t("An error has occured while moving the record to this group: ") + error.data.message);
                                        self.do_reload(); // TODO: use draggable + sortable in order to cancel the dragging when the rcp fails
                                    });
                                }
                            }else{
                                return new instance.web.Dialog(this, {
                                    size: 'medium',
                                    title: "Access Denied !!",
                                    buttons: [{
                                        text: _t("Ok"),
                                        click: function() {
                                            this.parents('.modal').modal('hide');
                                            self.do_reload();
                                        }
                                    }, ],
                                }, $('<div/>').text("You Have Not Permission To change this State. Please Contact Your Administrator..")).open();
                            }
                        }else{
                            return new instance.web.Dialog(this, {
                                    size: 'medium',
                                    title: "Access Denied !!",
                                    buttons: [{
                                        text: _t("Ok"),
                                        click: function() {
                                            this.parents('.modal').modal('hide');
                                            self.do_reload();
                                        }
                                    }, ],
                                }, $('<div/>').text("You Have Not Permission To change this State. Please Contact Your Administrator..")).open();
                        }
                    });


                    });
                    
                }else {
                    new_group.records.splice(old_index, 1);
                    new_group.records.splice(new_index, 0, record);
                    new_group.do_save_sequences();
                }
            }else {
                if (old_group === new_group) {
                    new_group.records.splice(old_index, 1);
                    new_group.records.splice(new_index, 0, record);
                    new_group.do_save_sequences();
                } else {

                    old_group.records.splice(old_index, 1);
                    new_group.records.splice(new_index, 0, record);
                    record.group = new_group;
                    var data = {};
                    data[self.group_by] = new_group.value;
                    self.dataset.write(record.id, data, {}).done(function() {
                        record.do_reload();
                        new_group.do_save_sequences();
                        if (new_group.state.folded) {
                            new_group.do_action_toggle_fold();
                            record.prependTo(new_group.$records.find('.oe_kanban_column_cards'));
                        }
                    }).fail(function(error, evt) {
                        evt.preventDefault();
                        alert(_t("An error has occured while moving the record to this group: ") + error.data.message);
                        self.do_reload(); // TODO: use draggable + sortable in order to cancel the dragging when the rcp fails
                    });
                }
            }
        }
    });
};
