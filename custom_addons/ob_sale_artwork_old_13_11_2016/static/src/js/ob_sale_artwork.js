var attach = {};

function readerHandler(e2) {
    // attach['file_data'] = e2.target.result.split(',')[1];
    attach['file_data'] = e2.target.result.split(',')[1].replace(/^data:image\/(png|jpg|jpeg|bmp|gif|png|jfif|tif|tiff|rif|riff|ai|eps|pdf);base64,/, "");
}

var state_dict = {
    'confirmed': 'Approved',
    'semi_confirmed': 'Approved with Changes',
    'cancel': 'Cancel'
};

function handleFileSelect(e1) {

    var fileobj = $('#attach')[0].files[0];
    var fr = new FileReader();
    fr.onload = readerHandler;
    fr.readAsDataURL(fileobj);
}

function PreviewText() {


    var oFReader = new FileReader();

    attach['filename'] = document.getElementById("uploadText").files[0] ? document.getElementById("uploadText").files[0].name : null;

    oFReader.readAsDataURL(document.getElementById("uploadText").files[0]);
    oFReader.onload = function(oFREvent) {

        document.getElementById("uploadTextValue").value = oFREvent.target.result;
        attach['file_data'] = oFREvent.target.result;
    };
};

window.onload = function() {
    var x = document.getElementById("attach");
    if (x) {
        x.addEventListener('change', handleFileSelect, false);
    }
};

