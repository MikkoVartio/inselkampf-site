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
from mealtracker.ik.models import MapScan, Alliance, Player, Island, IslandCapture

def update_islands(scan):
    island_samples = scan.islandsample_set.all()
    
    #Make a hash of the samples, with the position as a key
    island_sample_hash = dict([(sample.position, sample) for sample in island_samples])
    
    #Delete islands not seen in this scan
    islands = Island.objects.all()
    
    for island in islands:
        if island.position not in island_sample_hash:
            
            #Unregister all samples
            for sample in island.islandsample_set.all():
                sample.island = None
                sample.save()
            
            island.delete()
            
    #Now add islands that were seen for the first time
    islands = Island.objects.all()
    island_hash = dict([(island.position, island) for island in islands])
    
    for island_sample in island_samples:
        if island_sample.position not in island_hash:
            Island.objects.create(position=island_sample.position, ocean=island_sample.ocean, group=island_sample.group, isle_num=island_sample.isle_num, x=island_sample.x, y=island_sample.y)
    
    #Finally, attach the islands to the player that owns them, and update the island info
    islands = Island.objects.all()
    player_hash = dict([(player.name, player) for player in Player.objects.all()]) #Do this to speed the process up by not forcing a player query for every island.
    
    for island in islands:
        sample = island_sample_hash[island.position]
        
        sample.island = island
        sample.save()
        
        island.name = sample.name
        island.score = sample.score
        
        if sample.ruler is '':
            island.player = None
        else:
        
            new_player = player_hash[sample.ruler]
            
            if island.player and island.player.name != sample.ruler:
                capture = IslandCapture.objects.create(island=island, old_player = island.player, new_player = new_player, map_scan=scan)
                
            island.player = new_player
            
        island.save()

def update_players(scan):
    player_samples = scan.playersample_set.all()
    
    #Make a hash of the samples, with the name as a key
    player_sample_hash = dict([(sample.name, sample) for sample in player_samples])
    
    #Delete players not seen in this scan
    players = Player.objects.all()
    
    for player in players:
        if player.name not in player_sample_hash:
            
            #Remove this player as an owner of its islands
            for island in player.island_set.all():
                island.player = None
                island.save()
            
            #Unregister all samples
            for sample in player.playersample_set.all():
                sample.player = None
                sample.save()
            
            player.delete()
    
    #Now add players that were seen for the first time
    players = Player.objects.all()
    player_hash = dict([(player.name, player) for player in players])
    
    for player_sample in player_samples:
        if player_sample.name not in player_hash:
            Player.objects.create(name=player_sample.name)
    
    #Finally, attach the player samples to their corresponding player object
    # and update them.
    players = Player.objects.all()
    for player in players:
        sample = player_sample_hash[player.name]
        
        sample.player = player
        sample.save()
        
        player.score = sample.score

        
        # Update membership in the alliance
        if sample.alliance_tag is '':
            player.alliance = None
        else:
            player.alliance = Alliance.objects.get(tag=sample.alliance_tag)
            
        player.save()


def update_alliances(scan):
    alliance_samples = scan.alliancesample_set.all()
    #Make a hash of the samples, with the tag as a key
    alliance_sample_hash = dict([(sample.tag, sample) for sample in alliance_samples])

    #First, delete alliances not seen in this scan
    alliances = Alliance.objects.all()

    for alliance in alliances:
        if alliance.tag not in alliance_sample_hash:
            
            #Remove all players from this alliance before deleting it
            for player in alliance.player_set.all():
                player.alliance = None
                player.save()
                
            #Unregister all samples
            for sample in alliance.alliancesample_set.all():
                sample.alliance = None
                sample.save()
            
            alliance.delete()

    #Now add alliances that were seen for the first time
    alliances = Alliance.objects.all()
    alliance_hash = dict([(alliance.tag, alliance) for alliance in alliances])

    for alliance_sample in alliance_samples:
        if alliance_sample.tag not in alliance_hash:
            Alliance.objects.create(tag=alliance_sample.tag)

    #Finally, attach the alliance samples to their corresponding alliance object, and
    #update it.
    alliances = Alliance.objects.all()
    for alliance in alliances:
        sample = alliance_sample_hash[alliance.tag]

        sample.alliance = alliance
        sample.save()

        alliance.score = sample.score
        alliance.save()

def update_from_scan(scan):
    """This function updates the current understanding of inselkampf given the
    specified map scan"""
    
    update_alliances(scan)
    update_players(scan)
    update_islands(scan)