import asyncio
from datetime import datetime
from jsonrpclib import Server
from jsonrpclib.jsonrpc import AppError
import os, sys, re
import time
import json
from netaddr import *


# username and password for the connection
username = 'dwarf'
password = 'arista'

deviceNotConnected=[]

# devices =['spine1','spine2','leaf1-A','leaf1-B','leaf2-A','leaf2-B','leaf3-A','leaf4']

commandes=['show lldp neighbors detail',
            'show version',
            'show interfaces status',
            'show ip interface',
            'show ip bgp summary',
            'show bgp evpn summary',
            'show mlag',
            'show mlag interfaces members',
            'show mlag interfaces detail',
            'show lacp neighbor all-ports',
            'show bgp evpn route-type imet',
            'show ip route summary',
            'show environment power']

def deviceInventory():
  deviceArray=[]
  # Read the source of truth
  data = readDataJsonFile('referenceCablingMap')
  # Start the process
  # Reaf the level and the value - level1,level2,level3
  for level, levelValue in data.items():
    # Read the device name in the levelValue
    for device,deviceValue in levelValue.items():
      if device not in deviceArray:
        deviceArray.append(device)
      # Read the interface and the value associated to the device
      for interface,interfaceValue in deviceValue.items():
        if interfaceValue[0] not in deviceArray:
          deviceArray.append(interfaceValue[0])
  return deviceArray

# Write data from the device in a file for future analysis
def writeData(device,data):
  with open('visuapp/static/data/'+device+'.json', 'w') as outfile:
    json.dump(data, outfile)
  outfile.close()

# Read a json file
def readDataJsonFile(file):
  try:
    with open('visuapp/static/data/' + file + '.json') as jsondata:
      data = json.load(jsondata)
      return data
  except:
    pass

# Connection to the switch
def openconnexion(device,username,password,cde):
  switch = Server("http://%s:%s@%s/command-api" %(username,password,device))
  try:
    # result = switch.runCmds(version = 1, cmds = cde)
    result = switch.runCmds(version = "latest", cmds = cde)
    # Format the result if result is not empty
    if result != None:
      data = {}
      for index in range(0,len(result)):
        data.update({cde[index].replace(" ",""):result[index]})
      writeData('devices/' + device,data)
  
  except AppError as err:
    code = err.args[0][0]
    error = err.args[0][1]
    if code == 1000:
      erreurCde = error.split("'")[1]
      commandes.remove(erreurCde)
      openconnexion(device,username,password,commandes)
  except:
    deviceNotConnected.append(device)
    data = {}
    writeData('devices/' + device,data)

# Connection TEST
def openconnexionTest(device,username,password,cde):
  switch = Server("http://%s:%s@%s/command-api" %(username,password,device))
  result = switch.runCmds(version = 1, cmds = cde)
  print (result)


def main():
  start_time_Final = datetime.now()
  devices = deviceInventory()
  for device in devices:
    print ("******************" + device + "*******************************")
    openconnexion(device,username,password,commandes)
    # openconnexionTest(device,username,password,commandes)
  totalFinal = datetime.now() - start_time_Final
  print (totalFinal)

# Define the pdf data
def cablingReportPdf():
  # Read the cabling file = source of truth
  data = readDataJsonFile('referenceCablingMap')
  index = 1
  items = []
  for levelKey,levelValue in data.items():
    for deviceKey,deviceValue in levelValue.items():
      for interfaceKey,interfaceValue in deviceValue.items():
        indexString = str(index)
        an_item = dict(id=indexString, localDevice=deviceKey,localPort=interfaceKey, remoteDevice=interfaceValue[0], remotePort=interfaceValue[1])
        items.append(an_item)
        index +=1
  resultPdf ={"items":items,"testResult":"NA"}
  writeData('result/cablingReport',resultPdf)

