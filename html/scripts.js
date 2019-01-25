//loads the json file
$(window).on('load',function(){
	$("#inputfile").val("")
	sprojects = $.getJSON('projects.json')
	document.getElementById('inputfile').addEventListener('change', handleFileSelect, false);
})

function load(){ //for when there has not been a json file chosen, uses default projects.json
	projects = sprojects.responseJSON
	clears();
	fillPro();
	fillSG();
	blankR();
	$("#loadbut").show()
	$("#basejson").hide()
}

function handleFileSelect(evt) {
    /*
    Handle file selected by browser dialog.
     */	
	reader = new FileReader()
	files = evt.target.files; // FileList object
	f = files[0];
	
	// Only process image files.
	if (!f.type.match('application/json')) {
        alert('Sorry, this script will only process JSON files.  ' +
            'You attempted to process a file of type: ' + f.type);
		return;
	}
	
	
	reader.readAsText(f);
	reader.onload = fileReadComplete;  // need some event handler here
}

function fileReadComplete(e) {
	projects = JSON.parse(reader.result)	
	$("#loadbut").show()
	$("#basejson").hide()
	clears();
	fillPro();
	fillSG();
	blankR();
}

function fillPro() {  //fills in the list of projects
	$('#txtPro')[0].innerHTML = ''
	var proSelect = $("#txtPro")[0]; 
	var por = projects.projects; 
	for (por in projects.projects){ 
		var option = document.createElement("option"); 
		option.text = por; 
		proSelect.add(option); 
	} 
}


function highlightSG(){ //highlights related seed groups when project is chosen
	var seedR = []
	for (i=0; i< projects.projects[$("#txtPro").val()]["regions"].length; i++){
		for (j=0; j< projects.projects[$("#txtPro").val()]["regions"][i]["seed_region_names"].length; j++)
			if (seedR.includes(projects.projects[$("#txtPro").val()]["regions"][i]["seed_region_names"][j])==false){
				seedR.push(projects.projects[$("#txtPro").val()]["regions"][i]["seed_region_names"][j])
			}
	}
	var seedG = []
	for (i=0; i< seedR.length; i++){
		if (seedG.includes(projects.regions[seedR[i]]["seed_group"])==false){
			seedG.push(projects.regions[seedR[i]]["seed_group"])
		}


	}
	$("#txtSG").val(seedG)
}



function fillSG() { //fills list of seed groups
	$('#txtSG')[0].innerHTML = ''
	var grSelect = $('#txtSG')[0];
	var sCheck = []; //array to check if seed group is already added

	var regArr = []; //store regions in array
	var reg = projects.regions
	for (reg in projects.regions){
		regArr.push(reg)
	}
	for (i=0; i< regArr.length; i++){
		var option = document.createElement("option");	
		option.text = projects.regions[regArr[i]]["seed_group"];
		if (sCheck.includes(projects.regions[regArr[i]]["seed_group"]) == false && projects.regions[regArr[i]]["seed_group"] !== null && projects.regions[regArr[i]]["seed_group"] !== "null"){	
			sCheck.push (projects.regions[regArr[i]]["seed_group"]);
			grSelect.add(option);
		} 
	}
}


function blankR(){ //clears both region select fields
	$("#txtCR")[0].innerHTML =""
	$("#txtSR")[0].innerHTML =""
}

function fillSR(){ //fills seed regions
	$('#txtSR')[0].innerHTML = ''
	var check = [];
	var seregSelect = $("#txtSR")[0];
	if ($("#txtPro").val().length ==1){
		var region = projects.projects[$('#txtPro').val()].regions
		for (i=0; i< region.length; i++){
			var pro = $('#txtPro').val();
			var seedR = region[i]["seed_region_names"]
			for (j=0; j<seedR.length; j++){	
				var option = document.createElement("option");	
				option.text = seedR[j];
				if (check.includes(seedR[j]) == false){	
					check.push (seedR[j]);
					seregSelect.add(option);
				}
			}
		}
	}else if ($("#txtPro").val().length >1){
		for (k=0; k<$("#txtPro").val().length ; k++){
		var region = projects.projects[$('#txtPro').val()[k]].regions
			for (i=0; i< region.length; i++){
				var pro = $('#txtPro').val();
				var seedR = region[i]["seed_region_names"]
				for (j=0; j<seedR.length; j++){	
					var option = document.createElement("option");	
					option.text = seedR[j];
					if (check.includes(seedR[j]) == false){	
						check.push (seedR[j]);
						seregSelect.add(option);
					}
				}
			}

		}
	}
}

