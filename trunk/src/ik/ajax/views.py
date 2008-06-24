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
import datetime
from django.http import HttpResponse
from django.utils import simplejson
from mealtracker.ik.models import MapScan

def island_locations(request):

    #Specify the islands of interest
    if request.GET.has_key('player'):
        
        player = request.GET['player']
        isles = MapScan.objects.latest().islandsample_set.filter(ruler=player)
    
    elif request.GET.has_key('alliance'):
        
        alliance = request.GET['alliance']
        isles = MapScan.objects.latest().islandsample_set.filter(alliance_tag=alliance)
        
    #Return a list of x,y coordinates
    result = [ [isle.x,isle.y,isle.score] for isle in isles]
    
    return HttpResponse(simplejson.dumps(result))
    
def island_info(request):
    x = request.GET['x']
    y = request.GET['y']
    
    isle = MapScan.objects.latest().islandsample_set.filter(x=x,y=y).get();
    
    result = {'name':isle.name, 'position':isle.position, 'ruler':isle.ruler,'alliance_tag':isle.alliance_tag, 'score':isle.score};
    
    return HttpResponse(simplejson.dumps(result))

class AllianceInfo:
    def __info__(self):
        self.prev_score = 200
        self.score = 100
        self.tag = '[ada]'
        self.rank = 1
    
def alliance_info_list(request):
    new_scan = MapScan.objects.latest()

    end_time = new_scan.end_time-datetime.timedelta(hours=23)

    prev_scan = MapScan.objects.filter(end_time__lt=end_time).latest()
    
    #############
    # Top 10 Alliances
    alliances = new_scan.alliancesample_set.order_by('-score').values('score','tag')[:10]
    tags = [alliance['tag'] for alliance in alliances]
    
    #Add the 'rank' of the alliance, and an initial previous score of 0
    result = [ {'rank': idx+1,'tag': alliance['tag'], 'score': alliance['score'], 'prev_score':0} for idx,alliance in enumerate(alliances)]
    
    #Now get the previous day's scores and annotate the alliance sample object
    prev_alliances = prev_scan.alliancesample_set.filter(tag__in=tags).values('score','tag')
  
    #This is 0(n^2) with the number of alliances. It sucks.
    for info in result:
        for alliance in prev_alliances:
            if info['tag'] == alliance['tag']:
                info['prev_score'] = alliance['score']
    
    return HttpResponse( simplejson.dumps( result ) )


    