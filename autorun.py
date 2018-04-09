import os

os.system("sudo apt-get install python-pip")
try:
    import numpy  
    print('\nnumpy was installed')
except ImportError:
    print('\nThere was no such module installed')

    print("Installing numpy..")
    os.system("sudo pip install numpy")
    
try:
    import nltk  
    print('\nnltk was installed')
except ImportError:
    print('\nThere was no such module installed')

    print("Installing nltk..")
    os.system("sudo pip install nltk")
    import nltk
    nltk.download('stopwords')
    
try:
    import matplotlib  
    print('\nmatplotlib was installed')
except ImportError:
    print('\nThere was no such module installed')

    print("Installing matplotlib..")
    os.system("sudo pip install matplotlib")
    
try:
    import textblob  
    print('\ntextblob was installed')
except ImportError:
    print('\nThere was no such module installed')

    print("Installing textblob..")
    os.system("sudo pip install textblob")
    
try:
    import flask  
    print('\nflask was installed')
except ImportError:
    print('\nThere was no such module installed')

    print("Installing flask..")
    os.system("sudo pip install flask")
os.system("python -m webbrowser -t \"http://127.0.0.1:5000\"")
os.system("python project.py example.json")


