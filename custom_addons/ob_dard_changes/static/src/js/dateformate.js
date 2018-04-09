openerp.ob_dard_changes = function (session) {
	var mail = session.mail
	
	mail.MessageCommon.include({
		format_data:function(){
            this.date = this.date ? session.web.str_to_datetime(this.date) : false;
            this.display_date = this.date.toString('ddd MMM dd yyyy HH:mm');
            if (this.author_avatar) {
                this.avatar = "data:image/png;base64," + this.author_avatar;
            } else if (this.type == 'email' && (!this.author_id || !this.author_id[0])) {
                this.avatar = ('/mail/static/src/img/email_icon.png');
            } else if (this.author_id && this.template != 'mail.compose_message') {
                this.avatar = mail.ChatterUtils.get_image(this.session, 'res.partner', 'image_small', this.author_id[0]);
            } else {
                this.avatar = mail.ChatterUtils.get_image(this.session, 'res.users', 'image_small', this.session.uid);
            }
            if (this.author_id && this.author_id[1]) {
                var parsed_email = mail.ChatterUtils.parse_email(this.author_id[1]);
                this.author_id.push(parsed_email[0], parsed_email[1]);
            }
            if (this.partner_ids && this.partner_ids.length > 3) {
                this.extra_partners_nbr = this.partner_ids.length - 3;
                this.extra_partners_str = ''
                var extra_partners = this.partner_ids.slice(3);
                for (var key in extra_partners) {
                    this.extra_partners_str += extra_partners[key][1];
                }
            }
        },
	})	
}
