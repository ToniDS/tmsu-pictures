#!/bin/sh

IFS=":"


cd "/data/nextcloud/Photos Thailand"
find . -iname "*.JPG" | python "/home/antonia/PycharmProjects/tmsu/tag_from exifread.py" |
	while read A B C D E F; do tmsu tag "$A" $B $C $D $E $F; done
