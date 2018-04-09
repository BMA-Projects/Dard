/*global openerp, _, $ */

openerp.ob_product_image = function (instance) {

    instance.web.list.Binary.include({
        
        placeholder: "/web/static/src/img/placeholder.png",
        _format: function (row_data, options) {
            var value = row_data[this.id].value;
            var download_url;
            if (value && value.substr(0, 10).indexOf(' ') == -1) {
                download_url = "data:application/octet-stream;base64," + value;
            } else {
                download_url = this.placeholder;
            }
            return _.template("<img width='50' height='50' src='<%-href%>'/>", {
                href: download_url,
            });
        }

    });
};