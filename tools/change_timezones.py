import os
import exifread
from datetime import datetime
from datetime import date
import sys
import re


with open('/dev/stdout', 'w') as line:
    # TODO: bad workaround, refactor to sys.stdout.write() without "with open"
    for file in sys.stdin:
        file = file.strip("\n") #because find has delimiter newline
        with open(file, 'rb') as picture:
            tags = exifread.process_file(picture, stop_tag="Image DateTime")
            time_pic_taken = str(tags['Image DateTime'])

            #make datetime object from specific time format
            datetime_object = datetime.strptime(time_pic_taken, "%Y:%m:%d %H:%M:%S")

            date_object= datetime_object.date()


#write a file with each picture path and the time difference we need to change.
            # Because of different time zones: Dubai 3 hours, Thailand 6 hours
            if date(2018,3,15) == date_object:

               # Only those with "00" in between are from Dubai,
               # and therefore 3 hours td
                file_num = int(re.sub("[^0-9]", "", file))
                print(file_num)

                if file_num >= 61 and file_num < 85:
                    line.write(f"3 {file}\n")

                else:
                    line.write(f"6 {file}\n ")



            if date(2018,3,16) <= date_object < date(2018,4,3):
                line.write(f"6 {file}\n")

            if date_object == date(2018,4,3):
                line.write(f"3 {file}\n")



