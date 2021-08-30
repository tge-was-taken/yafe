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

# Usage
1. Download repository as zip (https://github.com/TGEnigma/yafe/archive/refs/heads/main.zip)
2. In 3ds Max, navigate to Scripting, select Run Script and open 'plugin.py'
3. Import FBN or HBN for editing, and export by selecting the FBN/HBN root node and pressing the 'Export' button in the GUI.
