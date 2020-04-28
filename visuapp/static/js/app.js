map_level=[]
map_node=[]
map_link=[]
device_index=['start']

// new variable
mapLevel=[]
mapNode=[]
mapLink=[]
mapDeviceArray=[]

// Refresh the device data
function refreshDataScript(){
  console.log("debut du process")
  $.ajax({
    url: '/refreshDataScript',
    dataType: 'json',
    type: 'POST',
    success: function(response) {
      console.log(JSON.stringify(response));
      // mapCreation(response);
    },
    error: function(error) {
    console.log("error");
    }
  });
}

// Call the python script for the cabling
function mapCablingJscript(){
  $.ajax({
    url: '/mapCablingPy',
    dataType: 'json',
    type: 'POST',
    success: function(response) {
      // console.log(JSON.stringify(response));
      mapCreation(response);
    },
    error: function(error) {
    console.log("error");
    },
  });
}
// Call the python script for the lldp delta - delta betwwen the cabling file and the lldp result
function mapLldpDeltaJscript(){
  $.ajax({
    url: '/mapLldpDeltaPy',
    dataType: 'json',
    type: 'POST',
    success: function(response) {
      mapCreation(response);
    },
    error: function(error) {
    console.log("error");
    },
  });
}
// Call the python script for the interfaces status
function mapInterfacesStatusJscript(){
  $.ajax({
    url: '/mapInterfacesStatusPy',
    dataType: 'json',
    type: 'POST',
    success: function(response) {
      mapCreation(response);
    },
    error: function(error) {
    console.log("error");
    },
  });
}
// Call the python script for the BGP status
function mapBGPJscript(){
  $.ajax({
    url: '/mapBGPPy',
    dataType: 'json',
    type: 'POST',
    success: function(response) {
      mapCreation(response);
    },
    error: function(error) {
    console.log("error");
    },
  });
}
// Call the python script for the EVPN status
function mapEVPNJscript(){
  $.ajax({
    url: '/mapEVPNPy',
    dataType: 'json',
    type: 'POST',
    success: function(response) {
      mapCreation(response);
    },
    error: function(error) {
    console.log("error");
    },
  });
}

// Call the python script for the Mlag status
function mapMlagJscript(){
  $.ajax({
    url: '/mapMlagPy',
    dataType: 'json',
    type: 'POST',
    success: function(response) {
      mapCreation(response);
    },
    error: function(error) {
    console.log("error");
    },
  });
}

// Manage the link or device color
function linkColor(valueGlobal){
  // Test for Delta LLDP or interface status
  value3 = valueGlobal[2]
  // link color
  console.log(valueGlobal)
  if (value3.indexOf("device") == -1) {
    if (value3 == 'ok'){
      edgeColor = '#07A513'
    }
    else if (value3 == 'ko'){
      edgeColor = '#FF0040'
    }
    else{
      edgeColor = '#0000ff'
    }
    return edgeColor
  }
  // node color 
  else {
    mapNode.forEach(function(item) {
      if (valueGlobal[0] == item['label']){
        if (value3.split('device')[1] == 'ok'){
          item['image'] = 'static/img/pumpkin-green.png'
        }
        else if (value3.split('device')[1] == 'ko'){
          item['image'] = 'static/img/pumpkin-red.png'
        }
      } 
    });
  }
}
// MAP creation
function mapCreation(response){
  // init the node counter
  nodeId = 0;
  // Store the number of level
  for (var key in response) {
    mapLevel.push(key)
  }
  // Read for each level the value and store the node name and the level
  for (index in mapLevel){
    for (var key in response[mapLevel[index]]){
      // node creation for vis
      if (mapDeviceArray.indexOf(key) == -1){
        nodeId++;
        var obj = { id: nodeId, label: key, level: Number(index)+1, title: key, image: 'static/img/pumpkin-back.png',shape: "image"};
        mapNode.push(obj)
        mapDeviceArray.push(key)
      } 
      // Read the value and extract the Node
      for (var key1 in response[mapLevel[index]][key]){
        labelDevice = response[mapLevel[index]][key][key1][0]
        if (mapDeviceArray.indexOf(labelDevice) == -1){
          nodeId++;
          var obj = { id: nodeId, label: labelDevice, level: Number(index)+2, title: labelDevice, image: 'static/img/pumpkin-back.png',shape: "image"};
          mapNode.push(obj)
          mapDeviceArray.push(labelDevice)

        }
      }
    }
  }
  // Link between node
  for (index in mapLevel){
    for (var key in response[mapLevel[index]]){
      linkStart = mapDeviceArray.indexOf(key)+1
      for (var key1 in response[mapLevel[index]][key]){
        labelDevice = response[mapLevel[index]][key][key1][0]
        interfDevice = response[mapLevel[index]][key][key1][1]
        linkEnd = mapDeviceArray.indexOf(labelDevice)+1
        // call the test function
        // Check if the array has 3 elements
        if ((response[mapLevel[index]][key][key1]).length == 3){
          // edgeColor = linkColor(response[mapLevel[index]][key][key1][2])
          edgeColor = linkColor(response[mapLevel[index]][key][key1])

        }
        else {
          edgeColor = '#0000ff'
        }
        var obj = {from: linkStart, to: linkEnd, title: key1+"-"+interfDevice, color:{color:edgeColor}, smooth: {type: "curvedCW", roundness: 0}};
        mapLink.push(obj);
      }
    }
  }


  // print the map
  mapDefinition(mapNode,mapLink);
}
// Vis definition and parameters
function mapDefinition(nodeMap,linkMap){
  // create an array with nodes
  var nodes = new vis.DataSet(nodeMap);
  // create an array with the link
  var edges = new vis.DataSet(linkMap);
  // create a network
  var container = document.getElementById('mynetwork');
  // provide the data in the vis format
 data = {
   nodes: nodes,
   edges: edges
 };
 var options = {
  //  width: '100%',
  //  height: '100%',
   physics: {
     enabled: false,
     minVelocity: 0.75
   },
   layout: {
    //  improvedLayout: true,
     hierarchical: {
       enabled: true,
       levelSeparation: 800,
      //  blockShifting: true,
      //  edgeMinimization: true,
      // parentCentralization: false, 
       direction: 'UD',
       nodeSpacing: 300,
       sortMethod: 'directed'
     }
   },

  edges: {
    smooth: true,
    color : {
      inherit: false
    }
  },
   interaction:{hover:true}
 };
 // initialize your network!
 network = new vis.Network(container, data, options);

 network.on("selectNode", function(params){
  document.getElementById("nodeIdentification").value = nodes.get(params.nodes[0])['label'];
 });
 network.on("selectEdge", function(params){
  // document.getElementById("nodeIdentification").value = nodes.get(params.nodes[0])['label'];
  console.log(params)
 });
}