# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import tools
from openerp.osv import fields, osv

class user_group(osv.osv):
    _name = "user.group"
    _description = "User Access Control with RR"
    _auto = False
#     _rec_name = 'date'
    _columns = {
        'name': fields.char('Name', size=128,),
        'user_id': fields.many2one('res.users', 'Users', readonly=True),
        'group_id': fields.many2one('res.groups', 'Groups', readonly=True),
        'rule_id': fields.many2one('ir.rule', 'Rules', readonly=True),
        'model_id': fields.many2one('ir.model', 'Object', readonly=True),
        'r': fields.boolean('Read'),
        'w': fields.boolean('Write'),
        'c': fields.boolean('Create'),
        'u': fields.boolean('unlink'),        
    }
    _order = 'name desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'user_group')
        cr.execute("""
            create or replace view user_group as (
                select min(g.id) as id, g.name as name, ugr.uid as user_id,ugr.gid as group_id, r.rule_group_id as rule_id, i.model_id as model_id,i.perm_read as r,i.perm_write as w,i.perm_create as c,i.perm_unlink as u from res_groups_users_rel ugr join res_groups g on(ugr.gid=g.id) left join rule_group_rel r on (g.id=r.group_id) left join ir_rule i on (r.group_id=i.id)
group by ugr.uid, ugr.gid, g.name, r.rule_group_id,i.model_id,i.perm_read,i.perm_write,i.perm_create,i.perm_unlink
            )
        """)
user_group()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
















