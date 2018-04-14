#/bin/sh

find "/data/nextcloud/Photos Thailand" -name "DSCF*.JPG" | python change_timezones.py | 
      while read A B; do exiftool -overwrite_original -AllDates+=$A "$B"; done	

