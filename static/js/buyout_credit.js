function process_price(data) {
    var outcome = eval('('+ data + ')');
    var awid = outcome['awid'];
    var price = outcome['price'];
    $("#get_price_"+awid).hide();
    $("#confirm_"+awid).show();
    $("#price_"+awid).html(price);
}

function get_price(awid) {
    $.ajax({url: price_ajax_url+'?awid='+awid,
     	    success: process_price,
     	    error: function(){alert("There was an error: "+data);}
     	   });
    
}

function process_buyout(data) {
    var outcome = eval('('+ data + ')');
    var awid = outcome['awid'];
    var already_processed = outcome['already_processed'];
    if (!already_processed) {
	$("#confirm_"+awid).html("Credited!");
	balance_update();
    }
    else {
	$("#confirm_"+awid).html("This prize was already delivered/claimed!");
    }
	
}

function buyout(awid) {
    $("#confirm_"+awid).html("Processing...");
    $.ajax({url: buyout_ajax_url+'?awid='+awid,
     	    success: process_buyout,
     	    error: function(){alert("There was an error: "+data);}
     	   });
}
