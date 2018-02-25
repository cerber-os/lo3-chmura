function showTimetableSelect() {
	document.getElementById("overlay").style.visibility = "visible";
	document.getElementById("overlaytitle").innerText = "Wybierz plan";
	
	document.getElementById("overlaycontent").innerHTML = document.getElementById("timetableselectdialog").innerHTML;
}
function handleTimetableSelectUpdate(select) {
	if (select.selectedIndex == select.children.length - 1) {
		showTimetableSelect();
		select.selectedIndex = select.getAttribute("data-previousselectedindex");
		return;
	}
	
	select.setAttribute("data-previousselectedindex", select.selectedIndex);
	
	var typeDictionary = {"trieda": "class", "student": "student", "ucitel": "teacher"};
	var uidDictionary = {"trieda": "lastclassuid", "student": "laststudentuid", "ucitel": "lastteacheruid"};
	var nameDictionary = {"trieda": "lastclass", "student": "laststudent", "ucitel": "lastteacher"};
	
	setCookie("lasttype", typeDictionary[select.selectedOptions[0].getAttribute("data-type")], 31536000000);
	setCookie(uidDictionary[select.selectedOptions[0].getAttribute("data-type")], select.selectedOptions[0].getAttribute("data-uid"), 31536000000);
	setCookie(nameDictionary[select.selectedOptions[0].getAttribute("data-type")], select.selectedOptions[0].innerText, 31536000000);
	
	window.location = "/?sel=" + typeDictionary[select.selectedOptions[0].getAttribute("data-type")] + "&uid=" + encodeURIComponent(select.selectedOptions[0].getAttribute("data-uid"));
}
function handleTimetableTypeSelectUpdate(select) {
	for (var i = 2; i < select.parentElement.children.length - 1; i++) {
		select.parentElement.children[i].style.display = "none";
		select.parentElement.children[i].removeAttribute("name");
	}
	
	if (select.selectedIndex == 0) {
		select.parentElement.children[2].style.display = "";
		select.parentElement.children[2].setAttribute("name", "uid");
	}
	else if (select.selectedIndex == 1) {
		select.parentElement.children[3].style.display = "";
		select.parentElement.children[4].style.display = "";
		select.parentElement.children[4].selectedIndex = 0;
		showStudentList(select.parentElement.children[4]);
	}
	else {
		select.parentElement.children[5].style.display = "";
		select.parentElement.children[5].setAttribute("name", "uid");
	}
}
function showStudentList(classSelect) {
	var classname = classSelect.selectedOptions[0].innerText;
	
	for (var i = 0; i < classSelect.parentElement.children.length - 1; i++)
		if (classSelect.parentElement.children[i].hasAttribute("data-class"))
			if (classSelect.parentElement.children[i].getAttribute("data-class") == classname) {
				classSelect.parentElement.children[i].style.display = "";
				classSelect.parentElement.children[i].setAttribute("name", "uid");

			}
			else {
				classSelect.parentElement.children[i].style.display = "none";
				classSelect.parentElement.children[i].removeAttribute("name");
			}
}

function setLastSettings(submit) {
	var formElements = submit.parentElement.parentElement.children;
	
	for (var i = 0; i < formElements.length; i++)
		if (formElements[i].getAttribute("name") == "uid") {
			
			if (formElements[i].hasAttribute("data-class")) {
				setCookie("lasttype", "student", 31536000000);
				setCookie("laststudent", formElements[i].selectedOptions[0].innerText, 31536000000);
				setCookie("laststudentuid", formElements[i].selectedOptions[0].value, 31536000000);
			}
			else if (formElements[i].getAttribute("data-selecttype") == "class") {
				setCookie("lasttype", "class", 31536000000);
				setCookie("lastclass", formElements[i].selectedOptions[0].innerText, 31536000000);
				setCookie("lastclassuid", formElements[i].selectedOptions[0].value, 31536000000);
			}
			else {
				setCookie("lasttype", "teacher", 31536000000);
				setCookie("lastteacher", formElements[i].selectedOptions[0].innerText, 31536000000);
				setCookie("lastteacheruid", formElements[i].selectedOptions[0].value, 31536000000);
			}

			return;
		}
}
function displayLastSettings() {
	var selects = document.getElementsByClassName("timetableselect");
	
	for (var i = 0; i < selects.length; i++) {
		var select = selects[i];
		
		var defaultOption = select.children[0];
		var defaultType = select.children[0].getAttribute("data-type");
		var defaultValue = select.children[0].innerText;
		
		var chooseOption = select.children[select.children.length - 1];
		select.removeChild(chooseOption);
		
		var defaultIsCurrentClass = defaultType == "Klasa" && defaultValue == getCookie("lastclass");
		var defaultIsCurrentStudent = defaultType == "Uczeń" && defaultValue == getCookie("laststudent");
		var defaultIsCurrentTeacher = defaultType == "Nauczyciel" && defaultValue == getCookie("lastteacher");
		
		var typeDictionary = {
			"Klasa": "trieda",
			"Uczeń": "student",
			"Nauczyciel": "ucitel"
		};
		defaultOption.setAttribute("data-type", typeDictionary[defaultOption.getAttribute("data-type")]);
		
		if (!defaultIsCurrentClass && getCookie("lastclass")) {
			var option = document.createElement("option");
			option.setAttribute("data-type", "trieda");
			option.setAttribute("data-uid", getCookie("lastclassuid"));
			option.innerText = getCookie("lastclass");
			select.appendChild(option);
		}
		
		if (!defaultIsCurrentStudent && getCookie("laststudent")) {
			var option = document.createElement("option");
			option.setAttribute("data-type", "student");
			option.setAttribute("data-uid", getCookie("laststudentuid"));
			option.innerText = getCookie("laststudent");
			select.appendChild(option);
		}
		else if (defaultIsCurrentStudent)
			select.appendChild(select.removeChild(defaultOption));
		
		if (!defaultIsCurrentTeacher && getCookie("lastteacher")) {
			var option = document.createElement("option");
			option.setAttribute("data-type", "ucitel");
			option.setAttribute("data-uid", getCookie("lastteacheruid"));
			option.innerText = getCookie("lastteacher");
			select.appendChild(option);
		}
		else if (defaultIsCurrentTeacher)
			select.appendChild(select.removeChild(defaultOption));
		
		select.appendChild(chooseOption);
		select.setAttribute("data-previousselectedindex", select.selectedIndex);
	}
}

function showDetails(a) {
	document.getElementById("overlay").style.visibility = "visible";
	document.getElementById("overlaytitle").innerText = "Szczegóły";
	document.getElementById("overlaycontent").innerHTML = "";
	
	var lessonContainer = a.parentElement.parentElement.parentElement;
	
	for (var i = 1; i < lessonContainer.children.length; i++) {
		var entry = lessonContainer.children[i].children[0].cloneNode(true);
		entry.className = "compactlesson";
		document.getElementById("overlaycontent").appendChild(entry);
	}
}

window.onload = function() {
	displayLastSettings();
}