function fillCR(){ //fills in list of coordinate regions of a project
	$('#txtCR')[0].innerHTML = ''
	var coregSelect = $("#txtCR")[0];
	var check = [];
	if ($("#txtPro").val().length ==1){
		var region = projects.projects[$('#txtPro').val()].regions
		for (i=0; i<region.length; i++){
			var pro = $('#txtPro').val();
			var option = document.createElement("option");
			option.text = region[i]["coordinate_region"]
			coregSelect.add(option);
		}
	}else if ($("#txtPro").val().length >1){
		for (k=0; k<$("#txtPro").val().length ; k++){
		var region = projects.projects[$('#txtPro').val()[k]].regions
			for (i=0; i<region.length; i++){
				var pro = $('#txtPro').val();
				var option = document.createElement("option");
				option.text = region[i]["coordinate_region"]
				if (check.includes(region[i]["coordinate_region"]) == false){	
						check.push (region[i]["coordinate_region"]);
						coregSelect.add(option);
				}
			}
		}
	}
}


function coselReg(){ //highlights related seed region fields when coordinate region is selected
	if ($("#txtCR option").length ==0){
		alert ("No coordinate region selectable.")
	}else if ($("#txtPro").val().length ==1){
		var region = projects.projects[$('#txtPro').val()].regions;
		var coordArr = [];
		for (i = 0; i < region.length; i++){
			coordArr.push (region[i]["coordinate_region"]);
		}
		var arrNum = coordArr.indexOf($("#txtCR").val()[0])
		var seedRG = region[arrNum]["seed_region_names"]
		$("#txtSR").val(seedRG)
		if (region[arrNum]["seed_region_names"].length !== 0){
			$("#txtSG").val(projects.regions[seedRG[0]]["seed_group"])
		}else{
			$("#txtSG").val("")
		}
	}else if ($("#txtPro").val().length >1){
		var check = []
		for (j=0; j<$("#txtPro").val().length ; j++){
			var region = projects.projects[$('#txtPro').val()[j]].regions;
			var coordArr = [];
			for (i = 0; i < region.length; i++){
				coordArr.push (region[i]["coordinate_region"]);
			}
			var arrNum = coordArr.indexOf($("#txtCR").val()[0])
			if (arrNum !== -1){
				for (k=0; k<region[arrNum]["seed_region_names"].length; k++){
					if (check.includes(region[arrNum]["seed_region_names"][k].toString()) == false){
						check.push(region[arrNum]["seed_region_names"][k].toString())
					}	
				}		
			}	
		}
		$("#txtSR").val(check)
		$("#txtSG").val(projects.regions[check[0]]["seed_group"])
	}
}

function regselCo(){ //highlights related coordinate region fields when seed region is selected
	if($("#txtSR").val().length == 1){
		if ($("#txtPro").val().length ==1){
			var region = projects.projects[$('#txtPro').val()].regions;
			var check = []
			for (i = 0; i < region.length; i++){
				if (region[i]["seed_region_names"].includes($("#txtSR").val()[0])){
					check.push (region[i]["coordinate_region"])
				}
			
			}
			$("#txtSG").val(projects.regions[$("#txtSR").val()]["seed_group"])		
		}else if ($("#txtPro").val().length >1){
			var check = []
			for (j=0; j<$("#txtPro").val().length ; j++){
				var region = projects.projects[$("#txtPro").val()[j]].regions;
				
				for (i = 0; i < region.length; i++){
					if (region[i]["seed_region_names"].includes($("#txtSR").val()[0])){
						check.push (region[i]["coordinate_region"])
					}
				}
			}
			$("#txtSG").val(projects.regions[$("#txtSR").val()[0]]["seed_group"])
		}

		$("#txtCR").val(check)
	}else if ($("#txtSR option").length ==0){
		alert ("No seed region selectable.")
	}
}

