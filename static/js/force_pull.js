function process_data(data) {
    if (data=="success") {
	$("#pull_result").html('Success! Refresh for new wallet info');
    }
    else {
	$("#pull_result").html('No new rows. There were either no new donations, or the API is caching.');
    }
}

function processPull() {
    $.ajax({url: pull_ajax_url,
     	    success: process_data,
     	    error: function(){alert("There was an error: "+data);}
     	   });

}