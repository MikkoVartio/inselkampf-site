#!/usr/local/bin/python2.4
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
from mealtracker.ik.models import MapScan,IslandSample
import scan
import utils
import getopt,sys
import os

def usage():
    head,tail = os.path.split(sys.argv[0])
    print "Usage:\n%s <dir_path>\n\nThis script takes a single argument, which should be a path to a directory containing raw map information." % tail

def configure():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"")
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    if len(args) != 1:
        usage()
        sys.exit(3)
    
    dir_path = args[0]
        
    if not os.path.isdir(dir_path):
        print dir_path + ' is not a directory, and it should be.'
        sys.exit(4)

    return dir_path

def CalculateAlliances( isles ):
    """Returns a dictionary with alliance name as the key
       and score as the value."""
    
    alliances = {}
    for isle in isles:
        tag = isle.alliance_tag
        
        if not alliances.has_key(tag):
            alliances[tag] = 0
        
        alliances[tag] += isle.score
    
    #Unaligned players technically aren't in an alliance

    if alliances.has_key(''):
        del alliances['']

    return alliances
        
def CalculateRulers( isles ):
    """Returns a dictionary with ruler as the key, and score
       as the value."""
    
    rulers = {}
    for isle in isles:
        ruler = isle.ruler
        
        #No ruler doesn't count as a ruler
        if ruler is '':
            continue
        
        if not rulers.has_key(ruler):
            rulers[ruler] = (isle.alliance_tag,0,0) #alliance_tag, num islands, score
        
        info = rulers[ruler]
        rulers[ruler] = (info[0], info[1]+1, info[2]+isle.score)
    
    return rulers
    
def GetAllInfo(map_scan):
    isles = map_scan.islandsample_set.all()

    rulers = CalculateRulers( isles )
    alliances = CalculateAlliances(isles)

    return isles, rulers, alliances

def main():

    dir_path = configure()

    isle_list = scan.read(dir_path)
    
    #Save the new scan
    map_scan = MapScan( start_time=scan.start(dir_path), end_time=scan.end(dir_path) )
    map_scan.save()
    
    #Save islands
    for key in isle_list:
        info = isle_list[key]
        pos = utils.IslandPosition(info.position)
        sample = map_scan.islandsample_set.create(position=info.position, name=info.name, ruler=info.ruler, alliance_tag=info.alliance_tag, score=int(info.score), ocean=pos.ocean, group=pos.group, isle_num=pos.island, x=pos.x, y=pos.y)
        sample.save()

    #Calculate info    
    isles, rulers, alliances = GetAllInfo(map_scan)

    #Save players    
    for ruler in rulers:
        player = map_scan.playersample_set.create(name=ruler, alliance_tag=rulers[ruler][0], island_count=rulers[ruler][1], score=rulers[ruler][2])
        player.save()

    #Save alliances
    for atag in alliances:
        alliance = map_scan.alliancesample_set.create(tag=atag, score=alliances[atag])
        alliance.save()

    print '%d players, %d alliances' % (len(rulers),len(alliances))

if __name__ == "__main__":
    main()