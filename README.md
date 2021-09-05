# yafe
Yet Another Field Editor.... for Persona 5

# What is it
Yafe allows you to import FBN and HBN files into 3ds Max for easy visual editing. This is primarily intended to be a research tool for the time being.
Not everything is supported yet, as the implementation is based on (read: literally generated from) the 010 templates.
Want more objects supported? Contribute to the template over at https://github.com/TGEnigma/010-Editor-Templates/blob/master/templates/p5_fbn.bt

# Why a Max plugin?
Turns out making your own 3d editor isn't so easy. Who'd have guessed?

Leveraging custom object attributes and the innate 3d editing capabilities of 3ds max, it's not too different from what a handcrafted editor would look like.

# Requirements
* 3ds Max 2022 (because of Python 3 dependency)

# Installation
1. Download repository as zip (https://github.com/TGEnigma/yafe/archive/refs/heads/main.zip)
2. Extract the zip anywhere
3. In 3ds Max, navigate to Scripting, select Run Script and open 'plugin.py'
4. If all goes well, the yafe GUI rollout should display.

# Usage instructions
## Importing
### Supported file types for import
- FBN
- HTB (same format as FBN)

### Process
1. Click 'Import' and select a FBN or HBN file to import
2. To view or edit the properties of an FBN object, select the object and click on the Modify (modifier) tab in the right sidebar.
3. When applicable, an FBN object can be moved/rotated freely in the scene and the changes will be saved on export.

### Notes
Each object type is represented in the scene using specific position/rotation data properties for that type. The positioning data of the scene object takes priority over property values, so any changes to these properties will be lost on export unless they are applied to the scene object directly.

| Object type ID    | Object name   | Position property | Rotation property |
| ----------------- | ------------- | ----------------- | ----------------- |
| 0x46424E30        | header        |                   |                   |
| 1                 | triggers      | Center            |                   |
| 2                 |               |                   |                   |
| 3                 |               |                   |                   |
| 4                 | entrances     | Position          | Rotation          |
| 5                 | hitdefs       | N/A               | N/A               |
| 6                 |               |                   |                   |
| 7                 |               |                   |                   |
| 8                 |               | Position          |                   |
| 9                 |               | Position          |                   |
| 10                |               |                   |                   |
| 11                |               |                   |                   |
| 12                |               |                   |                   |
| 13                |               |                   |                   |
| 14                | npcs          | PathNodes         |                   |
| 15                |               |                   |                   |
| 16                |               |                   |                   |
| 17                |               |                   |                   |
| 18                |               | Position          | Rotation          |
| 19                | triggers2     | Center            |                   |
| 20                |               |                   |                   |
| 21                |               |                   |                   |
| 22                | triggers3     | Center            |                   |
| 23                |               |                   |                   |
| 24                |               |                   |                   |
| 25                |               |                   |                   |
| 26                |               |                   |                   |
| 27                |               |                   |                   |
| 28                |               |                   |                   |
| 29                |               |                   |                   |
| 30                |               |                   |                   |

## Exporting

1. Select the FBN root node (by default these are named after the imported file) 
2. Press the 'Export' button in the GUI.
3. Select the file path to save the new file to.
