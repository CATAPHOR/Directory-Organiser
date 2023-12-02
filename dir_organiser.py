import pathlib
import sys
import shutil
from collections import Counter
from _ctypes import ArgumentError
from filetypes import type_dict

choice = {"y": True, "n": False}

# get correct directory for program to organise
def get_directory(path_str):
    # initialise path to user's Downloads folder if no argument supplied
    if not path_str:
        path = pathlib.Path("~/Downloads").expanduser()
    else:
        path = pathlib.Path(*path_str).resolve()
    
    if not path.exists():
        raise FileNotFoundError("Directory not found.")
    else:
        return path

# make the folders to organise the files into within the directory
def make_dirs(path, names):
    for name in names:
        (path / name).mkdir(exist_ok = True)

# move all files within directory to correct categories
def move_files(filetype_dict, path, category_folders):
    for child_path in path.iterdir():
        if child_path.is_file():
            try:
                new_child_path = path / filetype_dict[child_path.suffix[1:]]
            except KeyError:
                new_child_path = path / "other"
            shutil.move(child_path, new_child_path)
        elif child_path.is_dir():
            move_folder(filetype_dict, child_path, category_folders)

# determine categories to place folders into; detects frequency of filetypes within
def move_folder(filetype_dict, path, category_folders):
    if path.name not in category_folders:
        counter = Counter()
        count_filetypes(counter, path, filetype_dict)
        
        # default to other, but try to place in category by filetype frequency
        new_path = path.parent / "other"
        if counter:
            category = counter.most_common(1)[0]
            # see if second frequency is significant enough to affect folder's category
            if category[0] == "other":
                try:
                    category_2 = counter.most_common(2)[1]
                    if float(category_2[1]) / float(category[1]) > 0.6:
                        category = category_2
                except IndexError:
                    pass
            # set path as per detected category
            new_path = path.parent / category[0]
        
        # move folder
        shutil.move(path, new_path)

# recursively counts number of files of each category in directory and sub-directories
def count_filetypes(counter, path, filetype_dict):
    for child_path in path.iterdir():
        if child_path.is_dir():
            count_filetypes(counter, child_path, filetype_dict)
        elif child_path.is_file():
            try:
                category = filetype_dict[child_path.suffix[1:]]
            except KeyError:
                category = "other"
            counter[category] += 1

if __name__ == "__main__":
    # get arguments (if any), determine directory to operate on
    if len(sys.argv) > 2:
        raise ArgumentError("Supply one argument (folder path) or none.")
    folder = get_directory(sys.argv[1:])
    print(f"Will reorganise folder: {folder}.")
    
    # get user confirmation on procedure
    while True:
        try:
            proceed = choice[input("Proceed? Y/N: ").lower()]
        except KeyError:
            continue
        break
    
    if proceed:
        # get category names from dictionary
        category_folders = list(set(type_dict.values()))
        # make category subfolders
        make_dirs(folder, category_folders)
        # move files to appropriate categories
        move_files(type_dict, folder, category_folders)
        
        print("Folder has been reorganised categorically by file-type.")