﻿/*
*	TIMETABLE SELECTION-RELATED FUNCTIONS
*/
function showTimetableSelect() { //show the timetable select dialog
	//copy timetable select HTML to overlay and display it
	document.getElementById("overlay").style.visibility = "visible";
	document.getElementById("overlaytitle").innerText = "Wybierz plan";
	document.getElementById("overlaycontent").innerHTML = document.getElementById("timetableselectdialog").innerHTML;
	
	//show last mobile form
	var lastMobileForm = getCookie("lastmobileform");
	if (lastMobileForm) toggleMobileForm(Number(lastMobileForm));
	
	//select current timetable
	setCurrentTimetableInSelectDialog();
	
	//focus on the search bar
	document.getElementsByClassName("searchbar")[0].select();
	
	//zoom out for mobile users
	zoomOut();
}
function setCurrentTimetableInSelectDialog() { //update contents of the timetable select dialog
	//fetch current timetable data from quickselect
	var quickselect = document.getElementsByClassName("timetableselect")[0];
	var previousQuickselectIndex = Number(quickselect.getAttribute("data-previousselectedindex")); //fetch index from before "Choose" was selected
	
	var currentType = quickselect.options[previousQuickselectIndex].getAttribute("data-type");
	var currentUid = quickselect.options[previousQuickselectIndex].getAttribute("data-uid");
	
	//get all selects and make place for student class select
	var selects = document.getElementsByClassName("timetabledialogselects")[0].children;
	var studentClassSelect;
	
	//take appropriate action for each of them
	for (var i = 0; i < selects.length; i++)
		if (selects[i].getAttribute("name") == "sel") {
			//select the chosen timetable type
			
			for (var j = 0; j < selects[i].options.length; j++)
				if (selects[i].options[j].value == currentType) {
					selects[i].selectedIndex = j;
					handleTimetableTypeSelectUpdate(selects[i]);
					break;
				}
		}
		else if (selects[i].getAttribute("data-selecttype") == currentType) {
			//select the chosen option
			for (var j = 0; j < selects[i].options.length; j++)
				if (selects[i].options[j].value == currentUid) {					
					//if the current type is a student, select the appropriate class beforehand
					if (currentType == "student") {
						//get student's class from the parent select
						var studentClass = selects[i].getAttribute("data-class");
						
						//select the class in remembered select
						for (var k = 0; k < studentClassSelect.options.length; k++)
							if (studentClassSelect.options[k].value == studentClass) {
								studentClassSelect.selectedIndex = k;
								break;
							}
							
						//update the student selects
						showStudentList(studentClassSelect);
					}
					
					//select the option itself
					selects[i].selectedIndex = j;
					
					return;
				}
		}
		else if (selects[i].getAttribute("data-selecttype") == "populatedclass")
			studentClassSelect = selects[i]; //remember student class select for student selection
}
function handleTimetableSelectUpdate(select) { //triggered when a timetable quickselect is changed, modifies the select and acts appropriately
	//if the chosen option was the last one on the list, show timetable dialog and reset selected option
	if (select.selectedIndex == select.children.length - 1) {
		showTimetableSelect();
		select.selectedIndex = select.getAttribute("data-previousselectedindex");
		return;
	}
	
	//if not, remember the selected option for the next time the last option is chosen
	select.setAttribute("data-previousselectedindex", select.selectedIndex);
	
	//remember selected timetables using cookies
	setCookie("lasttype", select.selectedOptions[0].getAttribute("data-type"), 31536000000); //set last selected timetable type
	setCookie("last" + select.selectedOptions[0].getAttribute("data-type") + "uid", select.selectedOptions[0].getAttribute("data-uid"), 31536000000); //set its uid
	setCookie("last" + select.selectedOptions[0].getAttribute("data-type"), select.selectedOptions[0].innerText, 31536000000); //set its display name
	
	//change window location to desired timetable
	window.location = "/?sel=" + select.selectedOptions[0].getAttribute("data-type") + "&uid=" + encodeURIComponent(select.selectedOptions[0].getAttribute("data-uid"));
}
function handleTimetableTypeSelectUpdate(select) { //triggered when the timetable type select in the dialog is changed
	//hide all elements except type select; prevent them from being included in the form
	for (var i = 1; i < select.parentElement.children.length; i++) {
		select.parentElement.children[i].style.display = "none";
		select.parentElement.children[i].removeAttribute("name");
	}
	
	if (select.selectedOptions[0].value == "class") {
		//show the all classes select, include it in the form
		select.parentElement.children[1].style.display = "";
		select.parentElement.children[1].setAttribute("name", "uid");
	}
	else if (select.selectedOptions[0].value == "student") {
		//show the "from class" text and the populated classes select
		select.parentElement.children[2].style.display = "";
		select.parentElement.children[3].style.display = "";
		showStudentList(select.parentElement.children[3]); //show the corresponding student list and include it in the form
	}
	else if (select.selectedOptions[0].value == "teacher") {
		//show the teacher select and include it in the form
		select.parentElement.children[4].style.display = "";
		select.parentElement.children[4].setAttribute("name", "uid");
	}
	else if (select.selectedOptions[0].value == "classroom") {
		//show the classroom select and include it in the form
		select.parentElement.children[5].style.display = "";
		select.parentElement.children[5].setAttribute("name", "uid");
	}
}
function showStudentList(classSelect) { //display the appropriate student list and include it in the form
	//get the selected class name
	var classname = classSelect.selectedOptions[0].innerText;
	
	//iterate over all children of the dialog, find all student selects
	for (var i = 0; i < classSelect.parentElement.children.length - 1; i++)
		if (classSelect.parentElement.children[i].getAttribute("data-selecttype") == "student")
			if (classSelect.parentElement.children[i].getAttribute("data-class") == classname) {
				//if it's the matching class, show it and include it in the form
				classSelect.parentElement.children[i].style.display = "";
				classSelect.parentElement.children[i].setAttribute("name", "uid");
			}
			else {
				//otherwise, hide it and exclude it
				classSelect.parentElement.children[i].style.display = "none";
				classSelect.parentElement.children[i].removeAttribute("name");
			}
}
function setLastSettings(submit) { //triggered on timetable select form submission, remember choice
	//get all form selects
	var formSelects = submit.parentElement.parentElement.children[1].children;
	
	//iterate over them and find the one containing the currently selected uid (of unknown timetable type)
	for (var i = 0; i < formSelects.length; i++)
		if (formSelects[i].getAttribute("name") == "uid") {
			
			
			//get the select's timetable type
			var type = formSelects[i].getAttribute("data-selecttype");
			
			//remember the choice using cookies
			setCookie("lasttype", type, 31536000000);
			setCookie("last" + type, formSelects[i].selectedOptions[0].innerText, 31536000000);
			setCookie("last" + type + "uid", formSelects[i].selectedOptions[0].value, 31536000000);
			return;
		}
}
function displayLastSettings() { //called on document load, fills the timetable quickselect
	//find all timetable selects in the document
	var selects = document.getElementsByClassName("timetableselect");
	
	//for each one of them, do
	for (var i = 0; i < selects.length; i++) {
		var select = selects[i];
		
		//select the pre-filled option
		var defaultOption = select.children[0];
		var defaultType = select.children[0].getAttribute("data-type");
		var defaultUid = select.children[0].getAttribute("data-uid");
		
		//if the currently displayed timetable is a remembered one, remove the pre-filled option
		var rememberedType = getCookie("lasttype");
		var rememberedUid = getCookie("last" + rememberedType + "uid");
		var defaultRemoved = false;
		
		if (defaultType == rememberedType && defaultUid == rememberedUid) {
			select.removeChild(defaultOption);
			defaultRemoved = true;
		}
		
		//save the "choose" option and temporatily remove it
		var chooseOption = select.children[select.children.length - 1];
		select.removeChild(chooseOption);
		
		//list of timetable types to add to select
		var timetableTypes = ["class", "teacher", "student", "classroom"];
		
		//add option for each of the types, as long as it's remembered
		var indexToSelect = 0; //prepare for future selection
		
		for (var j in timetableTypes) {
			if (!getCookie("last" + timetableTypes[j])) continue;
			
			var option = document.createElement("option");
			option.setAttribute("data-type", timetableTypes[j]);
			option.setAttribute("data-uid", getCookie("last" + timetableTypes[j] + "uid"));
			option.innerText = getCookie("last" + timetableTypes[j]);
			
			option = select.appendChild(option);
			
			if (timetableTypes[j] == rememberedType && getCookie("last" + timetableTypes[j] + "uid") == rememberedUid && defaultRemoved)
				indexToSelect = option.index;
		}
		
		//re-add the "choose" option and remember the currently selected index
		select.appendChild(chooseOption);
		select.selectedIndex = indexToSelect;
		select.setAttribute("data-previousselectedindex", select.selectedIndex);
	}
}
function zoomOut() { //zooms the page out on mobile devices
	//change the meta name="viewport" and set the initial scale to 1
	var viewport = document.getElementById("viewport");
	viewport.content = "width=device-width, initial-scale=1";
	setTimeout(function() { viewport.content = "width=device-width"; }, 100) //after the DOM is updated, remove the initial-scale value to allow immediate change on next attempt
}

