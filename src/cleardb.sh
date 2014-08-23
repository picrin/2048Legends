#!/bin/bash
python manage.py sqlclear website | python manage.py dbshell
python manage.py syncdb