# Process for the lldp delta function
def mapLldpDelta():
  # Read the cabling file = source of truth
  data = readDataJsonFile('referenceCablingMap')
  index = 1
  items = []
  testResult = 0
  for levelKey,levelValue in data.items():
    for deviceKey,deviceValue in levelValue.items():
      # Load the file associated to the device
      deviceData = readDataJsonFile('devices/'+ deviceKey)
      # Store the interface from the cabling 
      for interfaceKey,interfaceValue in deviceValue.items():
        # Search the interfaceKey in the deviceData (configuration) file
        interface = "Ethernet"+str(interfaceKey)
        # Test if the section exist
        if 'showlldpneighborsdetail' in deviceData.keys():
          # Test if the interface is present in the lldp
          if interface in deviceData['showlldpneighborsdetail']['lldpNeighbors']:
            # Test if there is some information linked to the interface - remote devie.
            if len(deviceData['showlldpneighborsdetail']['lldpNeighbors'][interface]['lldpNeighborInfo']) > 0:
              lldpRemoteDevice = deviceData['showlldpneighborsdetail']['lldpNeighbors'][interface]['lldpNeighborInfo'][0]['systemName']
              lldpRemotePort = (deviceData['showlldpneighborsdetail']['lldpNeighbors'][interface]['lldpNeighborInfo'][0]['neighborInterfaceInfo']['interfaceId']).replace('"','')
              # Test if the remote device is equal to what we have from the cabling
              if interfaceValue[0] == deviceData['showlldpneighborsdetail']['lldpNeighbors'][interface]['lldpNeighborInfo'][0]['systemName']:
                # Test if the remote port is equal to what we have from the cabling
                if "Ethernet" + interfaceValue[1] == (deviceData['showlldpneighborsdetail']['lldpNeighbors'][interface]['lldpNeighborInfo'][0]['neighborInterfaceInfo']['interfaceId']).replace('"',''):
                  data[levelKey][deviceKey][interfaceKey].append("ok")
                  status ="ok"
                else:
                  data[levelKey][deviceKey][interfaceKey].append("ko")
                  status ="ERROR"
                  testResult+=1
              else:
                data[levelKey][deviceKey][interfaceKey].append("ko")
                status ="ERROR"
                testResult+=1
            else:
              data[levelKey][deviceKey][interfaceKey].append("ko")
              lldpRemoteDevice = "unknow"
              lldpRemotePort = "unknow"
              status ="ERROR"
              testResult+=1
          else:
            data[levelKey][deviceKey][interfaceKey].append("ko")
            lldpRemoteDevice = "unknow"
            lldpRemotePort = "unknow"
            status ="ERROR"
            testResult+=1
        else:
            data[levelKey][deviceKey][interfaceKey].append("ko")
            lldpRemoteDevice = "unknow"
            lldpRemotePort = "unknow"
            interfaceValue[0]="unknow"
            interfaceValue[1]="unknow"
            status ="ERROR"
            testResult+=1

        # Generate the file for the pdf report 
        indexString = str(index)
        an_item = dict(id=indexString, localDevice=deviceKey,localPort=interfaceKey, remoteDevice=interfaceValue[0], remotePort=interfaceValue[1],
        lldpRemoteDevice = lldpRemoteDevice, lldpRemotePort=lldpRemotePort,status=status)
        items.append(an_item)
        index +=1
        if testResult > 0:
          testStatus = "NOT PASS"
        else:
          testStatus = "PASS"
        resultPdf ={"items":items,"testResult":testStatus}
  # Store the result in the file
  writeData('result/lldpMapDelta',data)
  writeData('result/lldpReport',resultPdf)

