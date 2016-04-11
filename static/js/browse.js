
function show_values(){
    $("#meta_value").html("");
    var attrib_id = $("#attrib").val();
    var xmlstr, val_id, val_name;
    xmlstr += "<option value=\"0\" disabled=\"yes\" selected=\"yes\">Select a value</option>";
    for (i in attrib_values[attrib_id]) {
	val_id = attrib_values[attrib_id][i][0];
	val_name = attrib_values[attrib_id][i][1];
	xmlstr += "<option value=\""+val_id+"\">"+val_name+"</option>";
    }
    $("#meta_value").html(xmlstr);
    $("#meta_value").trigger("liszt:updated");
}

function browse_submit() {
    var att_id = $("#attrib").val();
    var val_id = $("#meta_value").val();
   
    if (att_id==0 || att_id==null ||
	val_id==0 || val_id==null)
	return false;
    
    next_url = base_url + "/" + att_id + "/" + val_id;
    window.location = next_url;
    
    return false;
}

function browse_all() {
    next_url = base_url + "/all";
    window.location = next_url;
    return false;
}

function queried_values() {
    if (query_att>0) {
	$("#attrib").val(query_att);
	show_values();
	$("#meta_value").val(query_val);
    }
}

function toggle_show(reelid) {
    var el = $("#details_"+reelid);
    if (el.css('display')=="none") {
	el.slideDown();
    }
    else {
	el.slideUp();
    }
}

function ready_browse(){
    $("#attrib").change(show_values);
    $("#browse_form").submit(browse_submit);
    $("#browse_all").click(browse_all);
    queried_values();
    $("select").chosen();
    $(".innerlink").click(function(e) {
	var reelid = $(this).attr("reelid");
	toggle_show(reelid);
    });
}

$(document).ready(ready_browse);