/*global openerp, _, $ */

openerp.ob_product_multi_images = function (instance) {
    var QWeb = instance.web.qweb,
    _t  = instance.web._t,
    _lt = instance.web._lt;
    
    instance.web.form.FieldBinaryImageMulti = instance.web.form.FieldBinaryImage.extend({
    template: 'FieldBinaryImageMulti',
    init: function(field_manager, node) {
        var self = this;
        this._super(field_manager, node);
        this.binary_value = false;
        this.useFileAPI = !window.FileReader;
        this.max_upload_size = 3 * 1024 * 1024; // 25Mo
        if (!this.useFileAPI) {
            this.fileupload_id = _.uniqueId('oe_fileupload');
            $(window).on(this.fileupload_id, function() {
                var args = [].slice.call(arguments).slice(1);
                self.on_file_uploaded.apply(self, args);
            });
        }
    },
    initialize_content: function() {
        var self = this;
        var dataset = new instance.web.DataSetSearch(this, 'res.users', {}, []);
        dataset.read_ids([instance.session.uid], ['name']).then(function(res) {
            if (res)
                self.user_name = res[0].name;
        });
        this._super();
        this.$el.find('.oe-image-preview').click(this.on_preview_button);
        this.$el.find('.oe_image_list').click(this.on_list_image);
    },
    on_file_change: function(e) {
        $('body').addClass("spinner-custom");
        var div= document.createElement("div");
        div.className += "overlay";
        document.body.appendChild(div);
        var self = this;
        var file_node = e.target;
        // instance.web.blockUI();
        console.log('block uper');
        if ((this.useFileAPI && file_node.files.length) || (!this.useFileAPI && $(file_node).val() !== '')) {
            if (this.useFileAPI) {
                var file = file_node.files[0];
                
                if (file.size > this.max_upload_size) {
                    var msg = _t("The selected file exceed the maximum file size of %s.");
                    instance.webclient.notification.warn(_t("File upload"), _.str.sprintf(msg, instance.web.human_size(this.max_upload_size)));
                    return false;
                }
                var filereader = new FileReader();
                filereader.readAsDataURL(file);
                filereader.onloadend = function(upload) {
                    var data = upload.target.result;
                    data = data.split(',')[1];
                    self.on_file_uploaded(file.size, file.name, file.type, data);
                };
            } else {
                this.$el.find('form.oe_form_binary_form input[name=session_id]').val(this.session.session_id);
                this.$el.find('form.oe_form_binary_form').submit();
            }
            this.$el.find('.oe_form_binary_progress').show();
            this.$el.find('.oe_form_binary').hide();
        }
        $('body').removeClass("spinner-custom");
        $('.overlay').remove();
        // instance.web.unblockUI();
    },
    on_file_uploaded_and_valid: function(size, name, content_type, orignal_file_name, date) {
        var self = this;
        var check_file = false;

        check_file = self.check_file_valid(content_type, orignal_file_name);
        
        if ( check_file ){
            if (name && size < this.max_upload_size) {
                var data_dict = {"size": instance.web.human_size(size), "name": name, "content_type": content_type, "date": date, "orignal_name": orignal_file_name, 'user':this.user_name};
                var data = JSON.parse(this.get('value'));
                if (data)
                    data.push(data_dict);
                else
                    data = [data_dict];
                this.internal_set_value(JSON.stringify(data));
                this.binary_value = true;
                this.set_filename(name);
                this.render_value();
                this.do_warn(_t("File Upload"), _t("File Upload Successfully !"));
            }
            else{
                if (size > this.max_upload_size) {
                    var msg = _t("The selected file exceed the maximum file size of %s.");
                      this.do_warn(_t("File upload"), _.str.sprintf(msg, instance.web.human_size(this.max_upload_size)));
                }else {
                       this.do_warn(_t("File Upload"), _t("There was a problem while uploading your file"));
                }
            }
        }
    },
    check_file_valid: function(content_type,orignal_file_name){
        var _validFileExtensions = ["jpg", "jpeg", "bmp", "gif", "png","jfif","tif","tiff","rif","riff","ai","eps","pdf"];
        
        var name_file = orignal_file_name.toLowerCase().split('.').pop();
        
        if (_validFileExtensions.indexOf(name_file) < 0){
                  this.do_warn(_t("File Upload"), _t("Only  jpg, jpeg, bmp, gif, png, jfif, tiff, rif, ai, eps allowed." ));
                  return false;
        }else {
            var image_type = false;
            if (name_file == 'ai' || name_file == 'eps' || name_file =='rif'){
                    return true;
                }
            if (content_type == 'undefined' || !content_type){
                    this.do_warn(_t("File Upload"), _t("Only  jpg, jpeg, bmp, gif, png, jfif, tiff, rif, ai, eps allowed." ));
                    return false;
            }else if (content_type){
                
                image_type = content_type.match(/image/i);
                if ((content_type == 'application/pdf') || (image_type && image_type.length > 0) || (content_type == 'application/postscript')){
                    
                    return true;
                }else {
                    this.do_warn(_t("File Upload"), _t("Only  jpg, jpeg, bmp, gif, png, jfif, tiff, rif, ai, eps allowed." ));
                    return false;
                }
             }
         }
    },
    on_list_image: function() {
        var images_list = this.get('value');
        var self = this;
        if (!this.get('value')) { 
            this.do_warn(_t("Image"), _t("Image not available !"));
            return false; 
        }
        this.image_list_dialog = new instance.web.Dialog(this, {
            title: _t("Image List"),
            width: '840px',
            height: '70%',
            min_width: '600px',
            min_height: '500px',
            buttons: [
                 {text: _t("Close"), click: function() { self.image_list_dialog.close();}}
            ]
        }).open();
        this.on_render_dialog();
    },
    on_render_dialog: function() {
        var IS_JSON = true;
        try
        {
            var json = $.parseJSON(this.get('value'));
        }
        catch(err)
        {
            IS_JSON = false;
        }
        images_list = [];
        if (IS_JSON) {
            images_list = JSON.parse(this.get('value'));
        }
        var self = this;
        var url_list = [];
        if (images_list) {
            _.each(images_list, function (index) {
                if (index) {
                    if(index['name_1']){
                        url_list.push({'name' : index['name_1'], 'path' : index['name'],'content_type': index['content_type']});
                    }else{
                        url_list.push({'name' : index['orignal_name'], 'path' : index['name'],'content_type': index['content_type']});
                    }
                }
            });
        }
        else { return false; }
        var image_list = [];
        var start = 0;
        for(var i=1; i <= Math.ceil(url_list.length/4); i++) {
            image_list.push(url_list.slice(start, start + 4));
            start = i * 4;
        }
        this.image_list_dialog.$el.html(QWeb.render('DialogImageList', {'widget': this, 'image_list': image_list}));
        this.image_list_dialog.$el.find(".oe-remove-image").click(function() {
            self.do_remove_image(this, true);
        });
    },
    
    render_value: function() {
        var self = this;
        var images_list = JSON.parse(this.get('value'));
        this.$el.find('#imagedescription').remove();
        var $img = QWeb.render("ImageDescription", { image_list: images_list, widget: this});
        this.$el.append($img);
        this.$el.find(".oe_image_row").click(function() {
            if (this.id) {
                var clicked = this.id;
                var name_desc = "";
                var title = "";
                var description = "";
                var content_type = "";
                _.each(images_list, function (index) {
                    if (index['name'] == clicked ) {
                        title = index['name_1'] ? index['name_1'] : '';
                        description = index['description'] ? index['description'] : '';
                        name_desc = 'Title:-' + title + '<br/>Description:-' +description;
                        content_type = index['content_type'];
                    }
                });
                self.do_display_image(this, name_desc, content_type, title, description);
            }
        });
        this.$el.find(".oe_list_record_delete").click(function() {
            if (this.id) {
                self.do_remove_image(this, false);
            }
        });
        this.$el.find(".oe-record-edit-link").click(function() {
            var self_1 = this;
            var data = JSON.parse(self.get('value'));
            _.each(data, function(d){
                if(d.name == self_1.id){
                    self.name_display = d.name_1 ? d.name_1 : '';
                    self.description_display = d.description ? d.description : '';
                }
            });
            self.select_mo_dialog = $(QWeb.render('edit_name_description', {widget:self})).dialog({
                resizable: false,
                modal: true,
                title: _t("Image Description"),
                width: 500,
                buttons: {
                    "Ok": function() {
                        var new_list = [];
                        var data = JSON.parse(self.get('value'));
                        if (self_1.id && data) {
                            _.each(data, function (index) {
                                if (index['name'] != self_1.id ) {
                                    new_list.push(index);
                                }
                                else {
                                    index["name_1"] = self.select_mo_dialog.find('#name_1').val();
                                    index["description"] = self.select_mo_dialog.find('#description').val();
                                    new_list.push(index);
                                }
                            });
                            self.internal_set_value(JSON.stringify(new_list));
                            self.invalid = false;
                            self.dirty = true;
                            self.render_value();
                            $(this).dialog( "close" );
                        }
                    },
                    "Close": function() {
                        $(this).dialog( "close" );
                    }
                },
            });
        });
    },
    do_display_image: function(curr_id, name_desc) {
        this.$el.find('.oe-image-preview').lightbox({
            fitToScreen: true,
            jsonData: [{"url" :curr_id.id, "title": name_desc}],
            loopImages: true,
            imageClickClose: false,
            disableNavbarLinks: true
        });
    },
    do_remove_image: function(curr_id, dialog) {
        var self = this;
        var images_list = JSON.parse(this.get('value'));
        if (images_list) {
            var new_list = [];
            if (confirm(_t("Are you sure to remove this image?"))) {
                _.each(images_list, function (index) {
                    if (index['name'] != curr_id.id ) {
                        new_list.push(index);
                    }
                });
                self.internal_set_value(JSON.stringify(new_list));
                this.invalid = false;
                this.dirty = true;
                if (dialog) {
                    this.on_render_dialog();
                }
                else{
                    this.render_value();
                }
            }
        }
    },
    on_preview_button: function() {
        var images_list = JSON.parse(this.get('value'));
        var url_list = [];
        var self = this;
        if (images_list && images_list.length>0) {
            _.each(images_list, function (index) {
                if (index) {
                    var title = index['name_1'] ? index['name_1'] : '';
                    var description = index['description'] ? index['description'] : '';
                    url_list.push({"url" :index['name'], "title": 'Title:-' + title + '<br/>Description:-' +description});
                }
            });
            this.$el.find('.oe-image-preview').lightbox({
                fitToScreen: true,
                jsonData: url_list,
                loopImages: true,
                imageClickClose: false,
                disableNavbarLinks: true
            });
        }
        else {
            this.do_warn("Image", "Image not available !");
            return false;
        }
        
    },
});

instance.web.form.FieldBinaryImagPdfeMulti = instance.web.form.FieldBinaryImageMulti.extend({
    template: 'FieldBinaryImagePdfMulti',
    init: function(field_manager, node) {
        this._super(field_manager, node);
        this.max_upload_size = 15 * 1024 * 1024; // 25Mo
    },
    
    on_file_change: function(e) {
        $('body').addClass("spinner-custom");
        var div= document.createElement("div");
        div.className += "overlay";
        document.body.appendChild(div);
        console.log('block niche',instance.web);

        var self = this;
        var file_node = e.target;
        if ((this.useFileAPI && file_node.files.length) || (!this.useFileAPI && $(file_node).val() !== '')) {
            if (this.useFileAPI) {
                var file = file_node.files[0];
                if (file.size > this.max_upload_size) {
                    var msg = _t("The selected file exceed the maximum file size of %s.");
                    instance.webclient.notification.warn(_t("File upload"), _.str.sprintf(msg, instance.web.human_size(this.max_upload_size)));
                    return false;
                }
                var filereader = new FileReader();
                
                filereader.readAsDataURL(file);
                filereader.onloadend = function(upload) {
                    var data = upload.target.result;
                    data = data.split(',')[1];
                    self.on_file_uploaded(file.size, file.name, file.type, data);
                };
            } else {
                this.$el.find('form.oe_form_binary_form input[name=session_id]').val(this.session.session_id);
                this.$el.find('form.oe_form_binary_form').submit();
            }
            this.$el.find('.oe_form_binary_progress').show();
            this.$el.find('.oe_form_binary').hide();
            
        }
        $('body').removeClass("spinner-custom");
        $('.overlay').remove();
        // instance.web.unblockUI();
    },
    render_value: function() {
        var self = this;
        var IS_JSON = true;
        try
        {
            var json = $.parseJSON(this.get('value'));
        }
        catch(err)
        {
            IS_JSON = false;
        }
        images_list = [];
        if (IS_JSON) {
            images_list = JSON.parse(this.get('value'));
        }
        this.$el.find('#imagepdfdescription').remove();
        var $img = QWeb.render("ImagePdfDescription", { image_list: images_list, widget: this});
        this.$el.append($img);
        this.$el.find(".oe_image_row").click(function() {
            if (this.id) {
                var clicked = this.id;
                var name_desc = "";
                var title = "";
                var description = "";
                var content_type = "";
                _.each(images_list, function (index) {
                    if (index['name'] == clicked ) {
                        title = index['name_1'] ? index['name_1'] : '';
                        description = index['description'] ? index['description'] : '';
                        name_desc = 'Title:-' + title + '<br/>Description:-' +description;
                        content_type = index['content_type'];
                    }
                });
                self.do_display_image(this, name_desc, content_type, title, description);
            }
        });
        this.$el.find(".oe_list_record_delete").click(function() {
            if (this.id) {
                self.do_remove_image(this, false);
            }
        });
        this.$el.find(".oe-record-edit-link").click(function() {
            var self_1 = this;
            var data = JSON.parse(self.get('value'));
            _.each(data, function(d){
                if(d.name == self_1.id){
                    self.name_display = d.name_1 ? d.name_1 : '';
                    self.description_display = d.description ? d.description : '';
                }
            });
            self.select_mo_dialog = $(QWeb.render('edit_name_description', {widget:self})).dialog({
                resizable: false,
                modal: true,
                title: _t("Image Description"),
                width: 500,
                buttons: {
                    "Ok": function() {
                        var new_list = [];
                        var data = JSON.parse(self.get('value'));
                        if (self_1.id && data) {
                            _.each(data, function (index) {
                                if (index['name'] != self_1.id ) {
                                    new_list.push(index);
                                }
                                else {
                                    index["name_1"] = self.select_mo_dialog.find('#name_1').val();
                                    index["description"] = self.select_mo_dialog.find('#description').val();
                                    new_list.push(index);
                                }
                            });
                            self.internal_set_value(JSON.stringify(new_list));
                            self.invalid = false;
                            self.dirty = true;
                            self.render_value();
                            $(this).dialog( "close" );
                        }
                    },
                    "Close": function() {
                        $(this).dialog( "close" );
                    }
                },
            });
        });
    },
    do_display_image: function(curr_id, name_desc, content_type, title, description) {
        var name = curr_id.id.split('/');
        var file_name = name.slice(-1)[0].split('.').pop().toLowerCase();
        
        if ((file_name == 'ai') || (file_name == 'eps') || (file_name == 'tif') || (file_name == 'tiff')){
            this.do_warn("No Image Preview Available", "No Image Preview Avaialable.");
            return false;
        }
        if (content_type == 'application/pdf') {
            $(QWeb.render('DisplayPDFImage', { widget:curr_id, url: curr_id.id, title: title, desc:description }))
                    .dialog({
                             position: 'center',
                             overflow: 'hidden',
                             closeOnEscape: true,
                             modal: true,
                             resizable: false,
                             width: 680,
                             height:700,
                             close: function(){
                                $(".ui-dialog").find("#dialog").dialog("destroy");
                             },
                             open: function (event, ui) {
                                 //$(this).css('overflow', 'hidden');
                                 $(this).parent().css('z-index', '1122');
                                  //this line does the actual hiding
                             }}).siblings('.ui-dialog-titlebar').remove();
                      
                      $('.close_button').click(function(){
                          $(".ui-dialog:visible").find("#dialog").dialog("destroy");
                          
                      });
        }else {
            this.$el.find('.oe-image-preview').lightbox({
                fitToScreen: true,
                jsonData: [{"url" :curr_id.id, "title": name_desc,'content_type':content_type}],
                loopImages: true,
                imageClickClose: false,
                disableNavbarLinks: true
            });
        }
    },
});

instance.web.form.FieldBinaryImageGrid = instance.web.form.FieldBinaryImage.extend({
    init: function(field_manager, node) {
        var self = this;
        this._super(field_manager, node);
        this.binary_value = false;
        this.useFileAPI = !window.FileReader;
        this.max_upload_size =  3 * 1024 * 1024; // 25Mo
        if (!this.useFileAPI) {
            this.fileupload_id = _.uniqueId('oe_fileupload');
            $(window).on(this.fileupload_id, function() {
                var args = [].slice.call(arguments).slice(1);
                self.on_file_uploaded.apply(self, args);
            });
        }
    },
    initialize_content: function() {
        var self = this;
        var dataset = new instance.web.DataSetSearch(this, 'res.users', {}, []);
        dataset.read_ids([instance.session.uid], ['name']).then(function(res) {
            if (res)
                self.user_name = res[0].name;
        });
        this._super();
    },
    render_value: function() {
        var self = this;
        if (this.get('value')!=""){
            var images_list = JSON.parse(this.get('value'));
            var url_list = [];
            if (images_list && images_list.length>0) {
                var i=0;
                _.each(images_list, function (index) {
                    if (index) {
                        if(index['name_1']){
                            url_list.push({'name' : index['name_1'], 'path' : index['name'], 'index' : i});
                        }else{
                            url_list.push({'name' : index['orignal_name'], 'path' : index['name'], 'index' : i});
                        }
                    }
                    i++;
                });
                var image_list = [];
                image_list.push(url_list);
                var $img = QWeb.render("FieldBinaryImageGrid", { 'widget' : this, 'image_list' : image_list});
                this.$el.html($img);
                this.$el.find('.oe-image-large-preview').click(this.on_large_preview);
            }
            else {
                this.$el.html('<p><i>'+_t('Image(s) not available.')+'</i></p>');
                return false; 
            }
        }
    else {
        this.$el.html('<p><i>'+_t('Image(s) not available.')+'</i></p>');
        return false; 
        }
    },
    on_large_preview: function(el) {
        $img = el.currentTarget;
        var images_list = JSON.parse(this.get('value'));
        var url_list = [];
        var self = this;
        if (images_list) {
            _.each(images_list, function (index) {
                if (index) {
                    var title = index['name_1'] ? index['name_1'] : '';
                    var description = index['description'] ? index['description'] : '';
                    url_list.push({"url" :index['name'], "title": 'Title:-' + title + '<br/>Description:-' +description});
                }
            });
        }
        else {
            this.do_warn("Image", "Image not available !");
            return false;
        }
        var cur_pos = $($img).parent('a').attr('id');
        this.$el.find('.oe-image-large-preview').lightbox({
            fitToScreen: true,
            activeImage: $($img).parent('a').attr('id'),
            jsonData: url_list,
            loopImages: true,
            imageClickClose: false,
            disableNavbarLinks: true
        });
    },
    });

    instance.web.form.widgets = instance.web.form.widgets.extend({
        'image_multi' : 'instance.web.form.FieldBinaryImageMulti',
        'image_pdf_multi': 'instance.web.form.FieldBinaryImagPdfeMulti',
        'image_grid' : 'instance.web.form.FieldBinaryImageGrid',
    });
};