# Process for the interfaces status
def mapInterfacesStatus():
  # Read the cabling file = source of truth
  data = readDataJsonFile('referenceCablingMap')
  index = 1
  items = []
  testResult = 0
  for levelKey,levelValue in data.items():
    for deviceKey,deviceValue in levelValue.items():
      # Load the file associated to the device
      deviceData = readDataJsonFile('devices/'+ deviceKey)
      # Store the interface from the cabling 
      for interfaceKey,interfaceValue in deviceValue.items():
        # Search the interfaceKey in the deviceData (configuration) file
        interface = "Ethernet"+str(interfaceKey)
        # Test if the section exist
        if 'showinterfacesstatus' in deviceData.keys():
          # Test if the interface is present in the show interfces status.
          if interface in deviceData['showinterfacesstatus']['interfaceStatuses']:
            intterfaceStatus = deviceData['showinterfacesstatus']['interfaceStatuses'][interface]['linkStatus']
            # Test if the interface is connected - link up
            if intterfaceStatus == 'connected':
              data[levelKey][deviceKey][interfaceKey].append("ok")
              status ="ok"
            else:
              data[levelKey][deviceKey][interfaceKey].append("ko")
              status ="ERROR"
              testResult+=1
          else:
            data[levelKey][deviceKey][interfaceKey].append("ko")
            status ="ERROR"
            testResult+=1
        else:
          data[levelKey][deviceKey][interfaceKey].append("ko")
          status ="ERROR"
          testResult+=1
  
        # Generate the file for the pdf report 
        indexString = str(index)
        an_item = dict(id=indexString, localDevice=deviceKey,localPort=interfaceKey,status=status)
        items.append(an_item)
        index +=1
        if testResult > 0:
          testStatus = "NOT PASS"
        else:
          testStatus = "PASS"
        resultPdf ={"items":items,"testResult":testStatus}
  # Store the result in the file
  writeData('result/mapInterfacesStatus',data)
  writeData('result/mapInterfacesStatusReport',resultPdf)