function sgSel(){ //select seed group, finds and highlights projects and regions related
	var sCheck = []; 
	var regArr = [];
	var regions = projects.regions

	for (regions in projects.regions){
		regArr.push(regions)
	}
	for (i=0; i< regArr.length; i++){ //finds the associated seed regions
		if (projects.regions[regArr[i]]["seed_group"] == $("#txtSG").val()){ 
			sCheck.push ([regArr[i]]);
		} 
	}
	var por = projects.projects; 
	var proj = []	
	var seedP = []	
	var seedC = []
	for (por in projects.projects){ 
		proj.push(por)
	} 

	for (i=0; i< proj.length; i++){
		for (j=0; j< projects.projects[proj[i]]["regions"].length; j++){
			for (k=0; k< projects.projects[proj[i]]["regions"][j]["seed_region_names"].length; k++){
				for (m=0; m<sCheck.length; m++){
					if (projects.projects[proj[i]]["regions"][j]["seed_region_names"][k].includes(sCheck[m])){
						seedP.push(proj[i])
						seedC.push(projects.projects[proj[i]]["regions"][j]["coordinate_region"])
						
					}
				}
			}
		}
	}

	$("#txtPro").val(seedP)
	fillSR()
	fillCR()
	$("#txtSR").val(sCheck)
	$("#txtCR").val(seedC)
		
}

function deta(x){ // fills in the details of project/region
	clears()
	var proj 
	proj = projects.projects[$('#txtPro').val()]
		
	if ($("#txtSR").val() == null || $("#txtCR").val() == null || $('#txtPro').val()== null){
		alert("No selection made.")
	}else {

		if (x == "CR"){
			if ($("#txtCR").val().length==1){
				var reg =  projects.regions[$('#txtCR').val() ]
				$("#txtSeq").val(reg["reference"].toString().replace(/\,/g, ''))
				$('#txtReg')[0].innerHTML = ("Coordinate")
				$('#txtRN').val($("#txtCR").val())
				regType = "Coordinate" //global variable to check region type
			} else if ($("#txtCR").val().length>1){
				alert("More than one coordinate selected.")
			}
		}else if (x == "SR"){
			if ($("#txtSR").val().length==1){
				var reg =  projects.regions[$('#txtSR').val()]
				$("#txtSeq").val(reg["reference"].toString().replace(/\,/g, ''))
				$('#txtReg')[0].innerHTML = ("Seed")
				$('#txtRN').val($("#txtSR").val())
				regType = "Seed" //global variable to check region type
			} else if ($("#txtSR").val().length>1){
				alert("More than one seed selected.")
			}
		}
		if ($("#txtSR option").length !== 0 || $("#txtCR option").length !==0){
			globReg = reg //global variable to store region chosen
			$('#txtNuc')[0].innerHTML = reg["is_nucleotide"].toString()
			if (reg["is_nucleotide"] == false){
				$("#txtSeG").val("null")
			}else{
				$("#txtSeG").val(reg["seed_group"])
			}
		}
		
		
	}
	if($("#txtPro").val().length == 1){
		$("#txtName").val($('#txtPro').val()) ;
		$('#txtDes').val(proj["description"]) 
		$('#txtVar').val(proj["max_variants"]) 

	} else{
		$('#txtName').val( "Project not selected.")
		$('#txtDes').val("N/A")
		$('#txtVar').val("N/A")

	}
}

function clears(){ //clears the details fields
	$("#txtName").val("")
	$('#txtDes').val("")
	$('#txtVar').val("")
	$("#txtSeG").val("")
	$('#txtNuc')[0].innerHTML = ""
	$("#txtSeq").val("")
	$('#txtReg')[0].innerHTML = ("")
	$('#txtRN').val("")
}


