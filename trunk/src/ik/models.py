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
import time
from django.db import models
import random
from django.db.models import permalink
import urllib

################################################################################

class Alliance(models.Model): 
    """This class represent the most up todate information about a given alliance."""
    
    tag = models.CharField(maxlength=16)
    score = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return '%s %d' % (self.tag, self.score)
        
    @permalink
    def get_absolute_url(self):
        return ('mealtracker.ik.info.views.alliance', (), {'tag_quoted': urllib.quote_plus(self.tag) } )


class Player(models.Model): 
    """This class represents the most up to date information about a given player."""
    name    = models.CharField(maxlength=32)
    score   = models.PositiveIntegerField(default = 0)
    alliance = models.ForeignKey(Alliance, null=True)
    
    @permalink
    def get_absolute_url(self):
        return ('mealtracker.ik.info.views.player', (),{'name':self.name})   

class Island(models.Model): 
    position = models.CharField(maxlength=11)
    name     = models.CharField(maxlength=64, default = '')
    score    = models.PositiveIntegerField(default=0)
    
    ocean    = models.PositiveIntegerField()
    group    = models.PositiveIntegerField()
    isle_num = models.PositiveIntegerField()
    x        = models.PositiveIntegerField()
    y        = models.PositiveIntegerField()
    
    player   = models.ForeignKey(Player, null=True)
    
    @permalink
    def get_absolute_url(self):
        return ('mealtracker.ik.info.views.island', (),{'ocean_s':self.ocean, 'group_s':self.group, 'isle_num_s':self.isle_num})


########################################################################################
class MapScan(models.Model):
    created_on = models.DateTimeField(auto_now_add = True)
    start_time = models.DateTimeField('Scan Start Time')
    end_time = models.DateTimeField('Scan Completion Time')
    
    def __str__(self):
        return str(self.end_time)
    
    class Meta:
        get_latest_by = 'end_time'
    
    class Admin:
        pass

class IslandSample(models.Model):
    map_scan = models.ForeignKey(MapScan)
    position = models.CharField(maxlength=11)
    name     = models.CharField(maxlength=64)
    ruler    = models.CharField(maxlength=32)
    alliance_tag = models.CharField(maxlength=16)
    score    = models.PositiveIntegerField()
    
    ocean    = models.PositiveIntegerField()
    group    = models.PositiveIntegerField()
    isle_num = models.PositiveIntegerField()
    x        = models.PositiveIntegerField()
    y        = models.PositiveIntegerField()
    
    island   = models.ForeignKey(Island, null=True) #Added
    
    def scan_time(self):
        return self.map_scan.end_time
    
    def player_sample(self):
        return self.map_scan.playersample_set.get(name=self.ruler)
    
    def __str__(self):
        return '%(name)s %(position)s %(ruler)s %(alliance_tag)s %(score)d' % {'name':self.name,'position':self.position,'ruler':self.ruler,'alliance_tag':self.alliance_tag,'score':self.score}
    
    @permalink
    def get_absolute_url(self):
        return ('mealtracker.ik.info.views.island', (),{'ocean_s':self.ocean, 'group_s':self.group, 'isle_num_s':self.isle_num})
    

class PlayerSample(models.Model):
    map_scan = models.ForeignKey(MapScan)
    name     = models.CharField(maxlength=32)
    alliance_tag = models.CharField(maxlength=16)
    island_count = models.PositiveIntegerField()
    score = models.PositiveIntegerField()
    player = models.ForeignKey(Player, null=True) #Added
    
    def scan_time(self):
        return self.map_scan.end_time
    
    def __str__(self):
        return '%s %s %d %d' % (self.name, self.alliance_tag, self.island_count, self.score)

    @permalink
    def get_absolute_url(self):
        return ('mealtracker.ik.info.views.player', (),{'name':self.name})    

class AllianceSample(models.Model):
    map_scan = models.ForeignKey(MapScan)
    tag = models.CharField(maxlength=16)
    score = models.PositiveIntegerField()
    alliance = models.ForeignKey(Alliance, null=True) 
        
    def scan_time(self):
        return self.map_scan.end_time
    
    def __str__(self):
        return '%s %d' % (self.tag, self.score)
 
 #########################################################################################
 
class IslandCapture(models.Model):
    island = models.ForeignKey(Island)

    old_player = models.ForeignKey(Player, related_name='islandloss_set')
    new_player = models.ForeignKey(Player)

    map_scan = models.ForeignKey(MapScan)
  

 
################################################################################

class Archive(models.Model):
    created_on = models.DateTimeField(auto_now_add = True)    
    ticket = models.SlugField(maxlength=32)
    
    def make_new_ticket(self):
        self.ticket = "%d" % random.randint(0,99999999999999999999)
        
    def get_absolute_url(self):
        return r'/ik/spy_reports/ticket/%d/%s/' % (self.id, self.ticket)
        
    class Admin:
        pass

class SpyReport(models.Model):
    created_on = models.DateTimeField(auto_now_add = True)    
    archive = models.ForeignKey(Archive)
    raw_text = models.TextField(maxlength=1023)

    position = models.CharField(maxlength=11)
    x        = models.PositiveIntegerField(default=0)
    y        = models.PositiveIntegerField(default=0)
    name        = models.CharField(maxlength=64)
    ruler           = models.CharField(maxlength=32)

    large_warships  = models.PositiveIntegerField(default=0)
    small_warships  = models.PositiveIntegerField(default=0)
    large_merchant  = models.PositiveIntegerField(default=0)
    small_merchant  = models.PositiveIntegerField(default=0)
    colo_ship       = models.PositiveIntegerField(default=0)
    
    spearfighters   = models.PositiveIntegerField(default=0)
    archers         = models.PositiveIntegerField(default=0)
    stone_throwers  = models.PositiveIntegerField(default=0)
    catapaults      = models.PositiveIntegerField(default=0)

    main_house      = models.PositiveIntegerField(default=0)
    gold_mine       = models.PositiveIntegerField(default=0)
    stone_quarry    = models.PositiveIntegerField(default=0)
    lumber_mill     = models.PositiveIntegerField(default=0)
    laboratory      = models.PositiveIntegerField(default=0)
    barracks        = models.PositiveIntegerField(default=0)
    harbour         = models.PositiveIntegerField(default=0)
    storehouse      = models.PositiveIntegerField(default=0)
    stone_wall      = models.PositiveIntegerField(default=0)
    watch_tower     = models.PositiveIntegerField(default=0)
    
    tech_spear      = models.PositiveIntegerField(default=0)
    tech_shield     = models.PositiveIntegerField(default=0)
    tech_bow        = models.PositiveIntegerField(default=0)
    tech_sail       = models.PositiveIntegerField(default=0)
    
    gold            = models.PositiveIntegerField(default=0)
    stone           = models.PositiveIntegerField(default=0)
    lumber          = models.PositiveIntegerField(default=0)
    
    class Admin:
        pass
