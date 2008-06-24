#!/bin/sh
date=$(/bin/date -Iminutes)

/usr/local/bin/python2.4 ~/webapps/django/mealtracker/ik/scripts/do_scan.py -p ~/ik_data/raw_maps-$date username password
/usr/local/bin/python2.4 ~/webapps/django/mealtracker/ik/scripts/import_scan.py ~/ik_data/raw_maps-$date
/usr/local/bin/python2.4 ~/webapps/django/mealtracker/ik/scripts/do_analysis.py
