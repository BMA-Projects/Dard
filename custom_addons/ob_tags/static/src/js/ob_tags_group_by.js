openerp.ob_tags = function(openerp) {
    var QWeb = openerp.web.qweb;
    openerp.web.Query.include({
    	group_by: function (grouping) {
            var ctx = openerp.web.pyeval.eval(
                'context', this._model.context(this._context));

            // undefined passed in explicitly (!)
            if (_.isUndefined(grouping)) {
                grouping = [];
            }

            if (!(grouping instanceof Array)) {
                grouping = _.toArray(arguments);
            }
            if (_.isEmpty(grouping) && !ctx['group_by_no_leaf']) {
                return null;
            }
            var raw_fields = _.map(grouping.concat(this._fields || []), function (field) {
                return field.split(':')[0];
            });
            
            if(grouping.length > 1 && grouping.indexOf("tag_id")>=0 && ['product.template','product.product'].indexOf(this._model.name)>=0){
            	new openerp.web.Dialog(this, {
                    title: _t("Warning"),
                    buttons: [
                        {text: _t("Ok"), click: function() {this.parents('.modal').modal('hide');}}
                    ]
                }, $('<div>').html('Group by Tag is not supported with other field.')).open();
            		
            }
            
            var self = this;
            return this._model.call('read_group', {
                groupby: grouping,
                fields: _.uniq(raw_fields),
                domain: this._model.domain(this._filter),
                context: ctx,
                offset: this._offset,
                lazy: this._lazy,
                limit: this._limit,
                orderby: openerp.web.serialize_sort(this._order_by) || false
            }).then(function (results) {
                return _(results).map(function (result) {
                    // FIX: querygroup initialization
                    result.__context = result.__context || {};
                    result.__context.group_by = result.__context.group_by || [];
                    _.defaults(result.__context, ctx);
                    var grouping_fields = self._lazy ? [grouping[0]] : grouping;
                    return new openerp.web.QueryGroup(
                        self._model.name, grouping_fields, result);
                });
            });
        },
    });
}