function toggleMobileForm(override) { //changes selection type on mobile devices and remembers the choice
	//get mobile forms holder
	var formHolder = document.getElementById("overlaycontent").children[0];
	
	if (override != undefined) {
		for (var i = 0; i < formHolder.children.length; i++)
			if (i == override) formHolder.children[i].setAttribute("data-selectedmobileform", "data-selectedmobileform");
			else formHolder.children[i].removeAttribute("data-selectedmobileform");
			
		return;
	}
	
	//iterate over forms, move the data-selectedmobileform attribute
	for (var i = 0; i < formHolder.children.length; i++)
		if (formHolder.children[i].hasAttribute("data-selectedmobileform")) {
			var newForm;
			
			//if at the end, move attribute to the beginning
			if (i == formHolder.children.length - 1) newForm = 0;
			else newForm = i + 1;
			
			//display the right form and remember the choice
			formHolder.children[newForm].setAttribute("data-selectedmobileform", "data-selectedmobileform");
			setCookie("lastmobileform", newForm, 31536000000);
			
			//remove attribute from current form
			formHolder.children[i].removeAttribute("data-selectedmobileform");
			return;
		}
}

/*
*	TIMETABLE-RELATED FUNCTIONS
*/
function showDetails(div) { //show the lesson details dialog, triggered when the "expand" link is clicked
	//show the overlay and clear its contents
	document.getElementById("overlay").style.visibility = "visible";
	document.getElementById("overlaytitle").innerText = "Szczegóły";
	document.getElementById("overlaycontent").innerHTML = "";
	
	//create comapct lesson holder
	var holder = document.createElement("div");
	holder.className = "compactlessonholder";
	holder = document.getElementById("overlaycontent").appendChild(holder);
	
	//get the lessonholder
	var lessonContainer = div.parentElement;
	
	//for each of the elements in the lessonholder, clone the element's only child, change its class to compact and append it to the overlay
	for (var i = 1; i < lessonContainer.children.length; i++) {
		var entry = lessonContainer.children[i].children[0].cloneNode(true);
		entry.className = "compactlesson";
		holder.appendChild(entry);
	}
	
	//zoom out on mobile devices
	zoomOut();
}

