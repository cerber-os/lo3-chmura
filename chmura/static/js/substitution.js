function populateDaySelect() {
	var select = document.getElementById("dayselect");
	
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
		select.appendChild(option);
		
		day.setDate(day.getDate() + 1);
	}
}
function handleSubstitutionDaySelectUpdate(select) {
	var date = select.selectedOptions[0].value;
	window.location.search = "?date=" + date;
}

function handleGroupSelectUpdate() {
	var select = document.getElementById("substitutiongroupselect");
	if (!select) return;
	
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
	
	if (hiddenWrappers == wrappers.length)
		document.getElementById("nochosensubstitution").style.display = "block";
	else
		document.getElementById("nochosensubstitution").style.display = "none";
}

window.onload = function() {
	populateDaySelect();
	handleGroupSelectUpdate();
}