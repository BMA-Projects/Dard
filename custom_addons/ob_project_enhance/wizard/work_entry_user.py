from openerp import models,fields ,api
from datetime import datetime
from openerp.tools.translate import _
from openerp.exceptions import Warning

class work_entry_user(models.TransientModel):
    """Work entry by user"""
    _name = 'work.entry.user'




    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals and vals.has_key('time_spent') and vals.get('time_spent') <= 0.0:
            raise Warning(_('Time Spend must be greater than Zero (0)'))
        return super(work_entry_user, self).create(cr, uid, vals, context=context)


    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(work_entry_user, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id') and context.get('active_model') == 'task.estimated':
            rec = self.pool.get(context.get('active_model')).browse(cr, uid, context.get('active_id'), context=context)
            res['task_number'] = rec.task_number or False
            res['estimated_task_type_id'] = rec.estimated_task_type_id.id or False
        return res


    def work_entry_log(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
       
        project_task_obj = self.pool.get('project.task')
        project_task_work_obj = self.pool.get('project.task.work')
        task_estimated_obj = self.pool.get('task.estimated')
        task_sequence_obj = self.pool.get('project.task.sequence')
        
        if context.get('active_ids'):
            vals = {}
            vals_seq = {}
            
            estimated_vals = {}
            brw_estimated = task_estimated_obj.browse(cr, uid, context.get('active_ids'), context=context)
            estimated_task_id = brw_estimated.estimated_task_id
            total_time_spent = float(brw_estimated.total_time_spent or 0)

            data = self.read(cr, uid, ids)[0]

            seq_ids = task_sequence_obj.search(cr, uid, [('name', '=', data['task_number'])], context=context)
#            if not seq_ids:
#                vals_seq['task_estimated_id'] = context['active_id']
#                vals_seq['name'] = data['task_number'] or False
#                seq_id = task_sequence_obj.create(cr, uid,  vals_seq, context=context)
#                vals['task_sequence_id'] = seq_id
#            else:
#                vals['task_sequence_id'] = seq_ids[0]
            
            vals['name'] = data['name'] or False

            #vals['task_number'] = data['task_number'] or False
            vals['hours'] = data['time_spent'] or 0
            #vals['task_type_id'] = data['task_type_id'][0] or False
            vals['work_type_id'] = data['work_type_id'][0] or False
            vals['task_id'] = estimated_task_id.id or False
            vals['user_id'] = uid
            vals['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            vals['task_sequence_id'] = seq_ids[0]
            vals['estimated_task_type_id'] = data['estimated_task_type_id'][0] or False

            project_task_work_obj.create(cr, uid,  vals, context=context)
            estimated_vals['total_time_spent'] = float(data['time_spent']) + total_time_spent
            task_estimated_obj.write(cr, uid, context.get('active_ids'), estimated_vals, context)

        return True


    task_number = fields.Char('Task ID')
    time_spent = fields.Float('Time Spent')
    task_type_id = fields.Many2one('project.task.type', 'Type of Task')
    work_type_id = fields.Many2one('project.work.type', 'Type of Work')
    name = fields.Text('Work Summary')
    user_id = fields.Many2one('res.users', string='User',default=lambda self: self.env.user)
    estimated_task_type_id = fields.Many2one('estimated.task.type', 'Task type')
