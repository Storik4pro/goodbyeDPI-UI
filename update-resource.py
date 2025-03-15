import os
import sys
from pathlib import Path
import subprocess

"""
Here you can generate qmltypes for each module in the project. 
You must regenerate them every time you modifly the qml files.

If you want to create new qml page, first add it to the 
resource.qrc file by example:
    <RCC>
        <qresource prefix="/qt/qml/GoodbyeDPI_UI">
            <file>res/path-to-file</file>
        </qresource>
    </RCC>

### For FluentUI folder ###

You need to create you own qml files for FluentUI folder 
(see FluentUI/resource.qrc) if you want to modify them.
"""

current_dir = os.path.dirname(os.path.abspath(__file__))
venv_dir = Path(sys.prefix)
pyside6_rcc = Path(venv_dir, 'Scripts', 'pyside6-rcc.exe')

subprocess.Popen(
    [pyside6_rcc,'src/resource.qrc', "-o",
     'src/resource_rc.py']
                 )

# subprocess.Popen(
#       [pyside6_rcc,'FluentUI/resource.qrc', "-o",
#       'FluentUI/resource_rc.py']
#                  )
