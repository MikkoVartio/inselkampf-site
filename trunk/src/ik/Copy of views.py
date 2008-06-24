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
from django.core.cache import cache
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
    ocean = forms.IntegerField(min_value=1, max_value=100, widget=forms.TextInput(attrs={'maxlength':3, 'size':3} ))
    group = forms.IntegerField(min_value=1, max_value=100, widget=forms.TextInput(attrs={'maxlength':3, 'size':3} ))
    isle_num = forms.IntegerField(min_value=1, max_value=25, widget=forms.TextInput(attrs={'maxlength':2, 'size':3} ))
    rulerless = forms.BooleanField(required=False, label="Rulerless", initial=True)
    weak = forms.BooleanField(required=False, label="Ruled by Weak Players (Really? Pick on the newbs?)")
    threshold = forms.IntegerField(required=False, min_value=0, initial=2500, label='...with a score threshold of')

def GetIslandList(params):
    scan = MapScan.objects.latest()
    results = []
    
    if params['rulerless']:
        results += scan.islandsample_set.filter(ruler='')    
    
    if params['weak']:
        #Get threshold, and default it to 0
        threshold = params['threshold']
        if not threshold: threshold = 0
        
        weak_tags = [a.tag for a in scan.alliancesample_set.filter(score__lt=threshold)]
        weak_tags.append('') #Don't forget the unaligned
        
        rulers = [ruler.name for ruler in scan.playersample_set.filter(score__lt=threshold, alliance_tag__in=weak_tags, island_count__gte=2)]
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
            isles.sort(key=lambda x:x.distance)

            results = isles
    else:
        form = DistanceForm()
    return render_to_response('ik/distance.html', {'form':form, 'results':results})

#################################################################################################
# Inselkampf News

def news(request):
    """This really shouldn't get re-run every time someone requests the page, do it once, store it, then
    have the news page present a feed of info, every time it updates, for the last week or so."""
    
    new_scan = MapScan.objects.latest()
    prev_scan = MapScan.objects.filter(end_time__lt=new_scan.end_time).latest()

    ## Find all islands which were not in the previous scan

    #The position of all islands in the previous scan, as a list
    prev_pos_list = [ item['position'] for item in prev_scan.islandsample_set.values('position')]

    new_isles = new_scan.islandsample_set.exclude(position__in=prev_pos_list)


    ## Find all of the islands which lost a ruler, but had one in the previous scan
    #The position of all islands in the previous scan which had rulers, as a list
    prev_ruled_list = [ item['position'] for item in prev_scan.islandsample_set.exclude(ruler='').values('position')]
    #Of the positions found above, which now have no ruler.
    newly_rulerless = new_scan.islandsample_set.filter(ruler='', position__in=prev_ruled_list)

    ## Find all of the islands which were rulerless, but have now been colonized
    #The position of all islands in the previous scan which did not have rulers
    prev_un_ruled_list = [ item['position'] for item in prev_scan.islandsample_set.filter(ruler='').values('position')]
    #Of the positions found above, which now have rulers
    just_colonized = new_scan.islandsample_set.exclude(ruler='').filter(position__in=prev_un_ruled_list)


    ## Find all islands which disappeared
    pos_list = [ item['position'] for item in new_scan.islandsample_set.values('position')]
    deleted_isles = prev_scan.islandsample_set.exclude(position__in=pos_list)

    ## Find all of the islands which had a ruler, but the ruler changed
    #Of the positions found above, which now have a different ruler.
    #changed_ruler = new_scan.islandsample_set.exclude(ruler='').filter(position__in=prev_ruled_list)
    
    return render_to_response('ik/news.html', {'scan':new_scan, 'new_isles':new_isles, 'newly_rulerless':newly_rulerless, 'just_colonized':just_colonized, 'deleted_isles':deleted_isles})

#################################################################################################
# Ocean Map
import StringIO
from PIL import Image
from mealtracker.ik.scripts import analytics

def wms(request):
    """The 'base' island map should be cached, and then annotated"""
    
    new_scan = MapScan.objects.latest()

    bbox = request['BBOX'].split(',')
    minx,bbminy,maxx,bbmaxy = [int(float(item)) for item in bbox]
    
    #Openlayers has (0,0) at the lower left corner, but the island coord system
    #places the origin at the upper left.
    miny=500-bbmaxy
    maxy=500-bbminy
    
    #Find out how much of the requested image is actually outside the bounding box
    leftgutter = min(0,minx)
    rightgutter = max(0,maxx-500)
    topgutter = min(0,miny)
    botgutter = max(0,maxy-500)
    
    #Calculate the original width of the requested bounds
    dx = maxx - minx
    dy = maxy - miny
    
    #Remove the gutter from the bounds
    minx = max(0,minx)
    maxx = min(500, maxx)
    miny = max(0,miny)
    maxy = min(500, maxy)
    

    #Calculate the reuquested output image size
    height = int(request['HEIGHT'])
    width = int(request['WIDTH'])
    #Cap the size at 2000, so we don't try to make a HUGE image.
    if height > 2000 or width > 2000:
        raise ValueError('The requested image size is too large')

    #im = Image.new('RGB',(maxx-minx,maxy-miny))
    #pix = im.load()
    
    #All islands
    #for isle in new_scan.islandsample_set.filter(x__gte=minx, x__lt=maxx, y__gte=miny, y__lt=maxy):
    #    pix[int(isle.x)-minx,int(isle.y)-miny] = (100,100,100)

    im = getCachedMapImage()
    
    bounds = (minx,miny,maxx,maxy)
    im = im.crop(bounds)
    
    data = (1,0,leftgutter,0,1,topgutter)
    im = im.transform((dx,dy), Image.AFFINE, data)
    im = im.resize((width,height))

    buf = StringIO.StringIO()
    im.save(buf,'jpeg')
    buf.seek(0)
    
    response = HttpResponse(buf.readlines(),mimetype="image/jpeg")
    return response