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
from utils import IkSession
import urllib2
import time

def doit():
    sess = IkSession('username')
    sess.login('password')

    url = r"http://213.203.194.123/us/1/index.php?s=%s&p=b1&a=order&id=b9" % sess.id

    #Masquerade as firefox out of paranoia
    headers = { 'user-agent' : r'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.3) Gecko/20070309 Firefox/2.0.0.3'}
    req = urllib2.Request(url,None, headers)
    page = urllib2.urlopen(req)

    str = page.read()
    page.close()

    sess.logout()

while True:
    print str(time.time())
    doit()
    time.sleep(3600)