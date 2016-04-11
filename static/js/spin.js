var CURRENT_DISPLAY = [-1,-1,-1];
var SPIN_TIMEOUTS = [null,null,null];
var SPIN_IN_PROGRESS = false;
var OUTCOME;
var REEL_STOP_TIME = 3000;

function stop_spin(slot, prize) {
    clearTimeout(SPIN_TIMEOUTS[slot]);
    display_prize(slot, prize);
}

function stop_all() {
    for (var i in SPIN_TIMEOUTS)
	clearTimeout(SPIN_TIMEOUTS[i]);
}

function spin(slot){
    //var curr_prize_index = prizepos[CURRENT_DISPLAY[slot]];
    //if (curr_prize_index == prizes.length-1) curr_prize_index = -1;
    display_prize(slot, prizes[Math.floor(Math.random()*prizes.length)][0]);
    SPIN_TIMEOUTS[slot] = setTimeout("spin("+slot+")", 100);
    
}

function display_prize(slot, prize){
    $("#pr_"+slot+"_"+CURRENT_DISPLAY[slot]).hide();
    $("#pr_"+slot+"_"+CURRENT_DISPLAY[slot]+"_o").hide();
    $("#pr_"+slot+"_"+prize).show();
    $("#pr_"+slot+"_"+prize+"_o").show();
    CURRENT_DISPLAY[slot] = prize;
}

function spin_all(){
    for (var i in CURRENT_DISPLAY) spin(i);
}

function process_outcome() {
    var win = true;
    for (var i in OUTCOME) {
	if (OUTCOME[0]!=OUTCOME[i]){
	    win = false;
	    break;
	}
    }

    if (win) {
	post_msg("Congratulations! You won: " + prizes[prizepos[OUTCOME[0]]][1]);
    } else {
	append_msg("Bad luck, no match. Try again!");
    }
    balance_update();

    SPIN_IN_PROGRESS = false;
}

function dramatic_stop(slot) { 
    stop_spin(slot, OUTCOME[slot]);
    append_msg(prizes[prizepos[OUTCOME[slot]]][1] + "... ");
    if ((slot+1)==OUTCOME.length)
	process_outcome()
    else
	setTimeout('dramatic_stop('+(slot+1)+')', REEL_STOP_TIME);
}

function process_data(data) {
    var bad_request = false;
    if (data=="$$$") {
	post_msg("You cannot afford to spin this!");
	bad_request = true;
    }
    if (data=="noauth") {
	post_msg("You still haven't logged in!");
	bad_request = true;
    }
    if (data=="disabled") {
	post_msg("The reel has been disabled. Sorry! Check the reel details for more info.");
	bad_request = true;
    }
    if (bad_request) {
	SPIN_IN_PROGRESS = false;
        stop_all();	
	return;
    }
    OUTCOME = eval('('+ data + ')');
    post_msg(" ");
    setTimeout('dramatic_stop(0)',REEL_STOP_TIME);
}

function go() {
    if (SPIN_IN_PROGRESS) return;
    if (noauth) {
	post_msg("Ship spinning requires logging in. Please do so.");
	return;
    }
    if (disabled) {
	post_msg("This station is currently disabled. Sorry! See the station details for more info.");
	return;
    }
    spin_all();
    SPIN_IN_PROGRESS = true;
    $.ajax({url: '?spin_ajax',
	    success: process_data,
	    error: function(){alert("There was an error: "+data);}
	   });
}

function write_msg(msg){
    $("#spinstatus-display").html(msg);
}

function append_msg(msg){
    $("#spinstatus-display").html($("#spinstatus-display").html()+msg);
}

function post_msg(msg){
    oldmsg = $("#spinstatus-display").html();
    $("#spinstatus-log p").first().html(oldmsg);
    oldlog = $("#spinstatus-log").html();
    newlog = "<p class='hiding'></p>"+oldlog;
    $("#spinstatus-log").html(newlog);
    write_msg(msg);
    $("#spinstatus-log p.hiding").slideDown();
    $("#spinstatus-log p.hiding").removeClass('hiding');
}

function prep_spin(){
    for (var i in CURRENT_DISPLAY){
	var prize = Math.floor(Math.random()*prizes.length);
	display_prize(i, prizes[prize][0]);
    }
}

$(document).ready(prep_spin);

///////////// Lever ///////////////

var lever_origpos;

function stop_drag() {
    var lever = $("#lever");
    var lever_newpos = lever.offset().top;
    if ((lever_newpos-lever_origpos + lever.height())/lever.parent().height() > 0.9)
    {
	go();
    }
    
    lever.animate({top: '0px'}, 1000);
}

function prep_lever() {
    lever_origpos = $("#lever").offset().top
    $("#lever").draggable({axis: "y",
			   snap: true,
			   containment: "#lever-container",
			   stop: stop_drag});
}

$(document).ready(prep_lever);