function editCheck(){ //check to see which fields are edited and if changes are permitted
	var proj = projects.projects[$('#txtPro').val()]
	var reg =  projects.regions
	var changes =""
	var matchOK 
	var isNuc = 0
	var isAA = 0
	var regNameOK = true
	

	if ($("#txtPro").val().length > 1 || $("#txtPro").val().length == 0){ //check for name change
		alert ("Project needs to be selected.")
		matchOK = false
	}else if($("#txtSR").val() == "" || $("#txtSR").val() == ""){
		alert("Region needs to be selected.")
	}else if($("#txtPro").val().toString() == $("#txtName").val()){
		newProj = $("#txtPro").val().toString()
	}else if($("#txtPro").val().toString() !== $("#txtName").val()){
		newProj = $("#txtName").val()
		changes += "\n" + "Project Name"
	}

	
	if ($("#txtVar").val() == proj["max_variants"]){ //check for max variant change
		newVar = proj["max_variants"]
	}else if ($("#txtVar").val() !== proj["max_variants"]){	
		newVar = $("#txtVar").val()
		changes += "\n" + "Max Variants"
	}
	

	if ($("#txtDes").val() == proj["description"]){ //check for description change
		newDes = proj["description"]
	}else if ($("#txtDes").val() !== proj["description"]){
		newDes = $("#txtDes").val()
		changes += "\n" + "Description"
	}

	
	if ($("#txtReg")[0].innerHTML == regType){ //check for region type
		newregType = regType
	}else if ($("#txtReg")[0].innerHTML !== regType){
		newregType = $("#txtReg")[0].innerHTML
		changes += "\n" + "Region Type"
	}


	if (regType == "Coordinate"){ //check for region name
		regName = $("#txtCR").val().toString()
	}else if (regType == "Seed"){
		regName = $("#txtSR").val().toString()
	}
	if (projects.regions[$("#txtRN").val()] == undefined){ 
		if ($("#txtRN").val() !== regName){
			changes += "\n" + "Region Name"
		} 
		regNameOK = true
	 	newregName = $("#txtRN").val()
	}else if(projects.regions[$("#txtRN").val()] !== undefined){
		if($("#txtRN").val() !== regName){
			alert("Region name already exists.")
			regNameOK = false
		}else{
			regNameOK = true	
			newregName = $("#txtRN").val()
		}
	}


	//check for seed group
	if ($("#txtReg")[0].innerHTML == "Coordinate" && $("#txtSeG").val() !== "null"){
		alert("seed group for coordinate regions is 'null'")
		$("#txtSeG").val("null")
		newSG = $("#txtSeG").val()
	}else if ($("#txtReg")[0].innerHTML == "Coordinate" && $("#txtSeG").val() == "null"){
		newSG = "null"
	}else if ($("#txtReg")[0].innerHTML == "Seed" && $("#txtSeG").val() == globReg["seed_group"]){
		newSG = $("#txtSeG").val()
	}else if ($("#txtReg")[0].innerHTML == "Seed" && $("#txtSeG").val() !== globReg["seed_group"]){
		newSG = $("#txtSeG").val()
		changes += "\n" + "Seed Group"
	}


	
	if (globReg["reference"].toString().replace(/\,/g, '') == $("#txtSeq").val().replace(/\,/g, '').replace(/\d/g, "").replace(/ +/g, '').replace(/\n/g, "").toUpperCase()){ //check for sequence
		newSeq = globReg["reference"]
	}else if (globReg["reference"].toString().replace(/\,/g, '') !== $("#txtSeq").val().replace(/\,/g, '').replace(/\d/g, "").replace(/ +/g, '').replace(/\n/g, "").toUpperCase()){ //converts sequence to array
		newSeq = []
		tempSeq =$("#txtSeq").val().replace(/\,/g, '').replace(/\d/g, "").replace(/ +/g, '').replace(/\n/g, "").toUpperCase()
		var arrLength = Math.ceil(tempSeq.length/65) 
		for (i=0; i< arrLength-1; i++){
			var seqBlock = ""
			for (j=0; j<65; j++){
				if (tempSeq[i*65 +j].length!== undefined){
					seqBlock += tempSeq[i*65 +j]
				}
			}
			newSeq[i] = seqBlock
		}	
		var seqBlock = ""
		for (i=(arrLength-1)*65; i<tempSeq.length; i++){
			seqBlock += tempSeq[i].toUpperCase()
		}
		newSeq[arrLength-1] = seqBlock
			
		changes += "\n" + "Reference Sequence"
	}
	
	var aminoCheck = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z",".","-",","," ","*","#"]
	var nucleicCheck = ["A","C","G","T","U","W","S","M","K","R","Y","B","D","H","V","N","Z",".","-",","," ","*","#"]

	for (i=0; i<newSeq.toString().length; i++){ //checks if sequence is nucleotide or amino acid
		if(nucleicCheck.includes(newSeq.toString()[i])==false){
			isNuc += 1
		}
		if(aminoCheck.includes(newSeq.toString()[i])==false){
			isAA += 1
		}
	}
	
	//check if sequence matches region type
	if ($("#txtReg")[0].innerHTML == "Coordinate"){
		if($("#txtNuc")[0].innerHTML == "false" && isAA == 0){
			matchOK = true
		}else{
			alert("For a coordinate region, sequence must be a valid Amino Acid Sequence")
			matchOK = false
		}
	}else if ($("#txtReg")[0].innerHTML == "Seed"){
		if($("#txtNuc")[0].innerHTML == "true" && isNuc == 0){
			matchOK = true
		}else{
			alert("For a seed region, sequence must be a valid Nucleotide Sequence")
			matchOK = false
		}
	}

	if (isNaN($("#txtVar").val())){
		alert("Max Variants must be a number")
		matchOK = false
	}

	if (matchOK == true && ($("#txtSR").val() !== "" || $("#txtSR").val() !== "") && regNameOK == true){
		if (changes == ""){
			if (confirm ("There were no changes")){
			}	
		}else{ 
			if (confirm ("The following will be changed:" + changes)){
				editChange()
			}	
		}
	}
}

