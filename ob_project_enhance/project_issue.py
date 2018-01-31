from openerp import models, fields, api, _

#class issue_severity(models.Model):
#	"Issue Severity"
#	_name = 'issue.severity'
#
#	name = fields.Char("Severity")
	
class project_issue(models.Model):
    """Project Management"""
    _inherit = 'project.issue'

    #severity_id = fields.Many2one('issue.severity', "Severity")
    #'task_id': fields.many2one('project.task', 'Task', domain="[('project_id','=',project_id)]"),
    created_by = fields.Many2one('res.users', string= "Raised By", default=lambda self: self.env.user,track_visibility='onchange')
    produced_by = fields.Many2one('res.users', string= "Produced By", default=lambda self: self.env.user,track_visibility='onchange')
    
