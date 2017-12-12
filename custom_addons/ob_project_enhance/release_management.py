from openerp import models, fields, api, _
from datetime import datetime,date
from openerp.exceptions import Warning
from openerp.tools.translate import _
from openerp.exceptions import Warning
from lxml import etree
from openerp.osv.orm import setup_modifiers

class release_management(models.Model):
	
	_name = "release.management"

	_description = "Project Release"

	_inherit = ['mail.thread', 'ir.needaction_mixin']

	name = fields.Char('Description', required=True,track_visibility='onchange')
	release_date = fields.Date('Release Date', required=True)
	project_id= fields.Many2one('project.project', string= "Project", required=True)
	start_date = fields.Date('Expected Start Date')
	end_date = fields.Date('Expected End Date')
	member_ids = fields.Many2many('res.users', 'release_user_rel', string='Team')
	story_ids = fields.Many2many('project.task', 'release_task_rel', string='Stories')
	state = fields.Selection([('planning','Planning'),('progress','In Progress'),('waiting','Ready For Release'),('progress_release','Release in Progress'),('live','Live'),('cancel','Cancel')],'Status', required=True, copy=False, default='planning',track_visibility='onchange')

	@api.multi
	def set_planning(self):
		return self.write({'state': 'planning'})

	@api.multi
	def set_progress(self):
		return self.write({'state': 'progress'})

	@api.multi
	def set_waiting(self):
		return self.write({'state': 'waiting'})

	@api.multi
	def set_progress_release(self):
		return self.write({'state': 'progress_release'})
	@api.multi
	def set_live(self):
		return self.write({'state': 'live'})

	@api.multi
	def set_cancel(self):
		return self.write({'state': 'cancel'})

	@api.multi
	@api.onchange('project_id')
	def onchange_project_id(self):
		self.story_ids = False

	@api.model
	def create(self, vals):
		pro_id = vals['project_id']
		obj_users = self.env['res.users']
		if pro_id:
			if vals.has_key('member_ids') or vals.has_key('story_ids'):
				if  vals.has_key('member_ids'):
					if vals['member_ids'][0][2] == []:
						raise Warning(_('Atleast one Team Member should be added!!!'))
				if vals['member_ids']:
					message_follower_ids = []
					if vals['member_ids'][0][2]:
						for new_member_id in vals['member_ids'][0][2]:
							partner_id = obj_users.browse(new_member_id).partner_id or False
							if partner_id:
								message_follower_ids.append(partner_id.id)
						vals['message_follower_ids'] = message_follower_ids
				
				if vals.has_key('story_ids'):
					if vals['story_ids'][0][2] == []:
						raise Warning(_('Atleast one story should be selected!!!'))	 
		if vals['end_date']:
			if vals['end_date'] > vals['release_date']:
				raise Warning(_('Expected End Date Should not be grater than Release Date!!!'))
		if vals['start_date']:
			if vals['start_date'] > vals['release_date']:
				raise Warning(_('Expected Start Date Should not be grater than Release Date!!!'))
			if vals['end_date']:
				if vals['start_date'] > vals['end_date']:
					raise Warning(_('Expected Start Date Should not be grater than Expected End Date!!!'))
		new_id = super(release_management,self).create(vals)
		# self.message_post(body=_("Release created"))
		return new_id 

	@api.multi
	def write(self, vals):
		obj_users = self.env['res.users']
		if vals.has_key('member_ids') or vals.has_key('story_ids'):
			if  vals.has_key('member_ids'):
				if vals['member_ids'][0][2] == []:
					raise Warning(_('Atleast one Team Member should be added!!!'))
				if vals['member_ids']:
					message_follower_ids = []
					if vals['member_ids'][0][2]:
						for new_member_id in vals['member_ids'][0][2]:
							# partner_id = obj_users.browse('new_member_id').partner_id or False
							partner_id = obj_users.browse(new_member_id).partner_id or False
							if partner_id:
								message_follower_ids.append(partner_id.id)
						vals['message_follower_ids'] = message_follower_ids
			if vals.has_key('story_ids'):
				if vals['story_ids'][0][2] == []:
					raise Warning(_('Atleast one story should be selected!!!'))	 
		if vals.has_key('end_date') or vals.has_key('start_date'):
			if not vals.has_key('release_date'):
				if vals.has_key('end_date'):
					if vals['end_date'] > self.release_date:
						raise Warning(_('Expected End Date Should not be grater than Release Date!!!'))
					if not vals.has_key('start_date'):
						if vals['end_date'] < self.start_date:
							raise Warning(_('Expected Start Date Should not be grater than Expected End Date!!!'))
					if vals.has_key('start_date'):
						if vals['end_date'] < vals['start_date']:
							raise Warning(_('Expected Start Date Should not be grater than Expected End Date!!!'))
				if vals.has_key('start_date'):
					if vals['start_date'] > self.release_date:
						raise Warning(_('Expected Start Date Should not be grater than Release Date!!!'))
					if not vals.has_key('end_date'):
						if vals['start_date'] > self.end_date:
							raise Warning(_('Expected Start Date Should not be grater than Expected End Date!!!'))
					if vals.has_key('end_date'):
						if vals['end_date'] < vals['start_date']:
							raise Warning(_('Expected Start Date Should not be grater than Expected End Date!!!'))
			if vals.has_key('release_date'):
				if vals.has_key('start_date'):
					if vals['start_date'] > vals['release_date']:
						raise Warning(_('Expected Start Date Should not be grater than Release Date!!!'))
				if vals.has_key('end_date'):
					if vals['end_date'] > vals['release_date']:
						raise Warning(_('Expected End Date Should not be grater than Release Date!!!'))
		if vals.has_key('release_date'):
			if not vals.has_key('start_date'):
				if vals['release_date'] > self.start_date:
					raise Warning(_('Expected Start Date Should not be grater than Release Date!!!'))
			if vals.has_key('end_date'):
				if vals['end_date'] > vals['release_date']:
					raise Warning(_('Expected End Date Should not be grater than Release Date!!!'))

		return super(release_management,self).write(vals)

	@api.multi
	def copy(self,default):
		raise Warning(_("Release Record Can not be Duplicated"))

