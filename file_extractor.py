import pandas as pd
from pyunpack import Archive
import shutil
import glob
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def unpack_zip(path):
    '''
    Recursive function to unzip every zip while creating new folders
    for each archive.
    :param path: Path to father folder
    :return: nothing
    '''
    zip_files = [f for f in glob.glob(path + "**/*.zip", recursive=True)]
    if not zip_files:
        return
    for f in zip_files:
        folder_name = f.split("\\")[-1].split(".")[0]
        Archive(f).extractall(path + '\\' + folder_name, auto_create_dir=True)
    new_path = path + '\\' + folder_name
    more_zip_files = [f for f in glob.glob(new_path + "**/*.zip", recursive=True)]

    unpack_zip(new_path) if more_zip_files else 1


def move_files(path, destination_folder, file_type = '*', keep_duplicates = True, extract_zip=True):
    '''
    :param path:  Path to father folder
    :param destination_folder: Where you want the files to be moved to
    :param extract_zip: Default = True if want to unzip files within father folder.
    :return: Nothing
    '''
    unpack_zip(path) if extract_zip == True else 1
    files = [f for f in glob.glob(path + "\**/*."+file_type, recursive=True)]
    df = create_df(files)
    if keep_duplicates:
        df_dup = find_duplicates(df)
        dup_index = get_index_of_duplicate(df_dup,files)
        files = rename_dup(df_dup,files,dup_index)
    else:
        files = set(files)
    print(files)
    for f in files:
        extension = f.split('.')[-1]
        file_path = destination_folder + '\\' + extension + '/' #name of the new folder
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if os.path.isfile(f):
            shutil.copy(f, file_path)


def rename_dup(df_dup,files,dup_index):
    '''
    function that renames the duplicated files
    :param df_dup: df of duplicates
    :param files: list of files
    :param dup_index: index of the duplicated files
    :return:
    '''
    for x in range(len(dup_index)):
        index = dup_index[0][x]
        if not os.path.exists(df_dup['rename'].loc[index]):
            os.rename(files[index], df_dup['rename'].loc[index])
            files[index] = df_dup['rename'].loc[index]

    return files


def get_index_of_duplicate(df_dup,files):
    '''
    function that retrieve the index of the files that needs to be renamed
    :param df_dup: df of duplicates
    :param files: list of files
    :return:
    '''
    return [df_dup.index for x in df_dup['path'] if x in files]


def create_df(files):
    '''
    creates a df from the loaded files
    :param files: list of files
    :return:
    '''
    path = files
    names = [x.split("\\")[-1] for x in path]
    d = {'path':path,'name':names}
    df = pd.DataFrame(d)
    return df


def find_duplicates(df):
    '''
    Function that finds duplicates files
    :param df: DF with the path and names
    :return:
    '''
    df1 = df[df.duplicated(subset=['name'])]
    df1['rename'] = df1['path'].apply(lambda x: change_name(x))
    return df1


def change_name(x):
    '''
    Function that renames the file name
    :param x: a file
    :return:
    '''
    splited = x.split("\\")
    # if len(splited) >= 3:
    #     splited[-1] = splited[-3] + "_" + splited[-2] + "_" + splited[-1]
    # elif len(splited) >= 2:
    #     splited[-1] = splited[-2] + "_" + splited[-1]
    # else:
    splited[-1] = 'copy_of_' + splited[-1]
    return "\\".join(splited)


def is_folder_empty(dest):
    '''
    Function that checks if the destination folder is empty or not.
    :param dest: Destination folder
    :return:
    '''
    if os.path.exists(dest):
        if not os.listdir(dest):
            print("Folder is not empty, will rewrite the files!")
    else:
        pass


if __name__ == '__main__':
    now = str(datetime.today()).split(" ")[0]
    path = r"path\to\origin\folder"
    destination_folder = r"path\to\destination\folder"+now
    is_folder_empty(destination_folder)
    move_files(path, destination_folder, file_type='*', keep_duplicates = False)
