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
    (r'^island/(?P<ocean_s>\d+)/(?P<group_s>\d+)/(?P<isle_num_s>\d+)/$', 'mealtracker.ik.info.views.island'),
    (r'^island/(?P<ocean_s>\d+)/(?P<group_s>\d+)/(?P<isle_num_s>\d+)/island_scores/$', 'mealtracker.ik.info.views.island_scores'),

    (r'^player/(?P<name>\S+)/scores/$', 'mealtracker.ik.info.views.player_scores'),
    (r'^player/(?P<name>\S+)/$', 'mealtracker.ik.info.views.player'),

    (r'^alliance/(?P<tag_quoted>\S+)/scores/$', 'mealtracker.ik.info.views.alliance_scores'),
    (r'^alliance/(?P<tag_quoted>\S+)/$', 'mealtracker.ik.info.views.alliance'),

)