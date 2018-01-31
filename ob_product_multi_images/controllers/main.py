
from openerp import http
from openerp.addons.web.controllers.main import Binary
openerpweb = http
import simplejson
import time
import openerp
import os
import StringIO

class Binary_multi(Binary):
    _cp_path = '/Binary'
    @http.route('/web/binary/upload_image_multi', type='http', auth="public")
    def upload_image_multi(self, req, callback, ufile):
        # TODO: might be useful to have a configuration flag for max-length file uploads
        out = """<script language="javascript" type="text/javascript">
                    var win = window.top.window;
                    win.jQuery(win).trigger(%s, %s);
                </script>"""
        args = []

        ext2conttype = ["jpg", "jpeg", "bmp", "gif", "png","jfif","tif","tiff","riff","ai","rif","eps","pdf"]
        filename = ufile.filename.lower()
        file_name = filename[filename.rfind(".")+1:]

        if ufile and file_name in ext2conttype:
            data = ufile.read()
            if data:
                current_dat_time = time.strftime("%d%m%y%H%M%S")
                file_name = current_dat_time + "_" + ufile.filename
                addons_path = openerpweb.addons_manifest['web']['addons_path'] + "/web/static/src/img/image_multi/"
                if not os.path.isdir(addons_path):
                    os.mkdir(addons_path)
                addons_path += file_name
                buff = StringIO.StringIO()
                buff.write(data)
                buff.seek(0)
                file_name = "/web/static/src/img/image_multi/" + file_name
                file = open(addons_path, 'wb')
                file.write(buff.read())
                file.close()
                args = [len(data), file_name, ufile.content_type, ufile.filename, time.strftime("%m/%d/%Y %H:%M:%S")]
        else:
            args = []
        return out % (simplejson.dumps(callback), simplejson.dumps(args))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: