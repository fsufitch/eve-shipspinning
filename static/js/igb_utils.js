function show_typeid(typeid) {
    if (typeof CCPEVE != 'undefined') { // If we're in the in-game browser
	CCPEVE.showInfo(typeid);
    }
    else {
	window.open("http://games.chruker.dk/eve_online/item.php?type_id="+typeid);
    }
}