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
import time, datetime, urllib
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django import newforms as forms
from mealtracker.ik.models import MapScan, IslandSample, PlayerSample, AllianceSample, Island, Player, Alliance
from django.utils import simplejson

##########
# Utilities

def sortedHistory(history):    
        #Sort by sample scan time, descending
        history = [h for h in history]              #We need a list, not a query set.
        history.sort(key=lambda x: x.scan_time())   #We have to call sort seperately, because it sorts in place and just returns 'None'.
        history.reverse()
        
        return history

###########
# Islands



def island(request, ocean_s, group_s, isle_num_s):

    ocean       = long(ocean_s)
    group       = long(group_s)
    isle_num    = long(isle_num_s)

    island = Island.objects.get(ocean=ocean, group=group, isle_num=isle_num)

    #The last 20 days
    end_time = MapScan.objects.latest().end_time-datetime.timedelta(days=20)
    history = IslandSample.objects.filter(island__ocean=ocean, island__group=group, island__isle_num=isle_num, map_scan__end_time__gt=end_time)

    history = sortedHistory(history)

    return render_to_response("ik/info/island.html", {'island':island, 'history':history});
    
def island_scores(request, ocean_s, group_s, isle_num_s):
    ocean       = long(ocean_s)
    group       = long(group_s)
    isle_num    = long(isle_num_s)
    
    scan = MapScan.objects.latest()

    #The last 20 days
    end_time = scan.end_time-datetime.timedelta(days=20)
    history = IslandSample.objects.filter(island__ocean=ocean, island__group=group, island__isle_num=isle_num, map_scan__end_time__gt=end_time)

    isles = sortedHistory(history)
    
    # Score, and seconds since epoch
    result = [ {'score':isle.score, 'time':time.mktime(isle.map_scan.end_time.timetuple()) } for isle in isles]
    
    return HttpResponse( simplejson.dumps(result))

#############
# Players

def player(request, name):

    player = Player.objects.get(name=name)
    
    islands = player.island_set.order_by('score')
    
    return render_to_response("ik/info/player.html", {'player': player, 'islands': islands})
    
def player_scores(request, name):
    
    scan = MapScan.objects.latest()

    #The last 20 days
    end_time = scan.end_time-datetime.timedelta(days=20)
    history = PlayerSample.objects.filter(player__name=name, map_scan__end_time__gt=end_time)

    history = sortedHistory(history)
    
    # Score, and seconds since epoch
    result = [ {'island_count':sample.island_count, 'score':sample.score, 'time':time.mktime(sample.map_scan.end_time.timetuple()) } for sample in history]

    return HttpResponse( simplejson.dumps(result))
    
#############
# Alliances

def alliance(request, tag_quoted):
    tag = urllib.unquote_plus(tag_quoted)
    
    alliance = Alliance.objects.get(tag=tag)
    
    members = Player.objects.filter(alliance__tag=tag).order_by('-score')
    
    num_islands = Island.objects.filter(player__alliance__tag=tag).count()
    
    return render_to_response("ik/info/alliance.html", {'alliance': alliance, 'members':members, 'num_islands':num_islands})
    
def alliance_scores(request, tag_quoted):
    tag = urllib.unquote_plus(tag_quoted)
    
    scan = MapScan.objects.latest()
    end_time = scan.end_time-datetime.timedelta(days=20)
    
    history = AllianceSample.objects.filter(alliance__tag=tag, map_scan__end_time__gt=end_time)
    
    history = sortedHistory(history)
    
    result = [{'score':sample.score, 'time':time.mktime(sample.map_scan.end_time.timetuple()) } for sample in history]
    
    return HttpResponse( simplejson.dumps(result))