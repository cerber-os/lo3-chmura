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