/*
*	SEARCH FUNCTIONALITY
*/
var searchIndex = [];

function addSearchIndexEntry(name, type, uid) { //add entry to the search index
	var entry = {};
	
	entry.name = name;
	entry.type = type;
	entry.uid = uid;
	
	searchIndex.push(entry);
}
function buildSearchIndex() { //fill index with entries
	//get all selects in the document
	var selects = document.getElementsByTagName("select");
	
	//iterate over all the selects
	for (var i = 0; i < selects.length; i++) {
		var selectType = selects[i].getAttribute("data-selecttype");
		
		//determine entries type, no data-selecttype = irrelevant select
		var type;
		if (selectType == "class" || selectType == "student" || selectType == "teacher" || selectType == "classroom") type = selectType;
		else continue;
		
		//add entries to search index
		for (var j = 0; j < selects[i].options.length; j++)
			addSearchIndexEntry(selects[i].options[j].innerText, type, selects[i].options[j].value);
	}
}
function searchForTimetable(query) { //find matching entries in the search index
	var results = [];
	
	//sanitize input
	if (!query) return results;
	query = query.toLowerCase();
	
	//iterate over search index entries
	for (var i in searchIndex) {
		//calculate score based on query position in name
		var score = searchIndex[i].name.toLowerCase().indexOf(query);
		
		//discard non-matching entries
		if (score == -1) continue;
		
		//create results entry
		var resultsEntry = {};
		resultsEntry.text = searchIndex[i].name;
		resultsEntry.html = searchIndex[i].name.substring(0, score)
			+ "<b>"
			+ searchIndex[i].name.substr(score, query.length)
			+ "</b>"
			+ searchIndex[i].name.substr(score + query.length);
		resultsEntry.type = searchIndex[i].type;
		resultsEntry.uid = searchIndex[i].uid;
		resultsEntry.score = score;
		results.push(resultsEntry);
	}
	
	//sort by score and by length
	results.sort(function(a, b) { return (a.score != b.score) ? (a.score - b.score) : (a.text.length - b.text.length); });
	
	return results;
}
function handleSearchBarKeyUp(input, event) { //triggered when a key is released in the search bar, used for text input
	//get suggestion holder
	var suggestionHolder = input.parentElement.children[3].children[0];
	
	//exclude control keys from being handled
	if (event.keyCode == 13) { return; }
	if (event.keyCode == 38) { return; }
	if (event.keyCode == 40) { return; }
	
	//get search results and clear previous results
	var results = searchForTimetable(input.value);
	suggestionHolder.innerHTML = "";
	
	//reset selected suggestion
	suggestionHolder.setAttribute("data-selectedindex", "-1");
	
	//build nonresult if there are no results
	if (results.length == 0 && input.value.length != 0) {
		var nonresult = document.createElement("a");
		nonresult.className = "result nonresult";
		nonresult.innerText = "Brak wyników.";
		
		suggestionHolder.appendChild(nonresult);
		return;
	}
	
	//result type dictionary
	var typeDictionary = {
		"class": "klasa",
		"teacher": "nauczyciel",
		"student": "uczeń",
		"classroom": "sala"
	};
	
	//build results
	for (var i = 0; i < 5 && i < results.length; i++) {
		var result = document.createElement("a");
		result.className = "result";
		result.innerHTML = results[i].html;
		result.innerHTML += "<span>" + typeDictionary[results[i].type] + "</span>";
		result.setAttribute("href", "/?sel=" + results[i].type + "&uid=" + encodeURIComponent(results[i].uid));
		result.setAttribute("data-type", results[i].type);
		result.setAttribute("data-uid", results[i].uid);
		result.setAttribute("data-displayname", results[i].text);
		result.setAttribute("onclick", "setLastSettingsFromSearch(this)");
		
		suggestionHolder.appendChild(result);
		
		//show 10th result only if there are 5 results
		if (i == 3 && results.length > 5) break;
	}
	
	//show skipped results nonresult
	if (results.length > 5) {
		var result = document.createElement("a");
		result.className = "result nonresult";
		result.innerText = "Nie pokazano " + (results.length - 4) + " wyników."
		
		suggestionHolder.appendChild(result);
	}
}
function handleSearchBarKeyDown(input, event) { //triggered when a key is pressed in the search bar, used for control keys
	//get suggestion holder
	var suggestionHolder = input.parentElement.children[3].children[0];
	
	//handle control keys
	if (event.keyCode == 13) { acceptSearchSuggestion(suggestionHolder, event); return; }
	if (event.keyCode == 40) { moveSearchSelection(suggestionHolder, true, event); return; }
	if (event.keyCode == 38) { moveSearchSelection(suggestionHolder, false, event); return; }
}
function moveSearchSelection(suggestionHolder, down, event) { //update data-selectedindex on suggestion holder
	//prevent cursor movement
	event.preventDefault();
	
	//prevent selection of empty list
	if (suggestionHolder.children.length == 0) return;
	
	//calculate desired selectedindex
	var desiredSelectedIndex = Number(suggestionHolder.getAttribute("data-selectedIndex")) + (down ? 1 : -1);
	
	//prevent selectedindex exceeding -1 when decreasing
	if (desiredSelectedIndex == -2) return;
	
	//calculate max selectedindex and prevent exceeding it
	var maxSelectedIndex = suggestionHolder.children.length - 1;
	if (!suggestionHolder.children[suggestionHolder.children.length - 1].hasAttribute("data-type")) maxSelectedIndex--; //prevent selecting nonresult
	if (desiredSelectedIndex == maxSelectedIndex + 1) return;
	
	//set selectedindex and update html
	suggestionHolder.setAttribute("data-selectedIndex", desiredSelectedIndex);
	updateSearchSelection(suggestionHolder);
}
function updateSearchSelection(suggestionHolder) { //select appropriate suggestion based on data-selectedindex
	//get selected index
	var selectedIndex = Number(suggestionHolder.getAttribute("data-selectedIndex"));
	
	//de-select all suggestions
	for (var i = 0; i < suggestionHolder.children.length; i++)
		suggestionHolder.children[i].removeAttribute("data-selected");
	
	//nothing to select
	if (selectedIndex == -1) return;
	
	//select selected index
	suggestionHolder.children[selectedIndex].setAttribute("data-selected", "data-selected");
}
function acceptSearchSuggestion(suggestionHolder, event) { //follow link in marked selection
	//prevent form submission
	event.preventDefault();
	
	//exclude empty suggestion holders
	if (suggestionHolder.children.length == 0) return;
	if (suggestionHolder.children.length == 1 && !suggestionHolder.children[0].hasAttribute("data-type")) return;
	
	//get selected index, if nothing is selected, select first entry
	var selectedIndex = Number(suggestionHolder.getAttribute("data-selectedIndex"));
	if (selectedIndex == -1) selectedIndex = 0;
	
	//click suggestion
	var suggestion = suggestionHolder.children[selectedIndex];
	setLastSettingsFromSearch(suggestion);
	window.location = suggestion.getAttribute("href");
}
function setLastSettingsFromSearch(a) { //remember chosen timetable, triggered on result selection
	var type = a.getAttribute("data-type");
	var displayName = a.getAttribute("data-displayname");
	var uid = a.getAttribute("data-uid");
	
	setCookie("lasttype", type, 31536000000);
	setCookie("last" + type, displayName, 31536000000);
	setCookie("last" + type + "uid", uid, 31536000000);
}

/*
*	EVENTS
*/
function handleOnKeyDown(event) {
	if (event.keyCode == 113) showTimetableSelect(); //show timetable select on F2
}
window.addEventListener("keydown", handleOnKeyDown);
window.onload = function() {
	displayLastSettings(); //update the quickselect to show remembered options
	buildSearchIndex(); //prepare search index for searching
}