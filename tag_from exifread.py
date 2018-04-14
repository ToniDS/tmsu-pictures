import exifread
from datetime import datetime
import sys

for filename in sys.stdin:
    file = filename.strip("\n")  # because find has delimiter newline
    with open(file, 'rb') as picture:
        tags = exifread.process_file(picture, stop_tag="Image DateTime")
        try: 
            time_pic_taken = tags['Image DateTime']

             # convert_to_datetime to get year, month and day
            time_pic_taken = str(time_pic_taken)

            datetime_object = datetime.strptime(time_pic_taken, "%Y:%m:%d %H:%M:%S")

            year = 'y'+str(datetime_object.year)
            month = 'm'+str(datetime_object.strftime('%m'))
            year_month=datetime_object.strftime('%Y-%m')
            day='d'+str(datetime_object.strftime('%d'))
            date=datetime_object.strftime('%Y-%m-%d')
            sys.stdout.write(f"{file}:{str(year)}:{month}:{date}:{str(day)}:{str(year_month)}\n")
        except KeyError: 
            print(file)
