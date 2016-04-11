var TIME = 0;

function make_tooltip(mouseover_id, tooltip_id) {
    var mo = $("#"+mouseover_id);
    var tt = $("#"+tooltip_id);
    
    mo.mouseover(function(){
        tt.css({display:"none"}).fadeIn(TIME);
    }).mousemove(function(kmouse){
        /*tt.css({left:kmouse.pageX+15, top:kmouse.pageY+15});*/
	tt.position({my:"left+10 top+10", at:"right bottom", of:kmouse, collision:"fit"});
    }).mouseout(function(){
        tt.fadeOut(TIME);
    });
}

