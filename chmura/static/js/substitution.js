function handleSubstitutionDaySelectLoad() {
	var selects = document.getElementsByClassName("dayselect");
	
	for (var i = 0; i < selects.length; i++)
		if (selects[i].selectedOptions[0].value != selects[i].getAttribute("data-date"))
			handleSubstitutionDaySelectUpdate(selects[i]);
}
function handleSubstitutionDaySelectUpdate(select) {
	var date = select.selectedOptions[0].value;
	window.location.search = "?date=" + date;
}

function selectSavedFilterIndex() {
	var index = getCookie("lastsubstitutionfilterindex");
	if (index == null) return;
	
	var selects = document.getElementsByClassName("substitutiongroupselect");
	if (selects.length == 0) return;
	
	for (var i = 0; i < selects.length; i++)
		selects[i].selectedIndex = Number(index);
	
	handleFilterSelectUpdate(selects[0]);
}
function handleFilterSelectUpdate(updatedSelect) {
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
		
		if (select.selectedOptions[0].getAttribute("data-type") == "class") {
			
			var groups = wrappers[i].getAttribute("data-group").split(", ");
			if (groups.indexOf(select.value) != -1) wrappers[i].style.display = "";
			else {
				wrappers[i].style.display = "none";
				hiddenWrappers++;
			}
			
		}
		else {
			
			var groups = wrappers[i].getAttribute("data-teachers").split(" ");
			if (groups.indexOf(select.value) != -1) wrappers[i].style.display = "";
			else {
				wrappers[i].style.display = "none";
				hiddenWrappers++;
			}
			
		}
	}
	
	setCookie("lastsubstitutionfilterindex", select.selectedIndex, 31536000000);
	
	var noSubstitutionDialogs = document.getElementsByClassName("nosubstitution");
	
	if (hiddenWrappers != wrappers.length || wrappers.length == 0) {
		for (var i = 0; i < noSubstitutionDialogs.length; i++)
			noSubstitutionDialogs[i].style.display = "none";
		
		return;
	}
	
	for (var i = 0; i < noSubstitutionDialogs.length; i++)
		if (noSubstitutionDialogs[i].getAttribute("data-type") == select.selectedOptions[0].getAttribute("data-type"))
			noSubstitutionDialogs[i].style.display = "block";
		else
			noSubstitutionDialogs[i].style.display = "none";
}

window.onload = function() {
	selectSavedFilterIndex();
	handleSubstitutionDaySelectLoad();
}