function editChange(){ //makes the edits
	var proje = projects.projects
	var regi = projects.regions
	
	if (newProj !== $("#txtPro").val().toString()){
		proje[newProj] = proje[$("#txtPro").val().toString()]
		delete proje[$("#txtPro").val().toString()]
		fillPro()
		$("#txtPro").val(newProj)
	}
	proje[newProj]["max_variants"] = newVar
	proje[newProj]["description"] = newDes
	

	
	var regionIndex = []
	var seedIndex
	var coorIndex = []
	
	if (newregType == "Coordinate"){ //for when coordinate name is changed
		regi[newregName] = {"is_nucleotide": false, "reference": newSeq, "seed_group": newSG}
		for (i=0; i<$("#txtCR option").length;i++){		
			if ($("#txtCR option")[i].innerHTML == $("#txtCR").val()){
				coorIndex.push(i)
			}
		}
		proje[newProj]["regions"][coorIndex[0]]["coordinate_region"] = newregName
		fillCR()
		$("#txtCR").val(newregName)

	}else if (newregType == "Seed"){ //for when seed name is changed 
		regi[newregName] = {"is_nucleotide": true, "reference": newSeq, "seed_group": newSG}
		for (i=0; i<$("#txtCR").val().length; i++){
			for (j=0; j<$("#txtCR option").length;j++){		
				if ($("#txtCR option")[j].innerHTML == $("#txtCR").val()[i]){
					regionIndex.push(j)
				}
			}
			seedIndex = proje[newProj]["regions"][regionIndex[i]]["seed_region_names"].indexOf(regName)
			proje[newProj]["regions"][regionIndex[i]]["seed_region_names"][seedIndex] = newregName
		}	
		fillSR()
		fillSG()
		$("#txtSR").val(newregName)
		$("#txtSG").val(newSG)
	}

}

