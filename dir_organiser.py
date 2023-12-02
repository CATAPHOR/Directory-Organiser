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
def move_files(filetype_dict, path, category_folders, ignore_dirs):
    file_count = 0
    dir_count = 0
    errors = []
    
    for child_path in path.iterdir():
        # file moving
        if child_path.is_file():
            # determine directory to move to
            try:
                new_child_path = path / filetype_dict[child_path.suffix[1:]]
            except KeyError:
                new_child_path = path / "other"
            # attempt move operation
            try:
                shutil.move(child_path, new_child_path)
                file_count += 1
                print(f"FILE:\t'{child_path.name}' -> {new_child_path.name}")
            except shutil.Error:
                errors.append(child_path)
            
        # folder moving
        elif child_path.is_dir() and not ignore_dirs:
            dir_move_output = move_folder(filetype_dict, child_path, category_folders)
            # update counts if not category folder
            if dir_move_output[0]:
                dir_count += dir_move_output[1]
                if not dir_move_output[1]:
                    errors.append(child_path)
            
    return file_count, dir_count, errors

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
        try:
            shutil.move(path, new_path)
            print(f"FOLDER:\t'{path.name}' -> .\\{new_path.name}")
            # bools: [not a category folder]: true; [operation successful]: true
            return True, True
        except shutil.Error:
            # bools: see above
            return True, False
    
    # first bool false as folder was category dir
    return False, True

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
        
        # get user confirmation on whether to move folders within directory
        print()
        while True:
            try:
                ignore_dirs = not choice[input("Should the program move folders in "
                                               "this directory? Y/N: ").lower()]
            except KeyError:
                continue
            break
        
        # move files to appropriate categories
        print("\nMoving files:")
        file_count, dir_count, errors = move_files(type_dict, folder, category_folders, ignore_dirs)
        
        print("\nFolder has been reorganised categorically by file-type.")
        print(f"{file_count} file{'s' * (file_count != 1)} moved; "
              f"{dir_count} folder{'s' * (dir_count != 1)} moved.")
        if len(errors) > 0:
            print(f"\n{len(errors)} files and/or folders could not be moved:")
            for path in errors:
                print(f"\t{path.name}")
        
        input("\nPress [Enter] to exit.")