# Process for the BGP status
def mapBGPV2():
  # Variable for the pdf generator
  items = []
  testResult = 0
  # Variable for the BGP procedure
  
  # Read the source of truth
  data = readDataJsonFile('referenceCablingMap')
  
  for levelKey,levelValue in data.items():
    for deviceKey,deviceValue in levelValue.items():
      # load the file associated to the device
      deviceData = readDataJsonFile('devices/'+ deviceKey)
      # Test deviceData is empty (None)
      if deviceData == None:
        deviceData={}
      # Store the interface from the cabling 
      for interfaceKey,interfaceValue in deviceValue.items():
        # Search the interfaceKey in the deviceData (configuration) file
        interface = "Ethernet"+str(interfaceKey)
        # Test if the section exist
        if 'showipbgpsummary' in deviceData.keys():
          # Test if the interface is present in the show interfces status.
          # STEP 1 store the ip address associated to the physical interface
          # Test if the interface from the referenceCablingMap exist in the 'device.json' file inside the showipinterface section
          if interface in deviceData['showipinterface']['interfaces']:
            # Store the ip and the mask associated to the interface
            interfaceIp = deviceData['showipinterface']['interfaces'][interface]['interfaceAddress']['primaryIp']['address']
            interfaceMask = deviceData['showipinterface']['interfaces'][interface]['interfaceAddress']['primaryIp']['maskLen']
            # Find the remote address - Because the show ip bgp summary gives the neighbor ip address
            ipList=[]
            for ip in IPSet([interfaceIp+'/'+str(interfaceMask)]):
              ipList.append(str(ip))
            # Remove the local ip address
            del ipList[ipList.index(interfaceIp)]
            ipNeighborBGP = ipList[0]
            #  STEP 2 find the ipNeighborBGP in the showipbgpsummary section of the device.json file.
            # Test if the ipNeighborBGP is present in the peers list
            if ipNeighborBGP in deviceData['showipbgpsummary']['vrfs']['default']['peers']:
              # Test the peerState
              peerState = deviceData['showipbgpsummary']['vrfs']['default']['peers'][ipNeighborBGP]['peerState']
              if deviceData['showipbgpsummary']['vrfs']['default']['peers'][ipNeighborBGP]['peerState'] == 'Established':
                data[levelKey][deviceKey][interfaceKey].append("ok")
                status ="ok"
              else:
                data[levelKey][deviceKey][interfaceKey].append("ko")
                status ="ERROR"
                testResult+=1
              # Call the pdf report function
              dataArray = dict(localDevice=deviceKey,localPort=interfaceKey,
                          localIp=interfaceIp, remoteIp=ipNeighborBGP,
                          peerState=peerState,status=status)
              items = generateReportPdf("BGP",dataArray,items)
            else:
              # ip neighbor address is not present in the show ip bgp summary
              data[levelKey][deviceKey][interfaceKey].append("ko")
              peerState = "ERROR"
              status ="ERROR"
              testResult+=1
              # Call the pdf report function
              dataArray = dict(localDevice=deviceKey,localPort=interfaceKey,
                          localIp=interfaceIp, remoteIp=ipNeighborBGP,
                          peerState=peerState,status=status)
              items = generateReportPdf("BGP",dataArray,items)
          else:
            # Test if the interface is not part of a mlag
            if 'showmlag' in deviceData:
              mlagInterface = deviceData['showmlag']['localInterface']
              mlagPeerLink = deviceData['showmlag']['peerLink']
              # check if the interface is a member of the peerlink
              try:
                if interface in deviceData['showlacpneighborall-ports']['portChannels'][mlagPeerLink]['interfaces'].keys():
                  if mlagInterface in deviceData['showipinterface']['interfaces']:
                    # Store the ip and the mask associated to the interface
                    interfaceIp = deviceData['showipinterface']['interfaces'][mlagInterface]['interfaceAddress']['primaryIp']['address']
                    interfaceMask = deviceData['showipinterface']['interfaces'][mlagInterface]['interfaceAddress']['primaryIp']['maskLen']
                    # Find the remote address - Because the show ip bgp summary gives the neighbor ip address
                    ipList=[]
                    for ip in IPSet([interfaceIp+'/'+str(interfaceMask)]):
                      ipList.append(str(ip))
                    # Remove the local ip address
                    del ipList[ipList.index(interfaceIp)]
                    ipNeighborBGP = ipList[0]
                    #  STEP 2 find the ipNeighborBGP in the showipbgpsummary section of the device.json file.
                    # Test if the ipNeighborBGP is present in the peers list
                    if ipNeighborBGP in deviceData['showipbgpsummary']['vrfs']['default']['peers']:
                      # Test the peerState
                      peerState = deviceData['showipbgpsummary']['vrfs']['default']['peers'][ipNeighborBGP]['peerState']
                      if deviceData['showipbgpsummary']['vrfs']['default']['peers'][ipNeighborBGP]['peerState'] == 'Established':
                        data[levelKey][deviceKey][interfaceKey].append("ok")
                        status ="ok"
                      else:
                        data[levelKey][deviceKey][interfaceKey].append("ko")
                        status ="ERROR"
                        testResult+=1
                        # Call the pdf report function
                        dataArray = dict(localDevice=deviceKey,localPort=interfaceKey,
                                        localIp=interfaceIp, remoteIp=ipNeighborBGP,
                                        peerState=peerState,status=status)
                        items = generateReportPdf("BGP",dataArray,items)
                    else:
                      # ip neighbor address is not present in the show ip bgp summary
                      data[levelKey][deviceKey][interfaceKey].append("ko")
                      peerState = ""
                      status ="ERROR"
                      testResult+=1
                      # Call the pdf report function
                      dataArray = dict(localDevice=deviceKey,localPort=interfaceKey,
                                      localIp=interfaceIp, remoteIp=ipNeighborBGP,
                                      peerState=peerState,status=status)
                      items = generateReportPdf("BGP",dataArray,items)
                else:
                  # print ('Pas dans un port channel')
                  # Call the pdf report function
                  dataArray = dict(localDevice=deviceKey,localPort=interfaceKey,
                                  localIp="None", remoteIp="NA",
                                  peerState="NA",status="NA")
                  items = generateReportPdf("BGP",dataArray,items)
              except KeyError:
                # print ('Pas dans un port channel - interface doesn t exist')
                # Call the pdf report function
                dataArray = dict(localDevice=deviceKey,localPort=interfaceKey,
                                  localIp="None", remoteIp="NA",
                                  peerState="NA",status="NA")
                items = generateReportPdf("BGP",dataArray,items)
            else:
              print ("pas de configuration level 3 pour cette interface")
        else:
          print ("la section showip bgp summary n existe pas")
        # Generate the file for the pdf report 
        if testResult > 0:
          testStatus = "NOT PASS"
        else:
          testStatus = "PASS"
        resultPdf ={"items":items,"testResult":testStatus}
  # Store the result in the file
  writeData('result/BGPStatus',data)
  writeData('result/BGPReport',resultPdf)

