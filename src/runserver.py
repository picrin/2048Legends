#!/usr/bin/env python
import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WC2048.settings")
from website import queries
queries.create_user_simple("annaja", "1")
