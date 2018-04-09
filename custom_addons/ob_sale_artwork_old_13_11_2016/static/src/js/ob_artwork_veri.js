var attach = {};
function readerHandler(e2) 
{ 
  attach['file_data'] = e2.target.result.split(',')[1];
  console.log("this valsss ",attach['file_data']);
}

function handleFileSelect(e1)
{
  var fileobj = $('#attach')[0].files[0]; 
  var fr = new FileReader();
  fr.onload = readerHandler;
  fr.readAsDataURL(fileobj); 
}
window.onload=function()
{
  var x = document.getElementById("attach");
  if (x){
    x.addEventListener('change', handleFileSelect, false);
  }
};


function validateForm(fileid){
    
    var artworkReplyForm = document.forms["artwork_veri_form"];
    
    var cmnt = artworkReplyForm.elements["cmnt"].value;
    var res_id = artworkReplyForm.elements["res_id"].value;
    var virtual_state = artworkReplyForm.elements["virtual_state"].value;
    var data_key = artworkReplyForm.elements["data_key"].value;
    var db = artworkReplyForm.elements["db"].value;
    var uname = artworkReplyForm.elements["uname"].value.trim();
    
    var vals = {};
    var url;
    var dic_new = {'cmnt':String(cmnt), 'uname':String(uname), 'res_id':String(res_id), 'db':String(db), 'virtual_state':String(virtual_state), 'data_key': String(data_key)};
    var _validFileExtensions = ["jpg", "jpeg", "bmp", "gif", "png","jfif","tif","tiff","rif","riff","ai","eps","pdf"];
    
    attach['filename'] = $('#attach')[0].files[0] ? $('#attach')[0].files[0].name : null;
    if(!uname)
        alert("Please fill required details");
    else if (uname.length > 300)
        alert("Maximum limit of character is reached (Max : 300 Char)");
    else{
        if ($('#attach')[0].files && $('#attach')[0].files[0]) {
           var name_file = attach['filename'].toLowerCase().split('.').pop();
           var self = this;
           if (_validFileExtensions.indexOf(name_file) < 0){
                  alert("Only  jpg, jpeg, bmp, gif, png, jfif, tiff, rif, ai, eps allowed." );
                  return window.location;
            }
            if(($('#attach')[0].files[0]).size/1048576  > 20){
                alert("File is too large to upload (Max : 20 MB)");
                return window.location;
            }
            else{
                var dic_new1 = {'attach': attach['file_data'],'name' : String(attach['filename']),'cmnt':String(cmnt), 'uname':String(uname), 'res_id':String(res_id), 'db':String(db), 'virtual_state':String(virtual_state), 'data_key': String(data_key)};
                openerp.session.rpc('/Verification/submit', {'data': dic_new1}).then(function(status) {
                    if (status){
                        url = "/Verification/submitresponse";
                        return window.location = url; 
                    }
                   
                });
            }
        }else {
            openerp.session.rpc('/Verification/submit', {'data': dic_new}).then(function(status) {
                if (status){
                        url = "/Verification/submitresponse";
                        return window.location = url; 
                }
            });
        }
    }
   
};