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
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django import newforms as forms
from mealtracker.ik.models import SpyReport, Archive
import re

################################################################
# Site Index

class SpyReportParser:

    def parse_description(self,description, text, callback):
        pattern = r'%s\W+(\d+)' % description
        result = re.search(pattern, text)
        if result is not None:
            num = int(result.group(1))
            callback( num )

    def parse_building(self, description, text, callback):
        pattern = r'%s\W+Level' % description
        self.parse_description(pattern, text, callback)

    def read(self,raw_text):
    
        result = re.search(r"Espionage of (.*) \((\d+:\d+:\d+)\)", raw_text)
        if result is not None:
            self.do_name(result.group(1))
            self.do_position(result.group(2))
        else:
            #We NEED the position info, so just look for that anywhere.
            #If for some reason more than one match is made (which would
            #happen if the island name contained something that looks like
            #a position) then use the last one found (because island name
            #comes first).
            result = re.findall(r"(\d+:\d+:\d+)", raw_text)
            if len(result) is not 0:
                self.do_position(result[-1])

        # Two player names may be listed, if so, the last one is the
        # ruler of the isle.
        result = re.findall(r'Units of (\w*)',raw_text)
        if len(result) is not 0:
            self.do_ruler(result[-1])
            
        # We want to avoid including the spy ship in the report, so chop
        # it off after the player names, and work only with that from this point
        # on. This also avoids potential injection via the island name.
        # If no player names at all are included, this will just result in us
        # working with the whole string.
        chopped_text = re.split(r'Units of (\w*)', raw_text)[-1]

        self.parse_description('Large Warships', chopped_text, self.do_large_warships)
        self.parse_description('Small Warships', chopped_text, self.do_small_warships)
        self.parse_description('Spearfighters', chopped_text, self.do_spearfighters)
        self.parse_description('Archers', chopped_text, self.do_archers)
        self.parse_description('Stone Throwers', chopped_text, self.do_stone_throwers)
        self.parse_description('Catapults', chopped_text, self.do_catapaults)
        
        self.parse_building('Gold Mine', chopped_text, self.do_gold_mine)
        self.parse_building('Stone Wall', chopped_text, self.do_stone_wall)
        
        
        

        
class SpyReportBuilder(SpyReportParser):
    def __init__(self, archive):
        self.archive = archive
    
    def from_text(self,raw_text):
        self.report = self.archive.spyreport_set.create()
        self.report.raw_text = raw_text
        self.read(raw_text)
        
    def do_name(self, name):
        self.report.name = name
    
    def do_position(self, position):
        self.report.position = position

    def do_ruler(self, ruler):
        self.report.ruler = ruler
    
    def do_large_warships(self, num):
        self.report.large_warships = num
        
    def do_small_warships(self, num):
        self.report.small_warships = num
    
    def do_spearfighters(self, num):
        self.report.spearfighters = num
        
    def do_archers(self, num):
        self.report.archers = num
        
    def do_stone_throwers(self, num):
        self.report.stone_throwers = num
    
    def do_catapaults(self, num):
        self.report.catapaults = num
    
    def do_gold_mine(self, num):
        self.report.gold_mine = num
    
    def do_stone_wall(self, num):
        self.report.stone_wall = num
        

def makeReports(archive, request):
    text = request.POST['report_text']
    
    builder = SpyReportBuilder(archive)
    
    #This regex will split on any pair of consecutive newlines, as long
    #as there is no non whitespace between them.This will also strip out
    #any whitespace at the end of the first line as well, which means that
    #if there are a large number of lines with random whitespace in them,
    #that will all be converted to blank lines.
    for raw_text in re.split(r'\s*?\n\s*?\n',text):
        
        #Skip extra blank lines
        if raw_text == '':
            continue
            
        builder.from_text(raw_text)
        builder.report.save()

def index(request):

    if request.POST.has_key('report_text'):
        archive = Archive()
        archive.make_new_ticket()
        archive.save()
        
        makeReports(archive, request)
        
        return HttpResponseRedirect(archive.get_absolute_url())
        
    return render_to_response('ik/spy_reports/index.html', {})

###############################################################################
    
def ticket(request, archive_id, ticket_num):
    archive = Archive.objects.get(id=archive_id, ticket=ticket_num)
    
    if request.POST.has_key('report_text'):
        makeReports(archive,request)
        
    reports = archive.spyreport_set.values()

    return render_to_response('ik/spy_reports/ticket.html', {'reports':reports})
