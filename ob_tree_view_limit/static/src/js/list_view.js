openerp.ob_tree_view_limit = function(instance) {
    var QWeb = instance.web.qweb;
        _t = instance.web._t;

    instance.web.ListView.include({
      load_list: function(data) {
         var self = this;
         this.fields_view = data;

         if (!this.$pager) {
             this.$pager = $(QWeb.render("ListView.pager", {'widget':self}));
             if (this.options.$buttons) {
                 this.$pager.appendTo(this.options.$pager);
             } else {
                 this.$el.find('.oe_list_pager').replaceWith(this.$pager);
             }

             this.$pager
                 .on('click', 'a[data-pager-action]', function () {
                     var $this = $(this);
                     var max_page = Math.floor(self.dataset.size() / self.limit());
                     switch ($this.data('pager-action')) {
                         case 'first':
                             self.page = 0; break;
                         case 'last':
                             self.page = max_page - 1;
                             break;
                         case 'next':
                             self.page += 1; break;
                         case 'previous':
                             self.page -= 1; break;
                     }
                     if (self.page < 0) {
                         self.page = max_page;
                     } else if (self.page > max_page) {
                         self.page = 0;
                     }
                     self.reload_content();
                 }).find('.oe_list_pager_state')
                     .click(function (e) {
                         e.stopPropagation();
                         var $this = $(this);

                         var $select = $('<select>')
                             .appendTo($this.empty())
                             .click(function (e) {e.stopPropagation();})
                             .append('<option value="20">20</option>' +
                               '<option value="40">40</option>' +
                                     '<option value="80">80</option>' +
                                     '<option value="200">200</option>' +
                                     '<option value="500">500</option>' +
                                     '<option value="1000">1000</option>' +
                                     '<option value="2000">2000</option>' +
                                     '<option value="NaN">' + _t("Unlimited") + '</option>')
                             .change(function () {
                                 var val = parseInt($select.val(), 10);
                                 self._limit = (isNaN(val) ? null : val);
                                 self.page = 0;
                                 self.reload_content();
                             }).blur(function() {
                                 $(this).trigger('change');
                             })
                             .val(self._limit || 'NaN');
                     });
         }
         return self._super(data);
     },
    });
}