function delPR(){  //to delete a project or region
	var por = projects.projects;
	var check = []
	if ($("#txtPro").val().length !== 1){
		alert ("Project must be selected.")
	}else{
		if (confirm("Are you sure you want to delete?")) {
			if ($('#delType').val() == "project"){
				delete projects.projects[$('#txtPro').val()]
				alert ("project has been deleted")
				fillPro()
				closeForm('delForm')
			}else if ($('#delType').val() == "region"){ 
				if ($("#txtSR").val().length == 0 && $("#txtCR").val().length == 0){
					alert("Region must be selected.")
				}else{
					var coorIndex = []
					var upPro = projects.projects[$('#txtPro').val()]["regions"]
					if (regType == "Coordinate" && $("#txtCR").val().length == 1){ 
						for (i=0; i<$("#txtCR option").length;i++){		
							if ($("#txtCR option")[i].innerHTML == $("#txtCR").val()){
								coorIndex.push(i)
							}
						}
						delete projects.projects[$('#txtPro').val()]["regions"][coorIndex[0]]
						
						//shift array indexes down
						for (i = coorIndex[0]; i<upPro.length; i++){
							upPro[i] = upPro[i+1]
						}
						upPro.length = upPro.length - 1
						for (por in projects.projects){
							for(i=0; i<projects.projects[por]["regions"].length; i++){
								if (projects.projects[por]["regions"][i]["coordinate_region"]==$("#txtCR").val()){
									check.push($("#txtCR").val())
								}
							}
						}
						if (check.length == 0){
							delete projects.regions[$("#txtCR").val()]
						}
						fillCR()
						alert (regType + " region has been deleted.")
						clears()
						closeForm('delForm')
					}else if (regType == "Seed" && $("#txtSR").val().length == 1){ 
						var regionIndex = [] //where in the project regions it is
						var seedIndex //index of where the seed region is in the specific region
						for (i=0; i<$("#txtCR").val().length; i++){
							for (j=0; j<$("#txtCR option").length;j++){		
								if ($("#txtCR option")[j].innerHTML == $("#txtCR").val()[i]){
									regionIndex.push(j)
								}
							}
							seedIndex = upPro[regionIndex[i]]["seed_region_names"].indexOf($("#txtSR").val().toString())
							delete upPro[regionIndex[i]]["seed_region_names"][seedIndex]
							for (k = seedIndex; k < upPro[regionIndex[i]]["seed_region_names"].length; k++){
								upPro[regionIndex[i]]["seed_region_names"][k] = upPro[regionIndex[i]]["seed_region_names"][k+1]
							}
						upPro[regionIndex[i]]["seed_region_names"].length = upPro[regionIndex[i]]["seed_region_names"].length -1
						}
						for (por in projects.projects){
							for(i=0; i<projects.projects[por]["regions"].length; i++){
								for(j=0; j<projects.projects[por]["regions"][i]["seed_region_names"].length; j++){
									if (projects.projects[por]["regions"][i]["seed_region_names"][j]==$("#txtSR").val()){
										check.push($("#txtSR").val())
									}
								}
							}
						}
						if (check.length == 0){
							delete projects.regions[$("#txtSR").val()]
						}	
						fillSR()
						alert (regType + " region has been deleted.")
						clears()
						closeForm('delForm')
					}
				}
				
			}

		}
	}
}

function fillAddPro() {  //fills in the list of projects
	$('#addProj')[0].innerHTML = ""
	var proSelect = $('#addProj')[0]; 
	var por = projects.projects; 
	var option = document.createElement("option"); 
		option.text = "New Project";
		proSelect.add(option)
	for (por in projects.projects){ 
		var option = document.createElement("option"); 
		option.text = por; 
		proSelect.add(option); 
	} 
}

function fillAddCR(){ //fills coordinate regions in add form
	$("#cooregion")[0].innerHTML = ""
	var pro = projects.projects

		var cooSelect = $("#cooregion")[0]
		for (i=0; i< pro[$("#addProjName").val()]["regions"].length; i++){
			var option = document.createElement("option"); 
			option.text = pro[$("#addProjName").val()]["regions"][i]["coordinate_region"]; 
			cooSelect.add(option); 
		} 
	
}

function addPCheck(){ //checks for new or existing project
	
	var pro = projects.projects
	var reg = projects.regions
	if ($("#addProj").val() !== "New Project"){ //existing, fields cant be edited, fills the fields with existing data
		$("#addProjName").val($("#addProj").val())
		$("#addProjName").prop("readonly", true)
		$("#addVar").val(pro[$("#addProj").val()]["max_variants"].toString())
		$("#addVar").prop("readonly", true)
		$("#addDes").val(pro[$("#addProj").val()]["description"].toString())
		$("#addDes").prop("readonly", true)	

	}else if ($("#addProj").val() == "New Project"){ //new project, fields are editable
		$("#addProjName").val("")
		$("#addProjName").prop("readonly", false)
		$("#addVar").val("")
		$("#addVar").prop("readonly", false)
		$("#addDes").val("")
		$("#addDes").prop("readonly", false)
	}
}

