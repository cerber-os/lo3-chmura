function closeOverlay(div, event) {
	if (div)
		if (event.target != div) {
			return;
		}
		
	document.getElementById("overlay").style.visibility = "hidden";
}

function handleLocationSelectUpdate(select) {
	window.location = select.selectedOptions[0].value;
}
function toggleHeaderMenu() {
	var menu = document.getElementById("headermenu");
	
	if (menu.style.display == "block")
		menu.style.display = "none";
	else
		menu.style.display = "block";
}

function setCookie(name, value, milliseconds) {
	if (milliseconds) {
		var date = new Date();
		date.setTime(date.getTime() + milliseconds);
		document.cookie = encodeURIComponent(name) + "=" + encodeURIComponent(value) + "; expires=" + date.toUTCString() + "; path=/";
	}
	else
		document.cookie = encodeURIComponent(name) + "=" + encodeURIComponent(value) + "; path=/";
}
function getCookie(desiredName) {
	var entries = document.cookie.split(/; ?/);
	
	for (var i in entries) {
		var name = entries[i].substr(0, entries[i].indexOf("="));
		name = decodeURIComponent(name);
		
		if (name != desiredName) continue;
		
		var value = entries[i].substr(entries[i].indexOf("=") + 1);
		value = decodeURIComponent(value);
		
		return value;
	}
	
	return null;
}
function eraseCookie(name) {
	setCookie(name, "", -1);
}

function getHttpGetParameter(name) {
	name = name.replace(/[\[\]]/g, "\\$&");

	var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)")
	var results = regex.exec(window.location.href);

	if (!results) return null;
	if (!results[2]) return "";
	
	return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function handleOnKeyDown(event) {
	if (event.keyCode == 27) closeOverlay();
}
window.addEventListener("keydown", handleOnKeyDown);