function populateDaySelect() {
	var selects = document.getElementsByClassName("dayselect");
	
	var day = new Date();
	var dayNames = ["Niedziela", "Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota"];
	
	var urlDate = getHttpGetParameter("date");
	var selectedDate = urlDate ? new Date(getHttpGetParameter("date")) : new Date();
	
	for (var i = 0; i <= 7; i++) {
		var dayString = ("0" + day.getDate()).substr(-2);
		var monthString = ("0" + (day.getMonth() + 1)).substr(-2)
		var yearString = day.getFullYear();
		
		var dateString = dayNames[day.getDay()] + ", " + dayString + "." + monthString + "." + yearString;
		var isoString = yearString + "-" + monthString + "-" + dayString;
		
		var option = document.createElement("option");
		option.setAttribute("value", isoString);
		option.innerText = dateString;
		if (day.getDate() == selectedDate.getDate()) option.setAttribute("selected", "selected");
		for (var j = 0; j < selects.length; j++) selects[j].appendChild(option.cloneNode(true));
		
		day.setDate(day.getDate() + 1);
	}
}
function handleSubstitutionDaySelectUpdate(select) {
	var date = select.selectedOptions[0].value;
	window.location.search = "?date=" + date;
}

function selectSavedGroup() {
	var group = getCookie("lastsubstitutiongroup");
	
	var selects = document.getElementsByClassName("substitutiongroupselect");
	if (selects.length == 0) return;
	
	for (var i = 0; i < selects.length; i++)
		for (var j = 0; j < selects[i].options.length; j++)
			if (selects[i].options[j].value == group) {
				selects[i].selectedIndex = j;
				handleGroupSelectUpdate(selects[0]);
				break;
			}
}
function handleGroupSelectUpdate(updatedSelect) {
	var selects = document.getElementsByClassName("substitutiongroupselect");
	if (selects.length == 0) return;
	
	var select;
	if (updatedSelect) {
		select = updatedSelect;
		
		for (var i = 0; i < selects.length; i++)
			selects[i].selectedIndex = select.selectedIndex;
	}
	
	var hiddenWrappers = 0;
	
	var wrappers = document.getElementsByClassName("substitutiontablewrapper");
	for (var i = 0; i < wrappers.length; i++) {
		if (select.value == "*") {
			wrappers[i].style.display = "";
			continue;
		}
		
		var groups = wrappers[i].getAttribute("data-group").split(", ");
		if (groups.indexOf(select.value) != -1) wrappers[i].style.display = "";
		else {
			wrappers[i].style.display = "none";
			hiddenWrappers++;
		}
	}
	
	if (hiddenWrappers == wrappers.length && wrappers.length > 0)
		document.getElementById("nochosensubstitution").style.display = "block";
	else
		document.getElementById("nochosensubstitution").style.display = "none";
	
	setCookie("lastsubstitutiongroup", select.value, 31536000000);
}

window.onload = function() {
	populateDaySelect();
	selectSavedGroup();
}