/*global openerp, _, $ */

openerp.ob_adnart_images = function (instance) {
    var QWeb = instance.web.qweb,
    _t  = instance.web._t,
    _lt = instance.web._lt;
    
    instance.web.form.FieldBinarySliderImage = instance.web.form.FieldBinaryImage.extend({
    template:'FieldBinarySliderImage',
    render_value: function() {
        var self = this;
        var $img = "";
        var json = false;
        var images_list = this.get('value');
        if (images_list){
            images_list = images_list.replace(/'/g, '\"');
            json = window.JSON.parse(images_list);
        }
        this.$el.find('.slider').remove();

        if (json){
            $img = QWeb.render("MultiImages", {widget: self, image_list: json });
            $('.slider-wrap').append($img);
            $('.slider').tilesSlider({ random: false });
        }
    },
    });
    
    instance.web.form.widgets = instance.web.form.widgets.extend({
        'image_slider': 'instance.web.form.FieldBinarySliderImage',
    });
};
