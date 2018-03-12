/*
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
	
	//zoom out for mobile users
	zoomOut();
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
	
	//cookie name dictionaries, different names for different data types
	var uidDictionary = {"class": "lastclassuid", "student": "laststudentuid", "teacher": "lastteacheruid"};
	var nameDictionary = {"class": "lastclass", "student": "laststudent", "teacher": "lastteacher"};
	
	//remember selected timetables using cookies
	setCookie("lasttype", select.selectedOptions[0].getAttribute("data-type"), 31536000000); //set last selected timetable type
	setCookie(uidDictionary[select.selectedOptions[0].getAttribute("data-type")], select.selectedOptions[0].getAttribute("data-uid"), 31536000000); //set its uid
	setCookie(nameDictionary[select.selectedOptions[0].getAttribute("data-type")], select.selectedOptions[0].innerText, 31536000000); //set its display name
	
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
}
function showStudentList(classSelect) { //display the appropriate student list and include it in the form
	//get the selected class name
	var classname = classSelect.selectedOptions[0].innerText;
	
	//iterate over all children of the dialog, find all student selects
	for (var i = 0; i < classSelect.parentElement.children.length - 1; i++)
		if (classSelect.parentElement.children[i].getAttribute("data-selecttype") == "student")
			if (classSelect.parentElement.children[i].getAttribute("data-class") == classname) {
				//if it's the matching class, reset it, show it and include it in the form
				classSelect.parentElement.children[i].selectedIndex = 0;
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
	//get all form elements
	var formElements = submit.parentElement.parentElement.children;
	
	//iterate over them and find the one containing the currently selected uid (of unknown timetable type)
	for (var i = 0; i < formElements.length; i++)
		if (formElements[i].getAttribute("name") == "uid") {
			
			if (formElements[i].getAttribute("data-selecttype") == "student") {
				//current timetable type is student
				setCookie("lasttype", "student", 31536000000);
				setCookie("laststudent", formElements[i].selectedOptions[0].innerText, 31536000000);
				setCookie("laststudentuid", formElements[i].selectedOptions[0].value, 31536000000);
			}
			else if (formElements[i].getAttribute("data-selecttype") == "class") {
				//current timetable type is class
				setCookie("lasttype", "class", 31536000000);
				setCookie("lastclass", formElements[i].selectedOptions[0].innerText, 31536000000);
				setCookie("lastclassuid", formElements[i].selectedOptions[0].value, 31536000000);
			}
			else if (formElements[i].getAttribute("data-selecttype") == "teacher") {
				//current timetable type is teacher
				setCookie("lasttype", "teacher", 31536000000);
				setCookie("lastteacher", formElements[i].selectedOptions[0].innerText, 31536000000);
				setCookie("lastteacheruid", formElements[i].selectedOptions[0].value, 31536000000);
			}

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
		var defaultValue = select.children[0].innerText;
		
		//save the "choose option" and temporatily remove it
		var chooseOption = select.children[select.children.length - 1];
		select.removeChild(chooseOption);
		
		//determine whether the pre-filled option matches one of the saved options
		var defaultIsCurrentClass = defaultType == "Klasa" && defaultValue == getCookie("lastclass");
		var defaultIsCurrentStudent = defaultType == "Uczeń" && defaultValue == getCookie("laststudent");
		var defaultIsCurrentTeacher = defaultType == "Nauczyciel" && defaultValue == getCookie("lastteacher");
		
		//convert the pre-filled option type value from display name to type id
		var typeDictionary = {
			"Klasa": "class",
			"Uczeń": "student",
			"Nauczyciel": "teacher"
		};
		defaultOption.setAttribute("data-type", typeDictionary[defaultOption.getAttribute("data-type")]);
		
		if (!defaultIsCurrentClass && getCookie("lastclass")) {
			//if there is a remembered class and the pre-filled option wasn't a class, add an option to show the remembered class
			var option = document.createElement("option");
			option.setAttribute("data-type", "class");
			option.setAttribute("data-uid", getCookie("lastclassuid"));
			option.innerText = getCookie("lastclass");
			select.appendChild(option);
		}
		
		if (!defaultIsCurrentStudent && getCookie("laststudent")) {
			//if there is a remembered student and the pre-filled option wasn't a student, add an option to show the remembered student
			var option = document.createElement("option");
			option.setAttribute("data-type", "student");
			option.setAttribute("data-uid", getCookie("laststudentuid"));
			option.innerText = getCookie("laststudent");
			select.appendChild(option);
		}
		else if (defaultIsCurrentStudent)
			select.appendChild(select.removeChild(defaultOption)); //otherwise, if the pre-filled option was a student, move it to the bottom
		
		if (!defaultIsCurrentTeacher && getCookie("lastteacher")) {
			//if there is a remembered teacher and the pre-filled option wasn't a teacher, add an option to show the remembered teacher
			var option = document.createElement("option");
			option.setAttribute("data-type", "teacher");
			option.setAttribute("data-uid", getCookie("lastteacheruid"));
			option.innerText = getCookie("lastteacher");
			select.appendChild(option);
		}
		else if (defaultIsCurrentTeacher)
			select.appendChild(select.removeChild(defaultOption)); //otherwise, if the pre-filled option was a teacher, move it to the bottom
		
		//re-add the "choose" option and remember the currently selected index
		select.appendChild(chooseOption);
		select.setAttribute("data-previousselectedindex", select.selectedIndex);
	}
}
function zoomOut() { //zooms the page out on mobile devices
	//change the meta name="viewport" and set the initial scale to 1
	var viewport = document.getElementById("viewport");
	viewport.content = "width=device-width, initial-scale=1";
	setTimeout(function() { viewport.content = "width=device-width"; }, 1) //after the DOM is updated, remove the initial-scale value to allow immediate change on next attempt
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
function showDetails(a) { //show the lesson details dialog, triggered when the "expand" link is clicked
	//show the overlay and clear its contents
	document.getElementById("overlay").style.visibility = "visible";
	document.getElementById("overlaytitle").innerText = "Szczegóły";
	document.getElementById("overlaycontent").innerHTML = "";
	
	//create comapct lesson holder
	var holder = document.createElement("div");
	holder.className = "compactlessonholder";
	holder = document.getElementById("overlaycontent").appendChild(holder);
	
	//get the lessonholder
	var lessonContainer = a.parentElement.parentElement.parentElement.parentElement;
	
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
		if (selectType == "class" || selectType == "student" || selectType == "teacher") type = selectType;
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
	
	//sort by score
	results.sort(function(a, b) { return a.score - b.score; });
	
	return results;
}
function handleSearchBarKeyUp(input, event) { //triggered when a key is released in the search bar, used for text input
	//get suggestion holder
	var suggestionHolder = input.parentElement.children[2].children[0];
	
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
		"student": "uczeń"
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
	var suggestionHolder = input.parentElement.children[2].children[0];
	
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
*	ONLOAD CODE
*/
window.onload = function() {
	displayLastSettings(); //update the quickselect to show remembered options
	buildSearchIndex(); //prepare search index for searching
}