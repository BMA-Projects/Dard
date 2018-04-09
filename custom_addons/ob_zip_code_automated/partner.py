# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
#from openerp.osv import fields, osv, orm
from openerp import models, fields, api, _
import urllib2
import simplejson as json
#http://maps.googleapis.com/maps/api/geocode/json?address=249201&sensor=true
#url = urllib2.Request("http://maps.googleapis.com/maps/api/geocode/json?address=" + zip + "&sensor=true")
#url = http://zip.elevenbasetwo.com/v2/IN/249201
#url = http://zip.elevenbasetwo.com/v2/CA/9201
#url = "http://maps.googleapis.com/maps/api/geocode/json?address=" + zip + "&sensor=true"
#url = "http://zip.elevenbasetwo.com/v2/US/"+ zip
#url = "http://zip.elevenbasetwo.com/v2/CA/"+ zip


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.onchange('zip')
    def onchange_zip(self):
        value = {}
        zip = self.zip
        if zip:
            zip = str(''.join(e for e in zip if e.isalnum()))

        # if not zip:
        #     raise osv.except_osv(_('Error!'), _('Enter Zip Code'))

        country_obj = self.env['res.country']
        state_obj = self.env['res.country.state']

        try:

            url = "http://zip.getziptastic.com/v2/US/" + str(zip)
            the_page = json.load(urllib2.urlopen(url))
            # print "the page =======", the_page
            # value = the_page.copy()
            # print "valueeeeeeeees :::::", value
            if the_page:
                country_id = country_obj.search([('code', '=', 'US')])
                state_id = state_obj.search([('name', '=', the_page['state'])])
                # print "the state_id -------", state_id
                if not state_id:
                    state_values = {
                        'name' : the_page['state'],
                        'code' : the_page['state_short'],
                        'country_id' : country_id[0].id,
                    }
                    # print "state_value;;;;;;;;;;", state_values
                    state_ids = state_obj.create(state_values)
                    # print "state_ids|||||||", state_ids
                    value['state_id'] = state_ids.id
                    self.state_id = state_ids.id
                else:
                    value['state_id'] = state_id[0]
                    self.state_id = state_id[0]
                    self.country_id = country_id[0]
                return {'value': value}
        except:
            self.state_id = False
            self.country_id = False
            pass

        try:

            url = "http://zip.getziptastic.com/v2/CA/" + str(zip)
            the_page = json.load(urllib2.urlopen(url))
            if the_page:
                country_id = country_obj.search([('code', '=', 'CA')])
                state_id = state_obj.search([('name', '=', the_page['state'])])
                if not state_id:
                    state_values = {
                        'name' : the_page['state'],
                        'code' : the_page['state_short'],
                        'country_id' : country_id[0].id,
                    }
                    state_ids = state_obj.create(state_values)
                    self.state_id = state_ids.id
                    value['state_id'] = state_ids
                else:
                    value['state_id'] = state_id[0]
                    self.state_id = state_id[0]
                    self.country_id = country_id[0]
                return {'value': value}
        except:
            self.state_id = False
            self.country_id = False
            pass

        value['state_id'] = False
        value['country_id'] = False
        return {'value': value}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
