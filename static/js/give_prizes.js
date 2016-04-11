function process_data(data) {
    var outcome = eval('('+ data + ')');
    var id = outcome['awardid'];
    if (outcome['updated']) {
	$("#done-"+id).html('Done!');
    } else {
	$("#done-"+id).html('Someone else did this first!');
    }
    
}

function processDone(awardid) {
    $.ajax({url: prize_ajax_url+'?id='+awardid,
     	    success: process_data,
     	    error: function(){alert("There was an error: "+data);}
     	   });

}