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
	var showSecondSelect = select.selectedIndex == 1;
	
	select.parentElement.children[2].style.display = showSecondSelect ? "" : "none";
	select.parentElement.children[3].style.display = showSecondSelect ? "" : "none";
	select.parentElement.children[3].selectedIndex = 0;
	showStudentsList(select.parentElement.children[3]);
}
function showStudentsList(classSelect) {
	
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