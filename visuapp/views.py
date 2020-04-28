from flask import Flask, render_template, make_response
import pdfkit
import os
import json
import dwarfFunction
import asyncio

app = Flask(__name__)

app.config.from_object('config')

# Setup for the pdf document
options = {
    'page-size': 'A4',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'no-outline': None
}

@app.route('/refreshData')
def refreshData():
  dwarfFunction.main()
  return render_template('index.html')

@app.route('/')
def index():
  return render_template('index.html')

# MAP CABLING ********************************************************
@app.route('/mapCabling')
def mapCabling():
  return render_template('mapCabling.html')

@app.route('/mapCablingPy',methods=['POST'])
def mapCablingPy():
  # Call the function to generate the pdf report
  dwarfFunction.cablingReportPdf()
  with open('visuapp/static/data/referenceCablingMap.json') as jsondata:
    data = json.load(jsondata)
  return data

@app.route('/mapCablingPdf')
def mapCablingPdf():
  with open('visuapp/static/data/result/cablingReport.json') as jsondata:
    data = json.load(jsondata)
  title = {'title': 'Reference Cabling'}
  rendered = render_template('mapCablingPdf.html',data=data, title=title)
  pdf= pdfkit.from_string(rendered,False)
  response = make_response(pdf)
  response.headers['Content-type'] = 'application/pdf'
  response.headers['Content-Disposition'] = 'inline; filename=mapCablingPdf.pdf; options=options'
  return response
# **************************************************************************************************

# MAP LLDP AND DELTA WITH THE CABLING **************************************************************
@app.route('/mapLldpDelta')
def mapLldpDelta():
  return render_template('mapLldpDelta.html')

@app.route('/mapLldpDeltaPy',methods=['POST'])
def mapLldpDeltaPy():
  dwarfFunction.mapLldpDelta()
  with open('visuapp/static/data/result/lldpMapDelta.json') as jsondata:
    data = json.load(jsondata)
  return data

@app.route('/mapLldpDeltaPdf')
def mapLldpDeltaPdf():
  with open('visuapp/static/data/result/lldpReport.json') as jsondata:
    data = json.load(jsondata)
  title = {'title': 'Delta Between Cabling and LLDP'}
  rendered = render_template('mapLldpDeltaPdf.html',data=data, title=title)
  pdf= pdfkit.from_string(rendered,False)
  response = make_response(pdf)
  response.headers['Content-type'] = 'application/pdf'
  response.headers['Content-Disposition'] = 'inline; filename=mapLldpDeltaPdf.pdf; options=options'
  return response
# **************************************************************************************************

# MAP INTERFACES STATUS FROM THE CABLING ***********************************************************
@app.route('/mapInterfaceStatus')
def mapInterfaceStatus():
  return render_template('mapInterfacesStatus.html')

@app.route('/mapInterfacesStatusPy',methods=['POST'])
def mapInterfacesStatusPy():
  dwarfFunction.mapInterfacesStatus()
  with open('visuapp/static/data/result/mapInterfacesStatus.json') as jsondata:
    data = json.load(jsondata)
  return data

@app.route('/mapInterfacesStatusPdf')
def mapInterfacesStatusPdf():
  with open('visuapp/static/data/result/mapInterfacesStatusReport.json') as jsondata:
    data = json.load(jsondata)
  title = {'title': 'Interfaces Status'}
  rendered = render_template('mapInterfacesStatusPdf.html',data=data, title=title)
  pdf= pdfkit.from_string(rendered,False)
  response = make_response(pdf)
  response.headers['Content-type'] = 'application/pdf'
  response.headers['Content-Disposition'] = 'inline; filename=mapInterfacesStatusPdf.pdf; options=options'
  return response
# **************************************************************************************************

# MAP BGP STATUS FROM THE CABLING ***********************************************************
@app.route('/mapBGP')
def mapBGP():
  return render_template('mapBGP.html')

@app.route('/mapBGPPy',methods=['POST'])
def mapBGPPy():
  dwarfFunction.mapBGPV2()
  with open('visuapp/static/data/result/BGPStatus.json') as jsondata:
    data = json.load(jsondata)
  return data

