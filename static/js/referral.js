$(document).ready( function() {

    $("#referral_explanation a").click(function() {
	$("#referral_explanation a").hide();
	$("#referral_explanation span").css("visibility", "");
    });

    $("a#claimrefs").click(function() {
	$.ajax({url: '?claim_ajax',
		success: function() {
		    $("a#claimrefs").replaceWith("<em>Claimed! Refreshing...</em>");
		    location.reload();
		},
		error: function(data){alert("There was an error: "+data);}
	       });

    });

    $("#referral_bonuses a.claim").click(function() {
	var prize = $(this).attr("prize");
	$.ajax({url: '?claim_bonus_prize_ajax&prize='+prize,
		success: function(data) {
		    if (data=="already claimed") {
			alert("You already claimed that prize!");
		    } 
		    else if (data=="not enough referrals") {
			alert("You do not have enough referrals for that prize!");
		    }
		    else {
			location.reload();
		    }
		},
		error: function(data){alert("There was an error: "+data);}
	       });

    });


});