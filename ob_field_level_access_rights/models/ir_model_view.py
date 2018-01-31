# -*- coding: utf-8 -*-
from openerp import models, fields
from openerp.osv import orm
from lxml import etree
from openerp.tools.translate import _
import json


class view(models.Model):
    _inherit = 'ir.ui.view'

    def postprocess(self, cr, user, model, node, view_id, in_tree_view, model_fields, context=None):

        """Return the description of the fields in the node.

        In a normal call to this method, node is a complete view architecture
        but it is actually possible to give some sub-node (this is used so
        that the method can call itself recursively).

        Originally, the field descriptions are drawn from the node itself.
        But there is now some code calling fields_get() in order to merge some
        of those information in the architecture.

        """

        if context is None:
            context = {}
        result = False
        fields = {}
        children = True

        modifiers = {}
        Model = self.pool.get(model)
        if Model is None:
            self.raise_view_error(cr, user, _('Model not found: %(model)s') % dict(model=model),
                                  view_id, context)

        def encode(s):
            if isinstance(s, unicode):
                return s.encode('utf8')
            return s

        def check_group(node):
            """Apply group restrictions,  may be set at view level or model level::
               * at view level this means the element should be made invisible to
                 people who are not members
               * at model level (exclusively for fields, obviously), this means
                 the field should be completely removed from the view, as it is
                 completely unavailable for non-members

               :return: True if field should be included in the result of fields_view_get
            """

            if node.tag == 'field' and node.get('name') in Model._fields:
                field = Model._fields[node.get('name')]
                # Apply field level access-rights
                field_obj = self.pool.get('ir.model.fields')
                field_ids = field_obj.search_read(cr, user, [('name', '=', node.get('name')), ('model', '=', Model._name)])  # Search field
                if field_ids:
                    field_ids = field_ids[0]
                    invisible_groups = field_ids.get('invisible_groups')
                    read_only_groups = field_ids.get('read_only_groups')
                    same_field_flag = True
                    if invisible_groups: # Apply invisible on field based on groups
                        cr.execute("""SELECT 1 FROM res_groups_users_rel WHERE uid=%s AND gid IN %s""", (user, tuple(invisible_groups)))
                        if bool(cr.fetchone()):
                            node.set('invisible', '1')
                            modifiers['invisible'] = True
                            # Remove attrs for conditional visible/invisible (DOMAIN) issue.
                            if 'attrs' in node.attrib:
                                del(node.attrib['attrs'])
                            # Remove widget that is call external view/template and we are not able to apply restriction on other view/template becuase we apply restriction only on fields.
                            if 'widget' in node.attrib:
                                del(node.attrib['widget'])
                            same_field_flag = False
                    # If field have a any invisible group than no need to check read only group or apply read only attribute on field.
                    if read_only_groups and same_field_flag:# Apply readonly on field based on groups
                        cr.execute("""SELECT 1 FROM res_groups_users_rel WHERE uid=%s AND gid IN %s""", (user, tuple(read_only_groups)))
                        if bool(cr.fetchone()):
                            node.set('readonly', '1')
                            if 'attrs' in node.attrib:
                                attrs = eval(node.attrib['attrs'])
                                if attrs.get('invisible', False):
                                    # For read only attribute, remove other attributes like required that gives warning in case of none value.
                                    node.attrib['attrs'] = str({'invisible': attrs['invisible']})
                if field.groups and not self.user_has_groups(cr, user, groups=field.groups, context=context):
                    node.getparent().remove(node)
                    fields.pop(node.get('name'), None)
                    # no point processing view-level ``groups`` anymore, return
                    return False

            if node.get('groups'):

                can_see = self.user_has_groups(
                    cr, user, groups=node.get('groups'), context=context)
                if not can_see:
                    node.set('invisible', '1')
                    modifiers['invisible'] = True
                    if 'attrs' in node.attrib:
                        del(node.attrib['attrs'])  # avoid making field visible later
                del(node.attrib['groups'])
            return True

        if node.tag in ('field', 'node', 'arrow'):
            if node.get('object'):
                attrs = {}
                views = {}
                xml = "<form>"
                for f in node:
                    if f.tag == 'field':
                        xml += etree.tostring(f, encoding="utf-8")
                xml += "</form>"
                new_xml = etree.fromstring(encode(xml))
                ctx = context.copy()
                ctx['base_model_name'] = model
                xarch, xfields = self.postprocess_and_fields(cr, user, node.get('object'), new_xml, view_id, ctx)
                views['form'] = {
                    'arch': xarch,
                    'fields': xfields
                }
                attrs = {'views': views}
                fields = xfields
            if node.get('name'):
                attrs = {}
                field = Model._fields.get(node.get('name'))
                if field:
                    children = False
                    views = {}
                    for f in node:
                        if f.tag in ('form', 'tree', 'graph', 'kanban', 'calendar'):
                            node.remove(f)
                            ctx = context.copy()
                            ctx['base_model_name'] = model
                            xarch, xfields = self.postprocess_and_fields(cr, user, field.comodel_name, f, view_id, ctx)
                            views[str(f.tag)] = {
                                'arch': xarch,
                                'fields': xfields
                            }
                    attrs = {'views': views}
                fields[node.get('name')] = attrs

                field = model_fields.get(node.get('name'))
                if field:
                    orm.transfer_field_to_modifiers(field, modifiers)

        elif node.tag in ('form', 'tree'):
            result = Model.view_header_get(cr, user, False, node.tag, context)
            if result:
                node.set('string', result)
            in_tree_view = node.tag == 'tree'

        elif node.tag == 'calendar':
            for additional_field in ('date_start', 'date_delay', 'date_stop', 'color', 'all_day', 'attendee'):
                if node.get(additional_field):
                    fields[node.get(additional_field)] = {}

        if not check_group(node):
            # node must be removed, no need to proceed further with its children
            return fields

        # The view architeture overrides the python model.
        # Get the attrs before they are (possibly) deleted by check_group below
        orm.transfer_node_to_modifiers(node, modifiers, context, in_tree_view)

        # TODO remove attrs counterpart in modifiers when invisible is true ?

        # translate view
        if 'lang' in context:
            Translations = self.pool['ir.translation']
            if node.text and node.text.strip():
                term = node.text.strip()
                trans = Translations._get_source(cr, user, model, 'view', context['lang'], term)
                if trans:
                    node.text = node.text.replace(term, trans)
            if node.tail and node.tail.strip():
                term = node.tail.strip()
                trans = Translations._get_source(cr, user, model, 'view', context['lang'], term)
                if trans:
                    node.tail =  node.tail.replace(term, trans)

            if node.get('string') and node.get('string').strip() and not result:
                term = node.get('string').strip()
                trans = Translations._get_source(cr, user, model, 'view', context['lang'], term)
                if trans == term and ('base_model_name' in context):
                    # If translation is same as source, perhaps we'd have more luck with the alternative model name
                    # (in case we are in a mixed situation, such as an inherited view where parent_view.model != model
                    trans = Translations._get_source(cr, user, context['base_model_name'], 'view', context['lang'], term)
                if trans:
                    node.set('string', trans)

            for attr_name in ('confirm', 'sum', 'avg', 'help', 'placeholder'):
                attr_value = node.get(attr_name)
                if attr_value and attr_value.strip():
                    trans = Translations._get_source(cr, user, model, 'view', context['lang'], attr_value.strip())
                    if trans:
                        node.set(attr_name, trans)

        for f in node:
            if children or (node.tag == 'field' and f.tag in ('filter', 'separator')):
                fields.update(self.postprocess(cr, user, model, f, view_id, in_tree_view, model_fields, context))
        orm.transfer_modifiers_to_node(modifiers, node)
        return fields

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