function addPO(){ //regarding the project fields
	if ($("#addProj").val() == "New Project"){
		var newProj = $("#addProjName").val()
		var newValue = {"max_variants": $("#addVar").val(), "description": $("#addDes").val(), "regions": []}
		var pro = projects.projects
		var existP = 0

		for (i=1; i<$("#addProj option").length; i++){
			if ($("#addProjName").val() == $("#addProj option")[i].innerHTML){
				existP += 1
			}
		} 
		
		//checks for empty fields, and if max variants is a number
		if ($("#addProjName").val() !== "" && isNaN($("#addVar").val())== false && $("#addVar").val() !== "" && $("#addDes").val() !=="" && existP == 0){ 
			pro[newProj] = newValue
			$("#addregion").show()
			$("#addProjName").prop("readonly", true)
			$("#addVar").prop("readonly", true)
			$("#addDes").prop("readonly", true)
			fillAddPro()
		}else if(existP > 0){
			alert("Project name already in use.")
		}else if(isNaN($("#addVar").val())== true){
			alert("Max Variants must be a number")
		}else if($("#addProjName").val() == "" || $("#addVar").val() == "" || $("#addDes").val() ==""){
			alert("Fields are empty.")
		}
		
	}else if ($("#addProj").val() !== "New Project"){
		$("#addregion").show()

	}
}


function addRCheck(){ //checks for coordinate or seed that user wanted to add
	if($("#addRegi").val() == "coordinate"){
		$("#seedgrouptext").hide()
	}else if ($("#addRegi").val() == "seed"){
		$("#seedgrouptext").show()
	}
	$("#common").show()
	$("#regionbut").show()
	$("#addRegName").val("")
	$("#addSequence").val("")
	$("#addSeedGroup").val("")
	
}


function seedShow(){ //displays the seed regions of the selected coordinate region in add form
	$("#seeregion")[0].innerHTML = ""
	var pro = projects.projects
	var seeSelect = $("#seeregion")[0]
	var seedcheck = []

	for (i=0; i< pro[$("#addProjName").val()]["regions"].length; i++){
		for (j=0; j<$("#cooregion").val().length; j++){
			if (pro[$("#addProjName").val()]["regions"][i]["coordinate_region"] == $("#cooregion").val()[j]){		
				for (k=0; k< pro[$("#addProjName").val()]["regions"][i]["seed_region_names"].length; k++){
					if (seedcheck.includes(pro[$("#addProjName").val()]["regions"][i]["seed_region_names"][k])== false){					
						var option = document.createElement("option"); 
						option.text = pro[$("#addProjName").val()]["regions"][i]["seed_region_names"][k]; 
						seeSelect.add(option); 
					}
					seedcheck.push(pro[$("#addProjName").val()]["regions"][i]["seed_region_names"][k])
				}
			}
		}
	} 
	$("#group")[0].innerHTML = ""
}

function groupShow(){
	$("#group")[0].innerHTML = ""
	var reg = projects.regions
	var groupcheck = []
	var groupSelect = $("#group")[0]
	for (i=0; i<$("#seeregion").val().length; i++){
		if (groupcheck.includes(reg[$("#seeregion").val()[i]]["seed_group"]) == false){					
			var option = document.createElement("option"); 
			option.text = reg[$("#seeregion").val()[i]]["seed_group"]; 
			groupSelect.add(option); 
		}
		groupcheck.push(reg[$("#seeregion").val()[i]]["seed_group"]) 
	}
}