@app.route('/mapBGPPdf')
def mapBGPPdf():
  with open('visuapp/static/data/result/BGPReport.json') as jsondata:
    data = json.load(jsondata)
  title = {'title': 'BGP Status'}
  rendered = render_template('mapBGPPdf.html',data=data, title=title)
  pdf= pdfkit.from_string(rendered,False)
  response = make_response(pdf)
  response.headers['Content-type'] = 'application/pdf'
  response.headers['Content-Disposition'] = 'inline; filename=mapBGPPdf.pdf; options=options'
  return response
# **************************************************************************************************

# MAP EVPN STATUS FROM THE CABLING ***********************************************************
@app.route('/mapEVPN')
def mapEVPN():
  return render_template('mapEVPN.html')

@app.route('/mapEVPNPy',methods=['POST'])
def mapEVPNPy():
  dwarfFunction.mapEVPNV2()
  with open('visuapp/static/data/result/EVPNV2Status.json') as jsondata:
    data = json.load(jsondata)
  return data

@app.route('/mapEVPNPdf')
def mapEVPNPdf():
  with open('visuapp/static/data/result/EVPNV2Report.json') as jsondata:
    data = json.load(jsondata)
  title = {'title': 'EVPN Status'}
  rendered = render_template('mapEVPNPdf.html',data=data, title=title)
  pdf= pdfkit.from_string(rendered,False)
  response = make_response(pdf)
  response.headers['Content-type'] = 'application/pdf'
  response.headers['Content-Disposition'] = 'inline; filename=mapEVPNPdf.pdf; options=options'
  return response

# **************************************************************************************************

# MAP MLAG STATUS FROM THE CABLING ***********************************************************
@app.route('/mapMlag')
def mapMlag():
  return render_template('mapMlag.html')

@app.route('/mapMlagPy',methods=['POST'])
def mapMlagPy():
  dwarfFunction.mlagStatus()
  with open('visuapp/static/data/result/MlagStatus.json') as jsondata:
    data = json.load(jsondata)
  return data

@app.route('/mapMlagPdf')
def mapMlagPdf():
  with open('visuapp/static/data/result/mlagReport.json') as jsondata:
    data = json.load(jsondata)
  title = {'title': 'Mlag Status'}
  rendered = render_template('mapMlagPdf.html',data=data, title=title)
  pdf= pdfkit.from_string(rendered,False)
  response = make_response(pdf)
  response.headers['Content-type'] = 'application/pdf'
  response.headers['Content-Disposition'] = 'inline; filename=mapMlagPdf.pdf; options=options'
  return response

@app.route('/mapMlagPeerLinkPdf')
def mapMlagPeerLinkPdf():
  with open('visuapp/static/data/result/mlagPortChannel.json') as jsondata:
    data = json.load(jsondata)
  title = {'title': 'Mlag PeerLink Status'}
  rendered = render_template('mapMlagPeerLinkPdf.html',data=data, title=title)
  pdf= pdfkit.from_string(rendered,False)
  response = make_response(pdf)
  response.headers['Content-type'] = 'application/pdf'
  response.headers['Content-Disposition'] = 'inline; filename=mapMlagPeerLinkPdf.pdf; options=options'
  return response
# **************************************************************************************************

# MAP MLAG STATUS FROM THE CABLING ***********************************************************
@app.route('/multiAgentPdf')
def multiAgentPdf():
  dwarfFunction.multiAgentPdf()
  with open('visuapp/static/data/result/multiAgentReport.json') as jsondata:
    data = json.load(jsondata)
  title = {'title': 'Multi Agent Status'}
  rendered = render_template('multiAgentPdf.html',data=data, title=title)
  pdf= pdfkit.from_string(rendered,False)
  response = make_response(pdf)
  response.headers['Content-type'] = 'application/pdf'
  response.headers['Content-Disposition'] = 'inline; filename=multiAgentPdf.pdf; options=options'
  return response

# **************************************************************************************************
@app.route('/testDescription')
def testDescription():
  return render_template('testDescription.html')



