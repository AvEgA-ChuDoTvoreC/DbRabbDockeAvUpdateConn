import os


imports = """
--=--IMPORT MODULES--=--

=Invalid Names:=


Actually, you can import a module with an invalid name. 
But you'll need to use imp for that, e.g. assuming file is named models.admin.py, you could do

import imp
with open('models.admin.py', 'rb') as fp:
    models_admin = imp.load_module(
        'models_admin', fp, 'models.admin.py',
        ('.py', 'rb', imp.PY_SOURCE)
    )
    
read: https://docs.python.org/3/library/imp.html#imp.find_module


If you really want to, you can import a module with an unusual 
filename (e.g., a filename containing a '.' before the '.py') using the imp module:

>>> import imp
>>> a_b = imp.load_source('a.b', 'a.b.py')
>>> a_b.x
"I was defined in a.b.py!"

However, that's generally a bad idea. It's more likely that you're trying to use packages, 
in which case you should create a directory named "a", containing a file named "b.py";
and then "import a.b" will load a/b.py.
"""

classes = """

"""

modules = [imports, classes]
for module in modules:
    print(module)
