# arista_Check
This software allows checking some parameters and create some MAPs.

## Installation
Step 1 :
pip install -r requirement.txt

You have to install manually wkhtmltopdf.

## How to configure
Goto /visuapp/static/data and edit referenceCablingMap.json
The network representation is based on level (from 1 to nn)
In general:
level1 is for the Spine.
level2 is for the Leaf.
level3 is for the distribution Leaf.

Example :
{
  "level1": {
    "spine1": {
      "1": ["leaf1-A","1"],
      "2": ["leaf1-B","1"]
    },
    "spine2": {
      "1": ["leaf1-A","2"],
      "2": ["leaf1-B","2"]
    }
  },
  "level2": {
    "leaf1-A": {
      "3": ["leaf1-B","3"],
      "5": ["leaf3-A","1"]
    },
    "leaf1-B":{
      "5": ["leaf3-A","2"],
      "6":["leaf-level2","2"]
    },
    "leaf2-A": {
      "3": ["leaf2-B","3"],
      "4":["leaf4-A","1"]
    },
    "leaf2-B":{
      "4":["leaf4-A","2"]
    }
  },
  "level3":{
    "leaf3-A":{
      "18":["leaf5-A","1"]
    }
  }
}
