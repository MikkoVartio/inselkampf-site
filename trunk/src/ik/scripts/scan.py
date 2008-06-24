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
import os
import sgmllib
import datetime

class IslandInfo:
    def __init__(self):
        self.name = ''
        self.position = ''
        self.ruler = ''
        self.alliance_tag = ''
        self.score = '0'

class IkMapParser(sgmllib.SGMLParser):

    def __init__(self, isle_list, verbose=0):
        sgmllib.SGMLParser.__init__(self,verbose)
        self.isle_list = isle_list
        
    def do_area(self, attributes):
        
        data = self.find_data(attributes)
        if( data == None):
            return

        #Now each piece of information is in a different element of the array
        data_pieces = data.split('\n')
        
        isle = IslandInfo()
        
        for piece in data_pieces:
            if piece.startswith('Island: '):
                isle.name = piece.replace('Island: ','',1)
            if piece.startswith('Position: '):
                isle.position = piece.replace('Position: ','',1)
            if piece.startswith('Ruler: '):
                isle.ruler = piece.replace('Ruler: ','',1)
            if piece.startswith('Alliance: '):
                isle.alliance_tag = piece.replace('Alliance: ','',1)
            if piece.startswith('Score: '):
                isle.score = piece.replace('Score: ','',1)
        
        #Store the information, with the island position as the key
        self.isle_list[isle.position] = isle

    def find_data(self, attributes):

        for a in attributes:
            if( a[0] == 'title'):
                return a[1]
        
        return None

def ReadFile( raw_map, isle_list ):
    p = IkMapParser( isle_list )
    try:
        f = open(raw_map)
        try:
            s = f.read()
        finally:
            f.close()
        p.feed(s)
    finally:           
        p.close()

def read(dir_name):
    filelist = os.listdir(dir_name)
    isle_list = {}
    
    for i,f in enumerate(filelist):
        print i,f
        ReadFile(os.path.join(dir_name,f),isle_list)

    return isle_list
    
    
def start(dir_name):
    filelist = os.listdir(dir_name)
    
    times = [os.stat(os.path.join(dir_name,f)).st_mtime for f in filelist]
    return datetime.datetime.fromtimestamp( min(times) )

def end(dir_name):
    filelist = os.listdir(dir_name)
        
    times = [os.stat(os.path.join(dir_name,f)).st_mtime for f in filelist]
    return datetime.datetime.fromtimestamp( max(times) )
    
    
    
    
        
        
    