# tmsu-pictures

Using tmsu to tag my pictures up

This repository helps me tag my pictures up. 
change_date.sh and change_timezones.py are helpers to change the time of the exif data, because I forgot to change my camera's time settings.

tag_from exifread.py and tag_from_exif.sh create the date tags from exif tags.

pytmsu is a CLI for tagging my pictures up. It automatically detects the tmsu database, reads all the existing tags, and allows me to tag my pictures, automatically bringing the next file.

You can invoke pytmsu with the top-level folder where all the pictures are. By default, it will show you all the pictures. You can filter using --tag and --exclude. 

Attribution to bison--,who helped me significantly with this code!
