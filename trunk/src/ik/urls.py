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

urlpatterns = patterns('',
    (r'^$', 'mealtracker.ik.views.index'),
    (r'^distance', 'mealtracker.ik.views.distance'),
    (r'^news', 'mealtracker.ik.views.news'),
    (r'^feedback/$', 'mealtracker.ik.views.feedback'),
    (r'^feedback/feedback_thanks.html', 'mealtracker.ik.views.feedback_thanks'),
    (r'^wms', 'mealtracker.ik.views.wms'),
    (r'^ajax/island_locations', 'mealtracker.ik.ajax.views.island_locations'),
    (r'^ajax/island_info', 'mealtracker.ik.ajax.views.island_info'),
    (r'^ajax/alliance_info_list', 'mealtracker.ik.ajax.views.alliance_info_list'),
    (r'^spy_reports/', include('mealtracker.ik.spy_reports.urls')),
    (r'^info/', include('mealtracker.ik.info.urls')),
    (r'^about/', 'django.views.generic.simple.direct_to_template', {'template':'ik/about.html'}),
    
)