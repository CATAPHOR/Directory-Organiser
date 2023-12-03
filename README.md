# Directory Organiser
Python script to reorganise files (through moving them into categorical subfolders) in a directory.

## Run Instructions
- Provide a singular argument of the filepath to directory to organise.
- If no argument is given, the program will set the directory to organise to the user's Downloads folder.
- The program will analyse all files and folders within the given directory (recurses through, analyses filetypes within) to restructure the hierarchy by filetype category.

## Categories
The categories are determined by `filetypes.py`, and are intialised in the following subfolders:
```
./documents
./images
./video
./audio
./archives
./software
./data
./code
./web
./utilities
./fonts
./anki
./other
```
