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
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django import newforms as forms
from mealtracker.ik.models import MapScan
import scripts.utils as utils

################################################################
# Site Index

def index(request):
    return render_to_response('ik/index.html', {})

################################################################
# Expansion Planner

class DistanceForm(forms.Form):
    ocean               = forms.IntegerField(min_value=1, max_value=100, widget=forms.TextInput(attrs={'maxlength':3, 'size':3} ))
    group               = forms.IntegerField(min_value=1, max_value=100, widget=forms.TextInput(attrs={'maxlength':3, 'size':3} ))
    isle_num            = forms.IntegerField(min_value=1, max_value=25, widget=forms.TextInput(attrs={'maxlength':2, 'size':3} ))
    rulerless           = forms.BooleanField(required=False, label="Rulerless", initial=True)
    low_score           = forms.BooleanField(required=False, label='...with a score less than')
    threshold           = forms.IntegerField(required=False, min_value=0, initial=2500 )
    weak_alliance       = forms.BooleanField(required=False, label='...in an alliance with a score less than')
    alliance_threshold  = forms.IntegerField(required=False, min_value=0, initial=2500)
    low_island_count    = forms.BooleanField(required=False, label='...with an island count less than')
    max_num_islands     = forms.IntegerField(required=False, min_value=0, initial=6)

def GetIslandList(params):
    scan = MapScan.objects.latest()
    results = []
    
    if params['rulerless']:
        results += scan.islandsample_set.filter(ruler='')    
    
    if params['weak_alliance'] or params['low_score'] or params['low_island_count']:

        #Build the base query        
        rulers = scan.playersample_set.filter( island_count__gte=2)

        if params['weak_alliance']:
            ### Get a list of all 'weak' alliances
            #Get the alliance threshold, default of 10,000,000
            alliance_threshold = params['alliance_threshold']
            if not alliance_threshold: alliance_threshold = 10000000

            weak_tags = [a.tag for a in scan.alliancesample_set.filter(score__lt=alliance_threshold)]
            weak_tags.append('') #Don't forget the unaligned

            #Add the alliance constraint to the query
            rulers = rulers.filter(alliance_tag__in=weak_tags)

        if params['low_score']:
            ### Get a list of all 'weak' players 
            #Get threshold, and default it to 1000000
            threshold = params['threshold']
            if not threshold: threshold = 10000000

            #Add the player score constraint
            rulers = rulers.filter(score__lt=threshold)

        if params['low_island_count']:
            #Get the maximum number of islands, default 1000
            max_num_islands = params['max_num_islands']
            if not max_num_islands: max_num_islands = 1000

            #Add a maximum island count constraint
            rulers = rulers.filter(island_count__lt=max_num_islands)

        rulers = [ruler.name for ruler in rulers]

        ### Finally, return the list islands owned by the 'weak' players
        
        results += scan.islandsample_set.filter(ruler__in=rulers)
    
    return results
    
def distance(request):
    ##If there are any items in the query string, then try to perform validation and the search,
    ##but if not, then this is the inital page request, and initial values should be displayed
    results = None
    if len(request.GET):
        
        form = DistanceForm(request.GET)
        
        if form.is_valid():
            params = form.clean()
            isles = GetIslandList(params)
            
            #Decoarate the islands with distance
            p = utils.IslandPosition('%d:%d:%d'% (params['ocean'],params['group'],params['isle_num']))

            for isle in isles: isle.distance = p.distance_to(isle)
            for isle in isles: isle.lws_time = isle.distance/5;
            for isle in isles: isle.colo_time = isle.distance/2;
            
            isles.sort(key=lambda x:x.distance)

            results = isles
    else:
        form = DistanceForm()
    return render_to_response('ik/distance.html', {'form':form, 'results':results})

#################################################################################################
# Inselkampf News

def cmpAlliance(left, right):
    
    if left.new_player.alliance is None and right.new_player.alliance is None:
        return 0
    
    if left.new_player.alliance is None:
        return 1
        
    if right.new_player.alliance is None:
        return -1
    
    return cmp(left.new_player.alliance.tag, right.new_player.alliance.tag)

def news(request):
    """This really shouldn't get re-run every time someone requests the page, do it once, store it, then
    have the news page present a feed of info, every time it updates, for the last week or so."""
    
    new_scan = MapScan.objects.latest()
    
    end_time = new_scan.end_time-datetime.timedelta(hours=23)

    prev_scan = MapScan.objects.filter(end_time__lt=end_time).latest()

    ## Find all scans in the time period of interest
    latest_scans = MapScan.objects.filter(end_time__gte=end_time).order_by('-end_time')

    latest_scans = [{'scan':scan, 
                     'captures': list(scan.islandcapture_set.all())} 
                     for scan in latest_scans]
    for item in latest_scans:
        item['captures'].sort(cmpAlliance)

    ## Find all islands which were not in the previous scan

    #The position of all islands in the previous scan, as a list
    prev_pos_list = [ item['position'] for item in prev_scan.islandsample_set.values('position')]

    new_isles = new_scan.islandsample_set.exclude(position__in=prev_pos_list)


    ## Find all of the islands which lost a ruler, but had one in the previous scan
    #The position of all islands in the previous scan which had rulers, as a list
    prev_ruled_list = [ item['position'] for item in prev_scan.islandsample_set.exclude(ruler='').values('position')]
    
    #Of the positions found above, which now have no ruler.
    newly_rulerless = new_scan.islandsample_set.filter(ruler='', position__in=prev_ruled_list)

    return render_to_response('ik/news.html', {'latest_scans':latest_scans, 'scan':new_scan, 'new_isles':new_isles, 'newly_rulerless':newly_rulerless})

#################################################################################################
# Ocean Map
import StringIO
from PIL import Image
from django.views.decorators.cache import cache_control

@cache_control(public=True, max_age=3600)
def wms(request):
    """The 'base' island map should be cached, and then annotated"""
    
    ## Find all islands which were not in the previous scan
    new_scan = MapScan.objects.latest()

    bbox = request['BBOX'].split(',')
    minx,bbminy,maxx,bbmaxy = [int(float(item)) for item in bbox]
    
    #Openlayers has (0,0) at the lower left corner, but the island coord system
    #places the origin at the upper left.
    miny=500-bbmaxy
    maxy=500-bbminy
    
    height = int(request['HEIGHT'])
    width = int(request['WIDTH'])

    im = Image.new('RGB',(maxx-minx,maxy-miny))
    pix = im.load()
    
    #All islands
    for pos in new_scan.islandsample_set.filter(x__gte=minx, x__lt=maxx, y__gte=miny, y__lt=maxy).values('x','y'):
        pix[int(pos['x'])-minx,int(pos['y'])-miny] = (100,100,100)

    im = im.resize((width,height))

    buf = StringIO.StringIO()
    im.save(buf,'jpeg')
    buf.seek(0)
    
    response = HttpResponse(buf.readlines(),mimetype="image/jpeg")
    return response
    
##################################################################################################
# Feedback
from mealtracker.ik.scripts import messaging

class FeedbackForm(forms.Form):
    message = forms.CharField(max_length=500, widget=forms.Textarea())
    email = forms.EmailField(required=False, max_length=100, label='Your email (optional)')

def feedback(request):
    if len(request.POST):
        form = FeedbackForm(request.POST)
        
        if form.is_valid():
            params = form.clean()
            messaging.send_feedback(params['message'], params['email'])
            return HttpResponseRedirect('feedback_thanks.html')
    else:
        form = FeedbackForm()
    
    return render_to_response('ik/feedback.html', {'form':form})

def feedback_thanks(request):
    return render_to_response('ik/feedback_thanks.html')