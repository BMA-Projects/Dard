/*global openerp, _, $ */

openerp.web_m2x_options = function (instance) {
    "use strict";

    var QWeb = instance.web.qweb,
        _t  = instance.web._t,
        _lt = instance.web._lt;
        
    /* Extended to update field Options*/
    
    instance.web.form.CompletionFieldMixin = {
        init: function() {
            this.limit = 7;
            this.orderer = new instance.web.DropMisordered();
        },
        get_search_result: function(search_val) {
            var self = this;

            var dataset = new instance.web.DataSet(this, this.field.relation, self.build_context());
            this.last_query = search_val;
            var exclusion_domain = [], ids_blacklist = this.get_search_blacklist();
            if (!_(ids_blacklist).isEmpty()) {
                exclusion_domain.push(['id', 'not in', ids_blacklist]);
            }

            return this.orderer.add(dataset.name_search(
                    search_val, new instance.web.CompoundDomain(self.build_domain(), exclusion_domain),
                    'ilike', this.limit + 1, self.build_context())).then(function(data) {
                self.last_search = data;
                // possible selections for the m2o
                var values = _.map(data, function(x) {
                    x[1] = x[1].split("\n")[0];
                    return {
                        label: _.str.escapeHTML(x[1]),
                        value: x[1],
                        name: x[1],
                        id: x[0],
                    };
                });

                // search more... if more results that max
                if (values.length > self.limit) {
                    values = values.slice(0, self.limit);
                    values.push({
                        label: _t("Search More..."),
                        action: function() {
                            dataset.name_search(search_val, self.build_domain(), 'ilike', 160).done(function(data) {
                                self._search_create_popup("search", data);
                            });
                        },
                        classname: 'oe_m2o_dropdown_option'
                    });
                }
                // quick create
                var raw_result = _(data.result).map(function(x) {return x[1];});
                if (search_val.length > 0 && !_.include(raw_result, search_val) &&
                    ! (self.options && (self.options.no_create || self.options.no_quick_create))) {
                    values.push({
                        label: _.str.sprintf(_t('Create "<strong>%s</strong>"'),
                            $('<span />').text(search_val).html()),
                        action: function() {
                            self._quick_create(search_val);
                        },
                        classname: 'oe_m2o_dropdown_option'
                    });
                }
                // create...
                if (!(self.options && (self.options.no_create || self.options.no_create_edit))){
                    values.push({
                        label: _t("Create and Edit..."),
                        action: function() {
                            self._search_create_popup("form", undefined, self._create_context(search_val));
                        },
                        classname: 'oe_m2o_dropdown_option'
                    });
                }
                else if (values.length == 0)
                    values.push({
                        label: _t("No results to show..."),
                        action: function() {},
                        classname: 'oe_m2o_dropdown_option'
                    });

                return values;
            });
        },
        get_search_blacklist: function() {
            return [];
        },
        _quick_create: function(name) {
            var self = this;
            var slow_create = function () {
                self._search_create_popup("form", undefined, self._create_context(name));
            };
            if (self.options.quick_create === undefined || self.options.quick_create) {
                new instance.web.DataSet(this, this.field.relation, self.build_context())
                    .name_create(name).done(function(data) {
                        if (!self.get('effective_readonly'))
                            self.add_id(data[0]);
                    }).fail(function(error, event) {
                        event.preventDefault();
                        slow_create();
                    });
            } else
                slow_create();
        },
        // all search/create popup handling
        _search_create_popup: function(view, ids, context) {
            var self = this;
            var pop = new instance.web.form.SelectCreatePopup(this);
            console.dir(pop);
            pop.select_element(
                self.field.relation,
                {
                    title: (view === 'search' ? _t("Search: ") : _t("Create: ")) + this.string,
                    initial_ids: ids ? _.map(ids, function(x) {return x[0];}) : undefined,
                    initial_view: view,
                    disable_multiple_selection: true,
                    // Update fields options
                    name: this.name,
                    create: this.options.create,
                    create_edit: this.options.create_edit
                },
                self.build_domain(),
                new instance.web.CompoundContext(self.build_context(), context || {})
            );
            pop.on("elements_selected", self, function(element_ids) {
                self.add_id(element_ids[0]);
                self.focus();
            });
        },
        add_id: function(id) {},
        _create_context: function(name) {
            var tmp = {};
            var field = (this.options || {}).create_name_field;
            if (field === undefined)
                field = "name";
            if (field !== false && name && (this.options || {}).quick_create !== false)
                tmp["default_" + field] = name;
            return tmp;
        },
    };

    /* Extended for Many2one fields */
    
    instance.web.form.FieldMany2One.include({
        // Used to show/hide dialog
        show_error_displayer: function () {
            if ((typeof this.options.m2o_dialog === 'undefined' && this.can_create) ||
                this.options.m2o_dialog) {
                new instance.web.form.M2ODialog(this).open();
            }
        },
        
        // Call this method to search using a string.
        
        get_search_result: function (search_val) {
            var def = $.Deferred();
            var self = this;
            // add options limit used to change number of selections record
            // returned.

            if (typeof this.options.limit === 'number') {
                this.limit = this.options.limit;
            }

            var dataset = new instance.web.DataSet(this, this.field.relation,
                                                   self.build_context());
            var blacklist = this.get_search_blacklist();
            this.last_query = search_val;
        
            var search_result = this.orderer.add(dataset.name_search(
                search_val,
                new instance.web.CompoundDomain(
                    self.build_domain(), [["id", "not in", blacklist]]),
                'ilike', this.limit + 1,
                self.build_context()));
            
            var create_rights;
            if (typeof this.options.create === "undefined" ||
                typeof this.options.create_edit === "undefined") {
                create_rights = new instance.web.Model(this.field.relation).call(
                    "check_access_rights", ["create", false]);
            }
            
            $.when(search_result, create_rights).then(function (_data, _can_create) {
                var data = _data;
                
                var can_create = _can_create || null;
                self.can_create = can_create;  // for ``.show_error_displayer()``
                self.last_search = data;
                // possible selections for the m2o
                var values = _.map(data, function (x) {
                    if (x[1] == undefined){
                        data[1] = data[1].split("\n")[0];
                        return {
                            label: _.str.escapeHTML(data[1]),
                            value: data[1],
                            name: data[1],
                            id: data[1],
                        };
                      }else {
                        x[1] = x[1].split("\n")[0];
                        return {
                            label: _.str.escapeHTML(x[1]),
                            value: x[1],
                            name: x[1],
                            id: x[0],
                        };
                        }
                    });
                   

                // search more... if more results that max

                if (values.length > self.limit) {
                    values = values.slice(0, self.limit);
                    values.push({
                        label: _t("Search More..."),
                        action: function () {
                            dataset.name_search(
                                search_val, self.build_domain(),
                                'ilike', 160).done(function (data) {
                                    self._search_create_popup("search", data);
                                });
                        },
                        classname: 'oe_m2o_dropdown_option'
                    });
                }

                // quick create

                var raw_result = _(data.result).map(function (x) {
                    return x[1];
                });

                if ((typeof self.options.create === 'undefined' && can_create) ||
                    self.options.create) {

                    if (search_val.length > 0 &&
                        !_.include(raw_result, search_val)) {

                        values.push({
                            label: _.str.sprintf(
                                _t('Create "<strong>%s</strong>"'),
                                $('<span />').text(search_val).html()),
                            action: function () {
                                self._quick_create(search_val);
                            },
                            classname: 'oe_m2o_dropdown_option'
                        });
                    }
                }

                // create and edit...

                if ((typeof self.options.create_edit === 'undefined' && can_create) ||
                    self.options.create_edit) {

                    values.push({
                        label: _t("Create and Edit..."),
                        action: function () {
                            self._search_create_popup(
                                "form", undefined,
                                self._create_context(search_val));
                        },
                        classname: 'oe_m2o_dropdown_option'
                    });
                }

                def.resolve(values);
            });

            return def;
        }
    });
    
    /* Extended for Many2many fields */

    instance.web.form.FieldMany2ManyTags.include({

        show_error_displayer: function () {
            if ((typeof this.options.m2o_dialog === 'undefined' && this.can_create) ||
                this.options.m2o_dialog) {
                new instance.web.form.M2ODialog(this).open();
            }
        },

        /**
        * Call this method to search using a string.
        */

        get_search_result: function (search_val) {
            var def = $.Deferred();
            var self = this;

            // add options limit used to change number of selections record
            // returned.

            if (typeof this.options.limit === 'number') {
                this.limit = this.options.limit;
            }
            var dataset = new instance.web.DataSet(this, this.field.relation,
                                                   self.build_context());
            var blacklist = this.get_search_blacklist();
            this.last_query = search_val;

            var search_result = this.orderer.add(dataset.name_search(
                search_val,
                new instance.web.CompoundDomain(
                    self.build_domain(), [["id", "not in", blacklist]]),
                'ilike', this.limit + 1,
                self.build_context()));

            var create_rights;
            if (typeof this.options.create === "undefined" ||
                typeof this.options.create_edit === "undefined") {
                create_rights = new instance.web.Model(this.field.relation).call(
                    "check_access_rights", ["create", false]);
            }
            $.when(search_result, create_rights).then(function (_data, _can_create) {
                var data = _data;

                var can_create = _can_create || null;
                self.can_create = can_create;  // for ``.show_error_displayer()``
                self.last_search = data;
                // possible selections for the m2o
                var values = _.map(data, function (x) {
                    if (x[1] == undefined){
                        data[1] = data[1].split("\n")[0];
                        return {
                            label: _.str.escapeHTML(data[1]),
                            value: data[1],
                            name: data[1],
                            id: data[1],
                        };
                      }else {
                        x[1] = x[1].split("\n")[0];
                        return {
                            label: _.str.escapeHTML(x[1]),
                            value: x[1],
                            name: x[1],
                            id: x[0],
                        };
                        }
                    });


                // search more... if more results that max
                if (values.length > self.limit) {
                    values = values.slice(0, self.limit);
                    values.push({
                        label: _t("Search More..."),
                        action: function () {
                            dataset.name_search(
                                search_val, self.build_domain(),
                                'ilike', 160).done(function (data) {
                                    self._search_create_popup("search", data);
                                });
                        },
                        classname: 'oe_m2o_dropdown_option'
                    });
                }

                // quick create

                var raw_result = _(data.result).map(function (x) {
                    return x[1];
                });

                if ((typeof self.options.create === 'undefined' && can_create) ||
                    self.options.create) {

                    if (search_val.length > 0 &&
                        !_.include(raw_result, search_val)) {

                        values.push({
                            label: _.str.sprintf(
                                _t('Create "<strong>%s</strong>"'),
                                $('<span />').text(search_val).html()),
                            action: function () {
                                self._quick_create(search_val);
                            },
                            classname: 'oe_m2o_dropdown_option'
                        });
                    }
                }

                // create and edit...

                if ((typeof self.options.create_edit === 'undefined' && can_create) ||
                    self.options.create_edit) {

                    values.push({
                        label: _t("Create and Edit..."),
                        action: function () {
                            self._search_create_popup(
                                "form", undefined,
                                self._create_context(search_val));
                        },
                        classname: 'oe_m2o_dropdown_option'
                    });
                }

                def.resolve(values);
            });

            return def;
        }
    });
    
    /* To hide Create button from SelectCreatePopup from many2one and many2many fields*/
    
    instance.web.form.SelectCreatePopup.include({
        setup_search_view: function(search_defaults) {
            var self = this;
            if (this.searchview) {
                this.searchview.destroy();
            }
            if (this.searchview_drawer) {
                this.searchview_drawer.destroy();
            }
            this.searchview = new instance.web.SearchView(this,
                    this.dataset, false,  search_defaults);
            this.searchview_drawer = new instance.web.SearchViewDrawer(this, this.searchview);
            this.searchview.on('search_data', self, function(domains, contexts, groupbys) {
                if (self.initial_ids) {
                    self.do_search(domains.concat([[["id", "in", self.initial_ids]], self.domain]),
                        contexts.concat(self.context), groupbys);
                    self.initial_ids = undefined;
                } else {
                    self.do_search(domains.concat([self.domain]), contexts.concat(self.context), groupbys);
                }
            });
            this.searchview.on("search_view_loaded", self, function() {
                self.view_list = new instance.web.form.SelectCreateListView(self,
                        self.dataset, false,
                        _.extend({'deletable': false,
                            'selectable': !self.options.disable_multiple_selection,
                            'import_enabled': false,
                            '$buttons': self.$buttonpane,
                            'disable_editable_mode': true,
                            '$pager': self.$('.oe_popup_list_pager'),
                        }, self.options.list_view_options || {}));
                self.view_list.on('edit:before', self, function (e) {
                    e.cancel = true;
                });
                self.view_list.popup = self;
                self.view_list.appendTo($(".oe_popup_list", self.$el)).then(function() {
                    self.view_list.do_show();
                }).then(function() {
                    self.searchview.do_search();
                });
                
                self.view_list.on("list_view_loaded", self, function() {
                    self.$buttonpane.html(QWeb.render("SelectCreatePopup.search.buttons", {widget:self}));
                    var $cbutton = self.$buttonpane.find(".oe_selectcreatepopup-search-close");
                    $cbutton.click(function() {
                        self.destroy();
                    });
                    var $sbutton = self.$buttonpane.find(".oe_selectcreatepopup-search-select");
                    $sbutton.click(function() {
                        self.select_elements(self.selected_ids);
                        self.destroy();
                    });
                    // To hide Create button if field don't have create options
                    if (typeof this.options.create === 'undefined' && typeof this.options.create_edit === 'undefined' || this.options.create || this.options.create_edit) {
                        $cbutton = self.$buttonpane.find(".oe_selectcreatepopup-search-create");
                        $cbutton.click(function() {
                            self.new_object();
                        });
                    } else {
                        $cbutton = self.$buttonpane.find(".oe_selectcreatepopup-search-close");
                        console.log('---------------$cbutton---------------',$cbutton);
                        this.$buttonpane[0].innerHTML = '<a class="oe_selectcreatepopup-search-close oe_bold oe_form_button_cancel" href="javascript:void(0)">Cancel</a>';
                        this.$buttonpane.click(function() {
                            self.destroy();
                        });
                        console.log('--------element---------------',this.$buttonpane[0].innerHTML);
                        }
                        
                });
                    
            });
            this.searchview.appendTo(this.$(".oe_popup_search"));
        },
    });
    
};

