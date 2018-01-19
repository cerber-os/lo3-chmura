function showDetails(a) {
	document.getElementById("overlay").style.visibility = "visible";
	document.getElementById("overlaytitle").innerText = "Szczegóły";

	var lessonContainer = a.parentElement.parentElement.parentElement;
	
	for (var i = 1; i < lessonContainer.children.length; i++) {
		var entry = lessonContainer.children[i].children[0];
		entry.className = "compactlesson";
		document.getElementById("overlaycontent").appendChild(entry);
	}
}