# -*- coding: utf-8 -*-

{
    'name': 'Ob Project Enhance',
    'category': 'Project Managment',
    'summary': 'New features of project Managment',
    'version': '1.0',
    'description': """Project Managment""",
    'author': 'OfficeBrain',
    'depends': ['project','project_issue','project_timesheet','hr','hr_timesheet'],
    'data': [
        'security/ob_project_enhance_security.xml',
        'security/ir.model.access.csv',
        #'web_kanban.xml',
        'wizard/work_entry_user_view.xml',
        'project_view.xml',
        'estimated_task_view.xml',
        'work_entry_view.xml',
        'hr_timesheet_view.xml',
        #'project_issue_view.xml',
        'project_task_work_sequence.xml',
        'release_management_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