function addRe(){
	var pro = projects.projects
	var reg = projects.regions
	var isNuc = 0	
	var isAA = 0
	var exist = 0
	var coordSeld = [] = $("#cooregion").val()
	var addSeq = $("#addSequence").val().replace(/\,/g, '').replace(/\d/g, "").replace(/ +/g, '').replace(/\n/g, "").toUpperCase()
	var aminoCheck = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z",".","-",","," ","*","#"]
	var nucleicCheck = ["A","C","G","T","U","W","S","M","K","R","Y","B","D","H","V","N","Z",".","-",","," ","*","#"]


	for (i=0; i<addSeq.length; i++){ //checks if sequence is nucleotide or not
		if(aminoCheck.includes(addSeq[i])==false){
			isAA += 1 
		}
		if(nucleicCheck.includes(addSeq[i])==false){
			isNuc += 1
		}
	}
	if($("#addRegi").val() == "coordinate"){
		for(i=0; i< $("#cooregion option").length; i++){
			if ($("#addRegName").val() == $("#cooregion option")[i].innerHTML){
				exist += 1
			}
		}
		if ($("#addRegName").val() !== "" && $("#addSequence").val() !== "" && exist == 0){//add check for existing coord with same name in projects and regions
			if(isAA == 0){
				pro[$("#addProjName").val()]["regions"].push ({"coordinate_region": $("#addRegName").val() ,"seed_region_names":[]})
				reg[$("#addRegName").val()] = {"is_nucleotide": false, "reference": addSeq, "seed_group": null}
				fillAddCR()
				$("#cooregion").val($("#addRegName").val())
			}else{
				alert("Must be an amino acid sequence for coordinate region.")
			}
				
		}else if ($("#addRegName").val() == "" || $("#addSequence").val() == ""){
			alert("Fields must be filled in.")
		}else if (exist > 0){
			alert("Region already exists.")
		}

	}else if ($("#addRegi").val() == "seed"){ //add check for existing seed with same name in projects and regions
		if($("#cooregion").val().length == 0){
			alert ("Coordinate region must be selected to add a seed region.") 
		}
		var proIndex = []
		var seedStore = []
		for(i=0; i<$("#cooregion option:selected").length; i++){ //gets index of the chosen coordinate regions in project
			proIndex.push($("#cooregion option:selected")[i].index)
			for(j=0; j<pro[$("#addProjName").val()]["regions"][proIndex[i]]["seed_region_names"].length; j++){
				seedStore.push(pro[$("#addProjName").val()]["regions"][proIndex[i]]["seed_region_names"][j])
			}
		}
		for(i=0; i<seedStore.length; i++){
			if ($("#addRegName").val() == seedStore[i]){
				exist += 1
			}
		}
		var cooCheck = []
		if ($("#addRegName").val() !== "" && $("#addSequence").val() !== "" && $("#addSeedGroup").val() !== "" && exist == 0){
			for (i=0; i< $("#cooregion").val().length; i++){
				for (j=0; j<pro[$("#addProjName").val()]["regions"].length ; j++){ 
					if ($("#cooregion").val()[i] == pro[$("#addProjName").val()]["regions"][j]["coordinate_region"]){
						cooCheck.push(j)
					}	
				}
			}
			if(isNuc == 0){
				for (i=0; i< cooCheck.length; i++){
					pro[$("#addProjName").val()]["regions"][cooCheck[i]]["seed_region_names"].push($("#addRegName").val());
					reg[$("#addRegName").val()] = {"is_nucleotide": true, "reference": addSeq, "seed_group": $("#addSeedGroup").val()};
				}
				$("#cooregion").val(coordSeld)
				seedShow()
				groupShow()
			}else{
				alert("Must be a nucleic acid sequence for seed region.")
			}
		}else if ($("#addRegName").val() == "" || $("#addSequence").val() == "" || $("#addSeedGroup").val() == ""){
			alert("Fields must be filled in.")
		}else if (exist > 0){
			alert("Region already exists.")
		}
	}
}

function clearAdd(){
	$("#addregion").hide()
	$("#addProjName").val("")
	$("#addProjName").prop("readonly", false)
	$("#addVar").val("")
	$("#addVar").prop("readonly", false)
	$("#addDes").val("")
	$("#addDes").prop("readonly", false)	
	$("#addRegName").val("")
	$("#addSequence").val("")
	$("#addSeedGroup").val("")

}

function openForm(x) { //open add or delete form
	document.getElementById(x).style.display = "block";
	$("#addProjName").val("")
	$("#addVar").val("")
	$("#addDes").val("")
	$("#addRegi").val("")
}
function closeForm(x) { //close add or delete form
	document.getElementById(x).style.display = "none";
}


/*
//download file code adapted from https://ourcodeworld.com/articles/read/189/how-to-create-a-file-and-generate-a-download-with-javascript-in-the-browser-without-a-server
function download() { 
  var element = document.createElement('a');
  element.setAttribute("href", 'data:text/plain;charset=utf-8,' + encodeURIComponent(JSON.stringify(projects,null,4)));
  element.setAttribute("target", "_blank")
  document.body.appendChild(element);

  element.click();
}
*/
function download() {
	if (projects !== undefined){
		name = prompt("Enter file name for download.")
		if(name !== "null"){
			if(name == ""){
				name = $("#inputfile")[0].files[0].name
			}		
			if(name.indexOf(".json") == -1){
				name += ".json"
			}
			var element = document.createElement('a');
			element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(JSON.stringify(projects,null,"\t")));
			element.setAttribute('download', name);
		  	  element.setAttribute("target", "_blank")
			document.body.appendChild(element);

			element.click();
		}
	}else{
		alert("No data to be downloaded.")
	}
}