class project_task(models.Model):
	_inherit = "project.task"

	@api.returns('self')
	def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
		res = super(project_task,self).search(cr, uid, args=args, offset=offset, limit=limit, order=order, context=context, count=count)
		if count:
			return res
		release_management_obj = self.pool.get('release.management')
		project_id, domain, used_story = None, [], []
		if args:
			for tup in args:
				if tup[0] == 'project_id': project_id = tup[2]
		if project_id:
			domain = [('project_id','=',project_id)]
		release_ids = release_management_obj.search(cr, uid, domain, context=context)
		story_ids = release_management_obj.read(cr, uid, release_ids, ['story_ids'], context=context)
		for story in story_ids:
			used_story.extend(story.get('story_ids'))
		return_ids = list(set(res).difference(set(used_story)))
		return return_ids

	@api.model
	def create(self,vals):
		if self._context.has_key('current_model') and self._context['current_model'] == 'release.management' :
			raise Warning(_('you are not allowed to create new story!!!'))	
		else:	
			res = super(project_task,self).create(vals)
		return res

class res_users(models.Model):
	_inherit= 'res.users'

	@api.model
	def create(self,vals):
		if self._context.has_key('current_model') and self._context['current_model'] == 'release.management' :
			raise Warning(_('you are not allowed to create new User!!!'))	
		else:
			res = super(res_users,self).create(vals)
		return res
				


# {'message_follower_ids': False, 'categ_ids': [[6, False, []]], 'sequence': 10, 'date_end': False, 'partner_id': False, 'message_ids': False, 'actual_qa_demo_date': False, 'user_id': 1, 'sale_line_id': False, 'actual_expected_external_demo_date': False, 'date_start': False, 'company_id': 1, 'priority': '0', 'demo_status': False, 'project_id': False, 'date_last_stage_update': '2015-02-05 17:52:48', 'expected_qa_demo_date': False, 'description': 'dasda', 'act_end_date': False, 'kanban_state': 'normal', 'child_ids': [[6, False, []]], 'initial_planned_hours': 0, 'work_ids': [], 'parent_ids': [[6, False, []]], 'act_start_date': False, 'estimated_id': [], 'stage_id': 1, 'name': 'asdasd', 'date_deadline': False, 'reviewer_id': 1, 'expected_external_demo_date': False, 'sprint_started': False, 'remaining_hours': 0}