# Process for the EVPN
def mapEVPNV2():
  spines=[]
  loopback0LeafJson={}
  dataEvpnMap={'level1':{}}
  deviceWithoutL0=[]
  spinePortCounter={}
  testResult =0
  items=[]
  # Read the source of truth
  data = readDataJsonFile('referenceCablingMap')
  # Inventory device
  devices = deviceInventory()
  for device in data['level1'].keys():
    # remove the spine from the inventory
    devices.remove(device)
    # add the spine 
    spines.append(device)
  # Read the loopback 0 on the leaf
  for device in devices:
    # Load the json file associated to the the device
    deviceData = readDataJsonFile('devices/'+device)
    if deviceData == None:
      deviceData={}
    # Test if loopback0 exist -
    try:
      if 'Loopback0' in deviceData['showipinterface']['interfaces'].keys():
        # store the lopoback as a key and the device name as a value
        loopback0LeafJson[deviceData['showipinterface']['interfaces']['Loopback0']['interfaceAddress']['primaryIp']['address']] = device
        # loopback1Leaf.append(deviceData['showipinterface']['interfaces']['Loopback1']['interfaceAddress']['primaryIp']['address'])
    except KeyError:
      print ("loopback0 doesn't exist")
      deviceWithoutL0.append(device)
  # Check the EVPN connectivity from the spine
  for spine in spines:
    spinePort = 1
    dataEvpnMap['level1'][spine]={}
    # Load the json file associated to the the device
    deviceData = readDataJsonFile('devices/'+spine)
    if deviceData == None:
      deviceData={}
    # Test if the showbgpevpnsummary record exist in deviceData
    if 'showbgpevpnsummary' in deviceData:
      for key in deviceData['showbgpevpnsummary']['vrfs']['default']['peers'].keys():
        if key in loopback0LeafJson.keys():
          device = loopback0LeafJson[key]
          devicePort = spines.index(spine)
          # Check the session state
          if deviceData['showbgpevpnsummary']['vrfs']['default']['peers'][key]['peerState'] == 'Established':
            state = 'ok'
            peerState = 'Established'
          else:
            state = 'ko'
            peerState = 'ERROR'
            testResult+=1
          dataEvpnMap['level1'][spine].update({str(spinePort):[device,str(devicePort+1),state]})
          # Gen pdf report *****************************
          dataArray = dict(localDevice=spine, remoteDevice=device,peerState=peerState,evpnPeer=key,status=state)
          items = generateReportPdf("EVPNV2",dataArray,items)
          # ********************************************
        else:
          devicePort = spines.index(spine)
          dataEvpnMap['level1'][spine].update({str(spinePort):[device,str(devicePort+1),"Error"]})
          # Gen pdf report *****************************
          dataArray = dict(localDevice=spine, remoteDevice="unknow",peerState="unknow",evpnPeer=key,status="ERROR")
          items = generateReportPdf("EVPNV2",dataArray,items)
          testResult+=1
          # ********************************************
        spinePort +=1
        spinePortCounter.update({spine:spinePort})
  # Add device without loopback0
  for spine in spines:
    spinePort = spinePortCounter[spine]
    for device in deviceWithoutL0:
      devicePort = spines.index(spine)
      dataEvpnMap['level1'][spine].update({str(spinePort):[device,str(devicePort+1),"NA"]})
      spinePort +=1

  # Generate the file for the pdf report 
  if testResult > 0:
    testStatus = "NOT PASS"
  else:
    testStatus = "PASS"
  resultPdf ={"items":items,"testResult":testStatus}
  
  # Store the result in the file
  writeData('result/EVPNV2Status',dataEvpnMap)
  writeData('result/EVPNV2Report',resultPdf)

