var TIME = 0;

var TOOLTIP_LIST = [];
function make_tooltip(mouseover_id, tooltip_id) {
    var mo = $("#"+mouseover_id);
    var tt = $("#"+tooltip_id);

    TOOLTIP_LIST.push(tt);
    
    mo.mouseover(function(){
        tt.css({display:"none"}).fadeIn(TIME);
    }).mousemove(function(kmouse){
        tt.css({left:kmouse.pageX+15, top:kmouse.pageY+15});
    }).mouseout(function(){
        tt.fadeOut(TIME);
    });
}

 
$(window).load(function() {
    $(".tooltip").appendTo("#tooltips");
});