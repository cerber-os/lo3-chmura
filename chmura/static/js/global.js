function closeOverlay(div, event) {
	if (div)
		if (event.srcElement != div)
			return;
		
	document.getElementById("overlay").style.visibility = "hidden";
}

window.onkeydown = function(event) { if (event.keyCode == 27) closeOverlay(); }