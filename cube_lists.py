"""functions to manipulate cube lists"""
import os

def combine_lists(cube_lists):
    """get a list of all cards used in any of the cubes"""
    card_names = set()
    for cube_list in cube_lists:
        card_names.update(cube_list)
    return card_names

def open_lists(cube_list_dir):
    """read in all of the cubes in a directory"""
    cube_lists = list()
    for file_name in os.listdir(cube_list_dir):
        file_path = os.path.join(cube_list_dir, file_name)
        with open(file_path) as cube_file:
            cube_lists.append(cube_file.readlines())
    return cube_lists

def run_script():
    """Do the default thing for the script"""
    list_dir = 'cube_lists'
    cube_lists = open_lists(list_dir)
    card_names = combine_lists(cube_lists)
    with open('cube_combined.txt', 'w') as cube_file:
        cube_file.write(''.join(card_names))

if __name__ == '__main__':
    run_script()