# Process for the mlag
def mlagStatus():
  # Delete the file
  try:
    os.remove('visuapp/static/data/result/mlagPortChannel.json')
  except:
    pass
  # Variable for the pdf generator
  items = []
  testResult = 0
  # Variable for the Mlag procedure
  deviceMlagStatus=""
  # Read the source of truth
  data = readDataJsonFile('referenceCablingMap')
  # Inventory device
  devices = deviceInventory()
  # Remove the spine
  devices = removeSpineFromInventory(devices,data)
  
  # Start the process
  # Load the json file associated to the the device
  for device in devices:
    deviceData = readDataJsonFile('devices/'+device)
    # Test deviceData is empty (None)
    if deviceData == None:
      deviceData={}
    # Test if showmlag exit
    if 'showmlag' in deviceData.keys():
      counterConfiguration = 0 #Increment if the parameter is defined
      if 'state' in deviceData['showmlag']:
        mlagState = deviceData['showmlag']['state']
        if mlagState == 'active':
          counterConfiguration +=1
      if 'localInterface' in deviceData['showmlag']:
        mlagLocalInterface = deviceData['showmlag']['localInterface']
        if len(mlagLocalInterface) == 0:
          mlagLocalInterface = 'unknow'
        else:
          counterConfiguration +=1
      if 'peerLink' in deviceData['showmlag']:
        mlagPeerLink = deviceData['showmlag']['peerLink']
        if len(mlagPeerLink) == 0:
          mlagPeerLink = 'unknow'
        else:
          counterConfiguration +=1
          # call the verification port-channel for the peerLink function
          dataMlagPortChannel = deviceData['showlacpneighborall-ports']['portChannels'][mlagPeerLink]
          mlagPortChannel(device,dataMlagPortChannel,mlagPeerLink)
      if 'peerAddress' in deviceData['showmlag']:
        mlagPeerAddress = deviceData['showmlag']['peerAddress']
        counterConfiguration +=1
      if 'configSanity' in deviceData['showmlag']:
        mlagConfigSanity = deviceData['showmlag']['configSanity']
        counterConfiguration +=1
      if 'domainId' in deviceData['showmlag']:
        mlagDomainId = deviceData['showmlag']['domainId']
        if len(mlagDomainId) == 0:
          mlagDomainId = 'unknow'
        else:
          counterConfiguration +=1
      # if all the parameters are set counterConfiguration is 6
      # test the state status
      if counterConfiguration == 6:
        if mlagState == 'active':
          deviceMlagStatus = "deviceok"
        else:
          deviceMlagStatus = 'deviceko'
          testResult+=1
      elif 0 < counterConfiguration < 6:
        deviceMlagStatus = 'deviceko'
        testResult+=1
      # No configuration
      elif counterConfiguration == 0:
        deviceMlagStatus = 'deviceNA'
        mlagState = "NA"
        mlagDomainId = "NA"
        mlagLocalInterface = "NA"
        mlagPeerAddress = "NA"
        mlagPeerLink = "NA"
        mlagConfigSanity ="NA"


      # Call the pdf report function
      dataArray = dict(localDevice=device, domainId=mlagDomainId,
                        localInterface=mlagLocalInterface,peerAddress=mlagPeerAddress,
                        peerLink=mlagPeerLink,configSanity=mlagConfigSanity,
                        status=mlagState)
      items = generateReportPdf("MLAG",dataArray,items)
      # Update the data variable
      for levelKey in data.keys():
        for deviceKey in data[levelKey].keys():
          for key,value in data[levelKey][deviceKey].items():
            # find the device that we are processin
            if device == value[0]:
              data[levelKey][deviceKey][key].append(deviceMlagStatus)
    # No mlag configuration
    else:
      # Call the pdf report function
      dataArray = dict(localDevice=device, domainId='NA',
                        localInterface='NA',peerAddress='NA',
                        peerLink='NA',configSanity='NA',
                        status='NA')
      items = generateReportPdf("MLAG",dataArray,items)
    # Generate the file for the pdf report 
    if testResult > 0:
      testStatus = "NOT PASS"
    else:
      testStatus = "PASS"
    resultPdf ={"items":items,"testResult":testStatus}

  # Store the result in the file
  writeData('result/mlagStatus',data)
  writeData('result/mlagReport',resultPdf)

# Process MLAG for the port-channel
# the port-channel must combine 2 ports at least.
def mlagPortChannel(device,data,mlagPeerLink):
  items = [] 
  dataInitial = readDataJsonFile('result/mlagPortChannel')
  if dataInitial != None:
    items = dataInitial['items']
  # Variable for the pdf 
  testResult = 0
  # Verify the number of ports in the portchannel must be >2
  mlagPeerLinkPort = data['interfaces'].keys()
  # Verify the number of pot in the portchannel must be >2
  if len(mlagPeerLinkPort) >1:
    mlagPeerLinkPortState = "ok"
  else:
    mlagPeerLinkPortState = "ko"
  # Test each port of the peerLink
  for interface in mlagPeerLinkPort:
    # The result must be true for the synchronization
    mlagPeerLinkSyncronization = data['interfaces'][interface]['partnerPortState']['synchronization']
    # Call the pdf report function
    dataArray = dict(localDevice=device, portChannel = mlagPeerLink,nbrePort=len(mlagPeerLinkPort),
                      stateNbrePort=mlagPeerLinkPortState,ethernetPort=interface,
                      synchronization=mlagPeerLinkSyncronization,status="to be defined")
    items = generateReportPdf("MLAGPeerLink",dataArray,items)
    resultPdf ={"items":items}
  # Store the result in a file
    writeData('result/mlagPortChannel',resultPdf)

