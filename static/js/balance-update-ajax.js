// Update any balance displays on the page with the current character's balance, every BALANCE_UPDATE_TIME ms.

var BALANCE_UPDATE_TIME = 30000;
var BALANCE_URL;
var BALANCE_TIMER;

function balance_update() {
    if (BALANCE_URL==undefined) {
	alert("Balance update URL undefined! Cannot update balance!");
	return;
    }
    $.ajax({ url: BALANCE_URL,
	     success: function(data) {
		 $('.balance-display').html(data);
		 clearTimeout(BALANCE_TIMER);
		 BALANCE_TIMER = setTimeout("balance_update()", BALANCE_UPDATE_TIME);
	     }
	   });
	     
}

$(document).ready(balance_update);