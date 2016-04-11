
function show_dropmenu() {
    $("div#dropitems").show();
}
function hide_dropmenu() {
    $("div#dropitems").hide();
}

$(document).ready( function() {
    $("div#dropmenu").mouseenter(show_dropmenu);
    $("div#dropmenu").mouseleave(hide_dropmenu);
});
