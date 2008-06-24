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
import smtplib
from django.template import Context, Template
from django.template.loader import get_template

SMTP_SERVER = ''
SMTP_USER = ''
SMTP_PASSWORD = ''



def send_feedback(message, sender_email):
    
    session = smtplib.SMTP(SMTP_SERVER)
    session.login(SMTP_USER, SMTP_PASSWORD)
    
    template = get_template('ik/feedback_message.txt')
    
    c = Context( { 'to':SMTP_USER, 'from':SMTP_USER, 'message':message, 'sender_email':sender_email} )
    message = template.render(c)

    try:
        session.sendmail(SMTP_USER, SMTP_USER, message)
    finally:
        pass
                