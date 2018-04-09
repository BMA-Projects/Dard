# -*- coding: utf-8 -*-
from openerp import models, fields
import time
# from openerp.addons.base.ir.ir_ui_menu import ir_ui_menu

# @api.multi
# def write(self, vals):
#     print "\nvals----->>>", vals
#     return super(models.Model, self).write(vals)

# ir_ui_menu.write = write

class ir_ui_menu(models.Model):
    _inherit = 'ir.ui.menu'

    invisible_groups = fields.Many2many(
        'res.groups', 'ir_ui_menu_group_rel_invisible_group_ob',
        'group_id', 'menu_id', 'Invisible Menu')




# class ir_model_data(models.Model):
#     _inherit = 'ir.model.data'


#     def _update(self,cr, uid, model, module, values, xml_id=False, store=True, noupdate=False, mode='init', res_id=False, context=None):
#         print "MY"
#         model_obj = self.pool[model]
#         if not context:
#             context = {}
#         # records created during module install should not display the messages of OpenChatter
#         context = dict(context, install_mode=True)
#         if xml_id and ('.' in xml_id):
#             assert len(xml_id.split('.'))==2, _("'%s' contains too many dots. XML ids should not contain dots ! These are used to refer to other modules data, as in module.reference_id") % xml_id
#             module, xml_id = xml_id.split('.')
#         action_id = False
#         if xml_id:
#             #OFFICEBEACON CODE
#             if model == 'ir.ui.menu':
#                 for i in self.pool.get(model).browse(cr, uid, res_id, context=context):
#                     print "\nvalues---->>", values
#                     list0 = i.groups_id and i.groups_id.ids
#                     print "list0",list0
#                     list1 = values.get('groups_id', False) and list(values.get('groups_id', False)[0])
#                     print "list1",list1
#                     if list0 and list1:
#                         list2 = [tuple(set(list0).intersection(list1))]
#                         list3 = list2 if list2[0] else []
#                         print "list2",list2
#                         print "list3",list3
#                         values.update({'groups_id': list3})
#                 print "values", values

#             cr.execute('''SELECT imd.id, imd.res_id, md.id, imd.model, imd.noupdate
#                           FROM ir_model_data imd LEFT JOIN %s md ON (imd.res_id = md.id)
#                           WHERE imd.module=%%s AND imd.name=%%s''' % model_obj._table,
#                           (module, xml_id))
#             results = cr.fetchall()
#             for imd_id2,res_id2,real_id2,real_model,noupdate_imd in results:
#                 # In update mode, do not update a record if it's ir.model.data is flagged as noupdate
#                 if mode == 'update' and noupdate_imd:
#                     return res_id2
#                 if not real_id2:
#                     self.clear_caches()
#                     cr.execute('delete from ir_model_data where id=%s', (imd_id2,))
#                     res_id = False
#                 else:
#                     assert model == real_model, "External ID conflict, %s already refers to a `%s` record,"\
#                         " you can't define a `%s` record with this ID." % (xml_id, real_model, model)
#                     res_id,action_id = res_id2,imd_id2

#         if action_id and res_id:
#             # if you wan't to update access rights every time then remove below line
#             # Add Below line for do not change rights after once create or update from front
#             if model != 'ir.model.access':
#                 model_obj.write(cr, uid, [res_id], values, context=context)
#             self.write(cr, uid, [action_id], {
#                 'date_update': time.strftime('%Y-%m-%d %H:%M:%S'),
#                 },context=context)
#         elif res_id:
#             model_obj.write(cr, uid, [res_id], values, context=context)
#             if xml_id:
#                 if model_obj._inherits:
#                     for table in model_obj._inherits:
#                         inherit_id = model_obj.browse(cr, uid,
#                                 res_id,context=context)[model_obj._inherits[table]]
#                         self.create(cr, uid, {
#                             'name': xml_id + '_' + table.replace('.', '_'),
#                             'model': table,
#                             'module': module,
#                             'res_id': inherit_id.id,
#                             'noupdate': noupdate,
#                             },context=context)
#                 self.create(cr, uid, {
#                     'name': xml_id,
#                     'model': model,
#                     'module':module,
#                     'res_id':res_id,
#                     'noupdate': noupdate,
#                     },context=context)
#         else:
#             if mode=='init' or (mode=='update' and xml_id):
#                 res_id = model_obj.create(cr, uid, values, context=context)
#                 if xml_id:
#                     if model_obj._inherits:
#                         for table in model_obj._inherits:
#                             inherit_id = model_obj.browse(cr, uid,
#                                     res_id,context=context)[model_obj._inherits[table]]
#                             self.create(cr, uid, {
#                                 'name': xml_id + '_' + table.replace('.', '_'),
#                                 'model': table,
#                                 'module': module,
#                                 'res_id': inherit_id.id,
#                                 'noupdate': noupdate,
#                                 },context=context)
#                     self.create(cr, uid, {
#                         'name': xml_id,
#                         'model': model,
#                         'module': module,
#                         'res_id': res_id,
#                         'noupdate': noupdate
#                         },context=context)
#         if xml_id and res_id:
#             self.loads[(module, xml_id)] = (model, res_id)
#             for table, inherit_field in model_obj._inherits.iteritems():
#                 inherit_id = model_obj.read(cr, uid, [res_id],
#                         [inherit_field])[0][inherit_field]
#                 self.loads[(module, xml_id + '_' + table.replace('.', '_'))] = (table, inherit_id)
#         return res_id