# Multi agent protocol
def multiAgentPdf():
  testResult = 0
  localTestResult = 0
  items=[]

  # Inventory device
  devices = deviceInventory()
  for device in devices:
    localTestResult = 0
    # Load the json file associated to the the device
    deviceData = readDataJsonFile('devices/'+device)
    if deviceData == None:
      deviceData={}
    # Test if showiproutesummary section exist -
    if 'showiproutesummary' in deviceData.keys():
      # store the result
      configure = deviceData['showiproutesummary']['protoModelStatus']['configuredProtoModel']
      operating = deviceData['showiproutesummary']['protoModelStatus']['operatingProtoModel']
      if configure != "multi-agent":
        localTestResult +=1
        testResult +=1
      if operating != "multi-agent":
        localTestResult +=1
        testResult +=1
      if localTestResult == 2:
        state = "ERROR"
        action = "to be verify"
      elif localTestResult == 1:
        state = "ERROR"
        action = "reboot needed"
      else :
        state = "ok"
        action = "none"
      
      # Gen pdf report *****************************
      dataArray = dict(localDevice=device, configure=configure,operating=operating,action=action,status=state)
      items = generateReportPdf("multiAgent",dataArray,items)
      # ********************************************
  # Generate the file for the pdf report 
  if testResult > 0:
    testStatus = "NOT PASS"
  else:
    testStatus = "PASS"
  resultPdf ={"items":items,"testResult":testStatus}
  
  # Store the result in the file
  writeData('result/multiAgentReport',resultPdf)

# Power Supply
def powerSupplyPdf():
  testResult = 0
  items=[]
  # Inventory device
  devices = deviceInventory()
  for device in devices:
    localTestResult = 0
    # Load the json file associated to the the device
    deviceData = readDataJsonFile('devices/'+device)
    if deviceData == None:
      deviceData={}
    # Test if showiproutesummary section exist -
    if 'showenvironmentpower' in deviceData.keys():
      # store the result
      for key in deviceData['showenvironmentpower']['powerSupplies'].keys():
        powerId = key
        state = deviceData['showenvironmentpower']['powerSupplies'][key]['state']
        if state != "ok":
          testResult +=1
        modelName = deviceData['showenvironmentpower']['powerSupplies'][key]['modelName']
        testStatus = "Pass"
        # Call the pdf report function
        dataArray = dict(localDevice=device,powerId=key,
                          state=state, modelName=modelName)
        items = generateReportPdf("powerSupply",dataArray,items)
    else:
      definedAnswer = "NA"
      # Call the pdf report function
      dataArray = dict(localDevice=device,powerId=definedAnswer,
                        state=definedAnswer, modelName=definedAnswer)      
      items = generateReportPdf("powerSupply",dataArray,items)


  # Generate the file for the pdf report 
  if testResult > 0:
    testStatus = "NOT PASS"
  else:
    testStatus = "PASS"
  resultPdf ={"items":items,"testResult":testStatus}
  # Store the result in the file
  writeData('result/powerSupply',resultPdf)
  





# Process evpn imet
def EVPNimet():
  print("to be developp")
  


# remove the spine from the inventory
def removeSpineFromInventory(devices,data):
  for device in data['level1'].keys():
    # remove the spine from the inventory
    devices.remove(device)
  return devices

# Generate the pdf report
def generateReportPdf(reportName,dataArray,items):
  try:
    index = len(items)+1
  except (TypeError, AttributeError):
    index = 1
  indexString = str(index)
  dataArray['id'] = indexString
  an_item = dataArray
  items.append(an_item)
  return items



# main()
powerSupplyPdf()