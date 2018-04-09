openerp.ob_live_support = function(instance) {


    instance.ob_live_support = {};
    var module = instance.im_chat;
    var mod = instance.im_odoo_support;

    module.UserWidget = openerp.Widget.extend({
        "template": "im_chat.UserWidget",
        events: {
            "click": "activate_user",
        },
        init: function(parent, user) {
            this._super(parent);
            this.set("id", user.id);

            if (user.name == 'Odoo Support'){
                user.name = 'Support'
                user.image_url = '/ob_live_support/static/src/img/officebrain.png'
            }

            this.set("name", user.name);
            this.set("im_status", user.im_status);
            this.set("image_url", user.image_url);
        },
        start: function() {
            this.$el.data("user", {id:this.get("id"), name:this.get("name")});
            this.$el.draggable({helper: "clone"});
            this.on("change:im_status", this, this.update_status);
            this.update_status();
        },
        update_status: function(){
            this.$(".oe_im_user_online").toggle(this.get('im_status') !== 'offline');
            var img_src = (this.get('im_status') == 'away' ? '/im_chat/static/src/img/yellow.png' : '/im_chat/static/src/img/green.png');
            this.$(".oe_im_user_online").attr('src', img_src);
        },
        activate_user: function() {
            this.trigger("activate_user", this.get("id"));
        },
    });

    var _t = openerp._t;
    var COOKIE_NAME = 'livechat_conversation';
    var SERVICE_URL = 'https://services.odoo.com/';



    module.ImTopButton = openerp.Widget.extend({
        template:'im_chat.ImTopButton',
        events: {
            "click": "clicked",
        },
        clicked: function(ev) {
            ev.preventDefault();
            new instance.web.Model('res.users').call("check_support",[], {})
                .then(function(result) {
                    if (result == false){
                        $('.odoo_support_contact').css({'visibility': 'hidden'});
                        $('.odoo_support_contact').remove();
                    }
                });

            this.trigger("clicked");
        },
    });
};
