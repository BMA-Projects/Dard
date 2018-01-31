CKEDITOR_BASEPATH = '/web_ckeditor/static/lib/ckeditor/';
function destroy_ckeditor(instance) {
    try {
        if (instance)
            instance.destroy(true);
    } catch(e) {
        console.log("Silenced a CKEditor destroy exception.");
    }
}
openerp.web_ckeditor = function (instance) {
    var QWeb = instance.web.qweb,
    _t  = instance.web._t,
    _lt = instance.web._lt;
    instance.web.form.FieldTextHtml.include({
        events: {
            'change input': 'store_dom_value',
        },
        editor: false,
        initialize_content: function() {
            var self = this;
            if(this.editor) {
                destroy_ckeditor(this.editor);
            }
            if (!this.get("effective_readonly")) { //  && this.flag (formview)
                this.editor = CKEDITOR.replace(this.$el.find('textarea')[0], {
                   toolbar: [
                        { name: 'document', groups: [ 'mode', 'document', 'doctools' ], items: [ 'Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates' ] },
                        { name: 'clipboard', groups: [ 'clipboard', 'undo' ], items: [ 'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo' ] },
                        { name: 'editing', groups: [ 'find', 'selection', 'spellchecker' ], items: [ 'Find', 'Replace', '-', 'SelectAll', '-', 'Scayt' ] },
                        { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ], items: [ 'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat' ] },
                        '/',
                        { name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align', 'bidi' ], items: [ 'NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl', 'Language' ] },
                        { name: 'insert', items: [ 'Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe' ] },
                        { name: 'links', items: [ 'Link', 'Unlink', 'Anchor' ] },
                        '/',
                        { name: 'styles', items: [ 'Styles', 'Format', 'Font', 'FontSize' ] },
                        { name: 'colors', items: [ 'TextColor', 'BGColor' ] },
                        { name: 'tools', items: [ 'Maximize', 'ShowBlocks' ] }
                    ],
                    filebrowserWindowWidth: '640',
                    filebrowserWindowHeight: '480',
                });
            }
        },
        store_dom_value: function () {
            if (!this.get('effective_readonly')
                && this.editor !== false
                && this.editor.getData().length
                && this.is_syntax_valid()) {                    
                this.internal_set_value(this.parse_value(this.editor.getData()));
            }
        },

        commit_value: function () {
            return this.store_dom_value();
        },
        
        render_value: function() {
            var show_value = this.format_value(this.get('value'), '');
            if (!this.get("effective_readonly") && this.editor !== false) {
                this.editor.setData(show_value);
            } else {
                this.$el.html(show_value);
            }
        },

        is_syntax_valid: function() {
            if (!this.get("effective_readonly") &&
                this.editor && this.editor.getData().length > 0) {
                try {
                    this.parse_value(this.editor.getData(), '');
                    return true;
                } catch(e) {
                    return false;
                }
            }
            return true;
        },

        parse_value: function(val, def) {
            return instance.web.parse_value(val, this, def);
        },

        format_value: function(val, def) {
            return instance.web.format_value(val, this, def);
        },

        is_false: function() {
            return this.get('value') === '' || this._super();
        },
        
        focus: function() {
            this.$('textarea:first')[0].focus();
        },

        /*set_dimensions: function (height, width) {
            this._super(height, width);
            this.$('textareat').css({
                height: height,
                width: width
            });
        },

        destroy: function() {
            if (this.editor) {
                destroy_ckeditor(this.editor);
                this.editor = false;
            }
        }*/
    });
};