openerp.ob_sale_artwork = function(instance) {
    var QWeb = instance.web.qweb,
        _t = instance.web._t;
    instance.web.form.FieldBinaryImage.include({
        render_value: function() {
            var self = this;
            this._super.apply(this, arguments);
            var id = this.view.datarecord.id;
            if (self.options.custom_img && id && $.type(id) == 'number') {
                new instance.web.Model(this.view.dataset.model).call('read', [id]).done(function(result) {
                    url = result.art_image_local_name;
                    var $img = $(QWeb.render("FieldBinaryImage-img", {
                        widget: self,
                        url: url
                    }));
                    self.$el.find('> img').remove();
                    self.$el.prepend($img);
                    if (self.get("effective_readonly")) {
                        if (!$('.download_img').length > 0)
                            self.$el.after("<span class='download_img' style='" + 'display: inline-block; margin: 40px 0 0 0; text-decoration: underline ;' + "'><a href='" + url + "' download>Download</a></span>");
                    		
                    }
                    
                    $img.load(function() {
                        $img.css("width", "90px").css("height", "90px");
                    });
                    $img.on('error', function() {
                        $img.attr('src', self.placeholder);
                    });
                });
            }
        },
    });

    var form_data = false;

    instance.web.View.include({
        load_view: function(context) {
            var self = this;
            $('.art_semi_confirm').unbind('click').click(function() {
                self.dialog_data = form_data;
                if (['confirmed', 'semi_confirmed', 'cancel'].indexOf(self.dialog_data.state) < 0) {
                    return self.image_semi_apporval('semi_confirmed');
                } else {
                    return self.check_approved_artwork();
                }
            });
            $('.art_cancle').unbind('click').click(function() {
                self.dialog_data = form_data;
                if (['confirmed', 'semi_confirmed', 'cancel'].indexOf(self.dialog_data.state) < 0) {
                    return self.image_semi_apporval('cancel');
                } else {
                    return self.check_approved_artwork();
                }
            });
            $('.art_confirm').unbind('click').click(function() {
                self.dialog_data = form_data;
                if (['confirmed', 'semi_confirmed', 'cancel'].indexOf(self.dialog_data.state) < 0) {
                    return self.image_appoval();
                } else {
                    return self.check_approved_artwork();
                }
            });
            return self._super(context);
        },

        check_approved_artwork: function() {
            var self = this;
            return new instance.web.Dialog(this, {
                size: 'medium',
                title: "Warning",
                close: function(event, ui) {
                    this.parents('.modal').dialog('destroy').remove();
                },
                buttons: [{
                    text: _t("Ok"),
                    click: function() {
                        this.parents('.modal').modal('hide');
                    }
                }, ],
            }, $('<div/>').text("You have already verified this virtual with " + state_dict[self.dialog_data.state] + ".")).open();
        },

        image_appoval: function() {
            var self = this;
            return new instance.web.Dialog(this, {
                size: 'medium',
                title: "Art Approval",
                buttons: [{
                        text: _t("Ok"),
                        click: function() {
                            var res_id = self.dialog_data.id;
                            var db = self.session.db;

                            var cmmnt = $('#cmnt').val();
                            var uname = $('#uname').val();
                            var dic_new1 = {};
                            if (!uname) {
                                return new instance.web.Dialog(this, {
                                    size: 'medium',
                                    title: "Warning",
                                    buttons: [{
                                        text: _t("Ok"),
                                        click: function() {
                                            this.parents('.modal').modal('hide');
                                        }
                                    }, ],
                                }, $('<div/>').text("Please Enter UserName.")).open();
                            }
                            dic_new1['cmnt'] = String(cmmnt);
                            dic_new1['uname'] = String(uname);
                            dic_new1['res_id'] = String(res_id);
                            dic_new1['db'] = String(db);
                            dic_new1['virtual_state'] = 'confirmed';
                            self.rpc('/Artapprove/submit', {
                                'data': dic_new1
                            }).then(function() {
                                console.log('call');
                                self.do_warn(_t("Art Approval"), ("You have successfully verified the virtual."));
                            });
                            this.parents('.modal').modal('hide');

                        }
                    },

                    {
                        text: _t("Cancel"),
                        click: function() {
                            this.parents('.modal').modal('hide');
                        }
                    }
                ],
            }, $('<div>' + QWeb.render('Approve.Art') + '</div>')).open();

        },

        image_semi_apporval: function(state) {
            var self = this;
            return new instance.web.Dialog(this, {
                size: 'medium',
                title: "Art Approval",
                buttons: [{
                        text: _t("Ok"),
                        click: function() {
                            var res_id = self.dialog_data.id;
                            var db = self.session.db;
                            var cmmnt = $('#cmnt').val();
                            var uname = $('#uname').val();
                            var dic_new1 = {};

                            if (attach['file_data']) {
                                attach['file_data'] = attach['file_data'].replace(/^data:image\/(png|jpg|jpeg|bmp|gif|png|jfif|tif|tiff|rif|riff|ai|eps|pdf);base64,/, "");
                            }

                            dic_new1['cmnt'] = String(cmmnt);
                            dic_new1['uname'] = String(uname);
                            dic_new1['res_id'] = String(res_id);
                            dic_new1['db'] = String(db);
                            dic_new1['attach'] = attach['file_data'];
                            dic_new1['name'] = attach['filename'];
                            dic_new1['virtual_state'] = state;


                            if (!uname) {
                                return new instance.web.Dialog(this, {
                                    size: 'medium',
                                    title: "Warning",
                                    buttons: [{
                                        text: _t("Ok"),
                                        click: function() {
                                            this.parents('.modal').modal('hide');
                                        }
                                    }, ],
                                }, $('<div/>').text("Please Enter UserName.")).open();
                            }

                            self.rpc('/Artapprove/submit', {
                                'data': dic_new1
                            }).then(function() {
                                self.do_warn(_t("Art Approval"), ("You have successfully verified the virtual."));
                            });
                            this.parents('.modal').modal('hide');

                        }
                    },

                    {
                        text: _t("Cancel"),
                        click: function() {
                            this.parents('.modal').modal('hide');
                        }
                    }
                ],
            }, $('<div>' + QWeb.render('ChangeApprove.Art') + '</div>')).open();


        },
    });

    instance.web.FormView.include({
        load_record: function(record) {
            var self = this;
            form_data = record;
            return $.when(self._super(record));
        },



    });
    instance.web.form.FieldBinaryFile.include({
        render_value: function() {
            var self = this;
            this._super.apply(this, arguments);

            var virtual_file = self.view.datarecord[self.node.attrs.filename];
            if ( self.view.datarecord.virtual_file_name_url ){
            	url = self.view.datarecord.virtual_file_name_url;
            	$('#myImg').attr('src',url);
            }
            if (this.get("effective_readonly")) {
                var id = this.view.datarecord.id;
                if (self.options.custom_img && id) {
                    url = self.view.datarecord.virtual_file_name_url;
                    if (!url) {
                        url = self.view.datarecord.file_url;
                    }
                    if (url) {
                        var show_value = _t("Download");
                        $('.virtual_file_name').remove();
                        if (self.view.datarecord[self.node.attrs.filename]) {
                            self.$el.find('a').replaceWith("<a class=virtual_file href='" + url + "' style='text-decoration: underline ;' download>" + show_value + "</a><span class=virtual_file_name>" + (self.view.datarecord[self.node.attrs.filename] || '') + "</span>");
                        } else {
                            self.$el.find('a').replaceWith("<a class=virtual_file style='text-decoration: underline ;' download></a><span class=virtual_file_name></span>");
                        }
                    }
                   	
                    // new instance.web.DataSet(self.view.dataset.model).call('read', [id]).done(function(result) {
                    // console.log("values ????",result)
                    // url = result.virtual_file_name_url;
                    // console.log("Readonly >>>>>",url);
                    // if(!url){
                    // url = result.file_url;
                    // }
                    // if(url){
                    // var show_value = _t("Download");
                    // $('.virtual_file_name').remove();
                    // if (self.view.datarecord[self.node.attrs.filename]){
                    // self.$el.find('a').replaceWith("<a class=virtual_file href='" + url + "' style='text-decoration: underline ;' download>" + show_value + "</a><span class=virtual_file_name>" + (self.view.datarecord[self.node.attrs.filename] || '') + "</span>");
                    // }else {
                    // self.$el.find('a').replaceWith("<a class=virtual_file style='text-decoration: underline ;' download></a><span class=virtual_file_name></span>");
                    // }
                    // }
                    // });
                }
            } else {
                if (this.get('value') == 'undefined') {
                    this.$el.find('input').eq(0).val('');
                }
            }
        }
    });
    instance.web.form.FieldBinary.include({
        on_file_change: function(e) {
            var file_node = e.target;
            var file = file_node.files[0];
            // console.log('dssssd',this);
            // var $input = this.$el.find('input.oe_form_binary_file')[1];
            // console.log('dssdsssd',$input);
            // $input.after($input.clone(true)).remove();
            if (file && this.widget == 'my_widget') {
	            var reader = new FileReader();
	            reader.onload = this.imageIsLoaded;
	            reader.readAsDataURL(file);
                var fname = file.name.toLowerCase();
                var pos = fname.lastIndexOf(".");
                var file_ext = fname.substring(pos, fname.length);
                var _validFileExtensions = [".jpg", ".jpeg", ".bmp", ".gif", ".png", ".jfif", ".tiff", ".rif", ".ai", ".eps", ".pdf"];

                if (file.size / 1048576 < 20) {
                    if (_validFileExtensions.indexOf(file_ext) >= 0) {
                        this._super(e);
                    } else {
                        instance.webclient.notification.warn(_t("Virtual File"), _t(file_ext + " file not supported.\nSupported Ext : .png,.jpg,.jpeg,.gif,.pdf,.ai,.eps"));
                    }
                } else {
                    instance.webclient.notification.warn(_t("Virtual File Size Exceed"), _t(file_ext + " File is too large to upload (Max : 20 MB)"));
                }
            } else {

                this._super(e);
            }
        },
       	imageIsLoaded: function(e) {
		    $('#myImg').attr('src', e.target.result);
		    
		},
    });
    instance.web.list.Binary.include({
        _format: function(row_data, options) {
            var flag = true;
            var ret1 = false;
            if (this.options) {
                my_option = JSON.parse(this.options);
                if (my_option.virtual_img && row_data.virtual_file_name.value) {
                    var show_value = _t("Download");
                    ret1 = _.template("<a href='" + row_data.virtual_file_name_url.value + "' style='text-decoration: underline ;' download=" + row_data.virtual_file_name.value + ">" + show_value + " " + row_data.virtual_file_name.value + "</a>", {});
                } else {
                    ret1 = this._super(row_data, options);
                }
                return ret1;

                if (my_option.custom_img && row_data.file_url.value) {
                    var show_value = _t("Download");
                    ret1 = _.template("<a href='" + row_data.file_url.value + "' style='text-decoration: underline ;' download=" + row_data.name.value + ">" + show_value + row_data.name.value + "</a>", {});
                } else {
                    ret1 = this._super(row_data, options);
                }
            } else {
                ret1 = this._super(row_data, options);
            }
            return ret1;
        }
    });
    instance.web.ListView.List.include({
        init: function(group, opts) {
            var self = this;
            this.group = group;
            this.view = group.view;
            this.session = this.view.session;

            this.options = opts.options;
            this.columns = opts.columns;
            this.dataset = opts.dataset;
            this.records = opts.records;

            this.record_callbacks = {
                'remove': function(event, record) {
                    var id = record.get('id');
                    self.dataset.remove_ids([id]);
                    var $row = self.$current.children('[data-id=' + id + ']');
                    var index = $row.data('index');
                    $row.remove();
                },
                'reset': function() {
                    return self.on_records_reset();
                },
                'change': function(event, record, attribute, value, old_value) {
                    var $row;
                    if (attribute === 'id') {
                        if (old_value) {
                            throw new Error(_.str.sprintf(_t("Setting 'id' attribute on existing record %s"),
                                JSON.stringify(record.attributes)));
                        }
                        self.dataset.add_ids([value], self.records.indexOf(record));
                        // Set id on new record
                        $row = self.$current.children('[data-id=false]');
                    } else {
                        $row = self.$current.children(
                            '[data-id=' + record.get('id') + ']');
                    }
                    $row.replaceWith(self.render_record(record));
                },
                'add': function(ev, records, record, index) {
                    var $new_row = $(self.render_record(record));
                    var id = record.get('id');
                    if (id) {
                        self.dataset.add_ids([id], index);
                    }

                    if (index === 0) {
                        $new_row.prependTo(self.$current);
                    } else {
                        var previous_record = records.at(index - 1),
                            $previous_sibling = self.$current.children(
                                '[data-id=' + previous_record.get('id') + ']');
                        $new_row.insertAfter($previous_sibling);
                    }
                }
            };
            _(this.record_callbacks).each(function(callback, event) {
                this.records.bind(event, callback);
            }, this);

            this.$current = $('<tbody>')
                .delegate('input[readonly=readonly]', 'click', function(e) {
                    /*
                        Against all logic and sense, as of right now @readonly
                        apparently does nothing on checkbox and radio inputs, so
                        the trick of using @readonly to have, well, readonly
                        checkboxes (which still let clicks go through) does not
                        work out of the box. We *still* need to preventDefault()
                        on the event, otherwise the checkbox's state *will* toggle
                        on click
                     */
                    e.preventDefault();
                })
                .delegate('th.oe_list_record_selector', 'click', function(e) {
                    e.stopPropagation();
                    var selection = self.get_selection();
                    $(self).trigger(
                        'selected', [selection.ids, selection.records]);
                })
                .delegate('td.oe_list_record_delete button', 'click', function(e) {
                    e.stopPropagation();
                    var $row = $(e.target).closest('tr');
                    $(self).trigger('deleted', [
                        [self.row_id($row)]
                    ]);
                })
                .delegate('td.oe_list_field_cell button', 'click', function(e) {
                    e.stopPropagation();
                    var $target = $(e.currentTarget),
                        field = $target.closest('td').data('field'),
                        $row = $target.closest('tr'),
                        record_id = self.row_id($row);

                    if ($target.attr('disabled')) {
                        return;
                    }
                    if (!$target[0].title == _t("Download Image"))
                        $target.attr('disabled', 'disabled');

                    // note: $.data converts data to number if it's composed only
                    // of digits, nice when storing actual numbers, not nice when
                    // storing strings composed only of digits. Force the action
                    // name to be a string
                    $(self).trigger('action', [field.toString(), record_id, function(id) {
                        $target.removeAttr('disabled');
                        return self.reload_record(self.records.get(id));
                    }]);
                })
                .delegate('a', 'click', function(e) {
                    e.stopPropagation();
                })
                .delegate('tr', 'click', function(e) {
                    var row_id = self.row_id(e.currentTarget);
                    if (row_id) {
                        e.stopPropagation();
                        if (!self.dataset.select_id(row_id)) {
                            throw new Error(_t("Could not find id in dataset"));
                        }
                        self.row_clicked(e);
                    }
                });
        }
    });

    instance.web.ActionManager.include({
        ir_actions_download_file: function(action, options) {
            var cur_time = (new Date).getTime();
            var f_name = action.file_name || 'unknown';
            var anchor_ele = $("<a href='" + action.file_url + "' id='" + cur_time + "' target='_blank' download='" + f_name + "'/>");
            if ($('div.oe_configure_line').length > 0) {
                $('div.oe_configure_line').append(anchor_ele[0]);
                $('a#' + cur_time)[0].click();
            } else {
                $('div.oe_view_manager_view_list').append(anchor_ele[0]);
                $('a#' + cur_time)[0].click();
            }
        }
    });
};