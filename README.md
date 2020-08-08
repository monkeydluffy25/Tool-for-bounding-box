# Tool-for-bounding-box
Run "pip install -r requirement.txt"

then execute the like below:

"python3 interactive.py --path /path/to/folder/containing/images/"

after "--path" enter the folder path for images in your system

NOTE: make sure the above path ends with "/" with correct folder path

In interactive mode following keyboard keys are to be used:

1) 'q' to quit the following image after marking the bounding box
2) 'r' to reload the same image for re-editing if something goes wrong
3) 'e' to edit mode on for drawing bounding box around table
4) 'c' to close without saving and to stop the further processing of files in the folder

Note: also u cant see the bounding box until u complete ur box like hold the left mouse button,drag around the table and then release the left mouse button to see the box.

# GUI code ReadME


Run "pip install -r requirement.txt" - this step is once for setting up the required modules "running it everytime is not necessary"

Run "sudo apt-get install python-tk python3-tk python-imaging-tk"

Run "python3 GUI.py"
