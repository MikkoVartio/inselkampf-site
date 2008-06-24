#    ik-site: A website for information about inselkampf world 1
#    Copyright (C) 2008  Noah C. Jacobson
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^tracker/', include('mealtracker.tracker.urls')),
    (r'^ik/', include('mealtracker.ik.urls')),
    (r'^admin/', include('django.contrib.admin.urls'))
)

# Serve up static files (css), but only when debug is true.
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/tracker/media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'c:/djangoprojects/mealtracker/static/tracker/media'}),
        (r'^static/ik/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'c:/djangoprojects/mealtracker/static/ik'}),
        )