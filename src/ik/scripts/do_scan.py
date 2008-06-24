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
import utils
import getopt,sys
import os
import urllib2
import time
import distutils.dir_util
import socket

def usage():
    head,tail = os.path.split(sys.argv[0])
    print "Usage:\n%s [-p <dir_path>] <username> <password>\n\nThis script downloads and stores an entire map scan. The default folder name is \'raw_maps\' but it can be changed with the -p option.\nOptions:\n\t-p <dir_path>" % tail

def configure():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"p:s:")
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    
    
    if len(args) != 2:
        print "Please provide a username and password."
        usage()
        sys.exit(3)

    username = args[0]
    password = args[1]

    dir_path = 'raw_maps'
    
    for o, a in opts:
        if o == '-p':
            dir_path = a
        if o == '-s':
            session_id = a

    return dir_path, username, password

def getMap(session_id, ocean, group):
    """http://213.203.194.123/us/1/index.php?s=ls70frb4c1au&p=map&pos1=1&pos2=12&zoom="""
    
    #Build url
    url = r'http://213.203.194.123/us/1/index.php?s=%(session)s&p=map&pos1=%(ocean)d&pos2=%(group)d&zoom=' % { 'session':session_id, 'ocean':ocean, 'group':group}
    
    #Masquerade as firefox out of paranoia
    headers = { 'user-agent' : r'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.3) Gecko/20070309 Firefox/2.0.0.3'}
    req = urllib2.Request(url,None, headers)

    #Keep querying until we're successful.
    done = False
    while not done:
        try:
            page = urllib2.urlopen(req)
            
            try:
                str = page.read()
            finally:
                page.close()
        except:
            time.sleep(5) #Sleep, for good karma
            print 'Retrying Page:'
        else:
            done = True
    
    page.close()
    
    return str

def getAllMaps(dir_path, session_id):
    group_list = [1,4,7,10,31,34,37,40,61,64,67,70,91,94,97,100]
    ocean_list = range(1,101)
    work_list = [(o,g) for o in ocean_list for g in group_list]

    for i,work in enumerate(work_list):

        fname = os.path.join(dir_path, r"o%d_g%d.html" % work)
        print i,fname
        page = getMap(session_id,work[0],work[1])

        f = open(fname,'w')
        try:
            f.write(page)
        finally:
            f.close()
            
    print 'Done.'

def main():

    #There's no way to set the default timeout for retrieving a
    #web page from the urllib2 library, but you CAN set the global
    #socket timeout. Set it to 10, so that we don't hang for minutes
    #at a time.
    timeout = 10
    socket.setdefaulttimeout(timeout)

    dir_path, username, password = configure()
   
    #Make sure the data directory exists
    distutils.dir_util.mkpath(dir_path)
    
    #Log in
    sess = utils.IkSession(username)
    sess.login(password)
    
    getAllMaps(dir_path, sess.id)

if __name__ == "__main__":
    main()