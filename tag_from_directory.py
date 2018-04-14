from pathlib import Path
import os
import subprocess
import exifread
from datetime import datetime



##for file in folder
# Open image file for reading (binary mode)
test= "~/Bilder"

for dirname, dirnames, filenames in os.walk(test):
    for filename in filenames:
        if filename.endswith(".jpg"):
            get_year_and_month_from_file(filename)



def get_year_and_month_from_file(filename):
    with open(filename, 'rb') as picture:
        tags = exifread.process_file(picture, stop_tag="Image DateTime")
        time_pic_taken = tags['Image DateTime']


    #convert_to_datetime to get year and month
    time_pic_taken = str(time_pic_taken)

    datetime_object=datetime.strptime(time_pic_taken, "%Y:%m:%d %H:%M:%S")


    year = datetime_object.year
    month= datetime_object.strftime('%B')
    subprocess.call(["tmsu", "tag", "-v", filename, str(year), month])
    return year, month


#get recursive directories until the next highest is Fotos
#ormal structure for all but 'Bilder Zeigen', 'DCIM', Data_Station, Kinderbilder, Pictures, prä-2008

#I am currently in fotos,
fotos = "/mnt/share/Fotos"
os.chdir(fotos)

def get_element_and_directory_lists(current):
    element_list=[]
    directory_list=[]
    for (dirpath, dirnames, filenames) in os.walk(current):
        element_list.extend(filenames)
        directory_list.extend(dirnames)
    return element_list, directory_list

#3 Listen:

def partition_lists(current, directory_list):
    sorted_pictures = [directory for directory in directory_list if directory.startswith('2')]
    recursive_list= []
    for directory in sorted_pictures:
        subdirectory_list = get_element_and_directory_lists(os.path.join(current, directory))[1]
        if len(subdirectory_list) != 0:
            recursive_list.append(directory)
    print(recursive_list)
    non_recursive_list = [dir for dir in sorted_pictures if dir not in recursive_list]

    print(non_recursive_list)
    return recursive_list, non_recursive_list

element_list, directory_list = get_element_and_directory_lists(fotos)
recursive_list, non_recursive_list = partition_lists(fotos, directory_list)

def test_folder_length(directory):
    tags = directory.split(' ')
    if len(tags) > 2:
        tag = ' '.join(tags[1:2])
    else:
        tag = str(tags[1])
    return tag



    def first(directory):
        tag=test_folder_length(directory)
        element_list = []
        for (dirpath, dirnames, filenames) in os.walk(os.path.join(fotos, directory)):
            element_list.extend(filenames)
        files = ' '.join(element_list)
    #print(files)
    #os.chdir(os.path.join(fotos, directory))
    #subprocess.call(["tmsu", "tag", f"--tags={tag}", files])

        for file in element_list:
            picturepath = os.path.join(fotos, directory, file)
            subprocess.call(["tmsu", "tag", "-v", picturepath, tag])

####TODO: For recursive:
#give all directories within a recursive tag, then go one deeper, and do the same as above
#non_recursive list is wrong

#for directory in non_recursive_list:
 #   first(directory)


for directory in recursive_list:
    tag = test_folder_length(directory)
    #erste Ebene
    element_list, directory_list = get_element_and_directory_lists(os.path.join(fotos, directory))
    for subdirectory in directory_list:
        subprocess.call(["tmsu", "tag", "-v", "--recursive", os.path.join(fotos, directory, subdirectory), tag])
    for file in element_list:
        picturepath = os.path.join(fotos, directory, file)
        subprocess.call(["tmsu", "tag", "-v", picturepath, tag])
    #zweite Ebene
    for subdirectory in directory_list:
        path = os.path.join(fotos, directory, subdirectory)
        if subdirectory[0].isalpha():
            tag = test_folder_length(subdirectory)
            tags = subdirectory.split(' ')
            element_list, directory_list = get_element_and_directory_lists(path)
            for file in element_list:
                picturepath = os.path.join(path, file)
                subprocess.call(["tmsu", "tag", "-v", picturepath, tag])










#need list of all elements in folder








#subprocess.call(["tmsu", "tag", f"--tags={tag}", files])









