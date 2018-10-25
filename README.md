# tmsu-pictures
Using tmsu to tag my pictures up

This repository helps me tag my pictures up. 
change_date.sh and change_timezones.py are helpers to change the time of the exif data, because I forgot to change my camera's time settings.

tag_from exifread.py and tag_from_exif.sh create the date tags from exif tags.

pytmsu is a CLI for tagging my pictures up. It automatically detects the tmsu database, reads all the existing tags, and allows me to tag my pictures, automatically bringing the next file.

If you want to use pytmsu, put it in the top-level directory your pictures are in. 

Attribution to bison--,who helped me significantly with this code!
