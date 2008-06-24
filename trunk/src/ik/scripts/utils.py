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
import math
import urllib
import urllib2

class IslandPosition:
    def __init__(self,pos_str):
        split_str = pos_str.split(':')
        
        self.ocean = int(split_str[0])
        self.group = int(split_str[1])
        self.island = int(split_str[2])
        self.x = self.CalcX()
        self.y = self.CalcY()
    
    def __str__(self):
        return "%d:%d:%d"%(self.ocean,self.group,self.island)
    
    def CalcX(self):
        oceanx = 50*((self.ocean-1) % 10)
        groupx = 5*((self.group-1) % 10)
        islex = (self.island-1) % 5
        return oceanx + groupx + islex
    
    def CalcY(self):
        oceany = int( (self.ocean-1)/10)*50
        groupy = int( (self.group-1)/10)*5
        isley  = int( (self.island-1)/5)
        return oceany + groupy + isley

    def distance_to(self,position):
        return distance(self,position)

def distance(pos1, pos2):
    """Takes two items with an x and y value and returns the, well, distance."""
    #Pythagorean Theorem
    return math.sqrt( math.pow(pos1.x-pos2.x,2) + math.pow(pos1.y-pos2.y,2) )
        
class IkSession:
    def __init__(self,username):
        self.id = None
        self.username = username
    
    def login(self, password):
        url = r'http://www.inselkampf.com/index.php?controller=sessions&action=create'

        #Masquerade as firefox out of paranoia
        headers = { 'user-agent' : r'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.3) Gecko/20070309 Firefox/2.0.0.3'}
        data = urllib.urlencode({'player':self.username,'password':password,'world':'1'})
        req = urllib2.Request(url,data, headers)
        page = urllib2.urlopen(req)

        str = page.read()
        page.close()
        
        #Find the session id
        tmp,s = page.geturl().split('=')
        self.id = s

    def logout(self):
        url = r'http://213.203.194.123/us/1/index.php?s=%s&a=logout' % self.id

        #Masquerade as firefox out of paranoia
        headers = { 'user-agent' : r'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.3) Gecko/20070309 Firefox/2.0.0.3'}
        req = urllib2.Request(url,None, headers)
        page = urllib2.urlopen(req)

        str = page.read()
        page.close()
        
        #Clean up
        self.id = None