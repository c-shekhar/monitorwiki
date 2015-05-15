# -*- coding: utf-8 -*-
import json
from json import dumps
from os.path import dirname, abspath

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.internet.protocol import ReconnectingClientFactory
import time
import datetime
import wapiti
from parsers import parse_irc_message
import monitor_geolite2
from freegeoip import get_geodata
import mysql.connector
from mysql.connector import MySQLConnection, Error
DEBUG = False
import logging
from twisted.python.log import PythonLoggingObserver
observer = PythonLoggingObserver()
observer.start()

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s\t%(name)s\t %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
bcast_log = logging.getLogger('bcast_log')
irc_log = logging.getLogger('irc_log')
api_log = logging.getLogger('api_log')


DEFAULT_LANG = 'en'
DEFAULT_PROJECT = 'wikipedia'
IRC_SERVER_HOST = 'irc.wikimedia.org'
IRC_SERVER_PORT = 6667
Edit=0.0
# time1=0
def strip_colors(msg):
    def _extract(formatted):
        if not hasattr(formatted, 'children'):
            return formatted
        return ''.join(map(_extract, formatted.children))

    return _extract(irc.parseFormattedText(msg))


class Monitor(irc.IRCClient):

    nickname = 'MinorII'

    def __init__(self,ns_map, factory):
        self.ns_map = ns_map
        self.factory = factory
        irc_log.info('created IRC monitor...')

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        irc_log.info('connected to IRC server...')

    def signedOn(self):
        self.join(self.factory.channel)
        irc_log.info('joined %s ...', self.factory.channel)
        time1=time.time()

    def insert_data(title, url,is_anon,id):
        query = "INSERT INTO dem(title,url,is_anon,id) " \
                "VALUES(%s,%s,%s,%s)"
        args = (title, url,is_anon,id)


    def privmsg(self, user, channel, msg):

        msg = strip_colors(msg)

        try:
            msg = msg.decode('utf-8')
        except UnicodeError as ue:
            bcast_log.warn('UnicodeError: %r on IRC message %r', ue, msg)
            return
        
        msg_dict = parse_irc_message(msg, self.ns_map)
        print 'START!...START!...START!...START!...START!...START!...START!...START!...START!...START!...'
        print msg_dict
        global Edit
        Edit=Edit+1
        print "#####yoyoy###......"
        try:
            conn = mysql.connector.connect(host='localhost',
                                           database='minor',
                                           user='root',
                                           password='password')
            print ("string1");
            if conn.is_connected():
                print('Connected to MySQL database')
                cursor = conn.cursor();
                if 'url' in msg_dict:
                    tem1=msg_dict['url'];
                    tem2=tem1.split('.');
                    tem3=tem2[0].split('//')
                    tem4=tem3[1];
                    query = ("INSERT INTO edits(page_title,is_anon,url,is_unpatrolled,parent_rev_id,is_bot,is_new,is_minor,summary,flags,user_name,actions,ns,change_size,rev_id,updated,epm,lang) VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%.5f','%s')" %(msg_dict['page_title'], msg_dict['is_anon'],msg_dict['url'],msg_dict['is_unpatrolled'],msg_dict['parent_rev_id'],msg_dict['is_bot'],msg_dict['is_new'],msg_dict['is_minor'],msg_dict['summary'],msg_dict['flags'],msg_dict['user'],msg_dict['action'],msg_dict['ns'],msg_dict['change_size'],msg_dict['rev_id'],str(datetime.datetime.now()),Edit/60.0,tem4))
                    # cursor = conn.cursor()
                    print ("string2")
                    cursor.execute(query)
                    if cursor.lastrowid:
                        print ("string3")
                        print('last insert id', cursor.lastrowid)
                    else:
                        print('last insert id not found')
                    conn.commit()
                    print ("string4")
        except Error as e:
            print ("string5")
            print(e)
     
        finally:
            cursor.close()        
            conn.close()
        if msg_dict.get('is_anon'):
            tt=msg_dict['user']
            print 'ip address:--', tt + '#########.......' 
            geodata=get_geodata(tt)
            print "IP: %s" % geodata["ip"]
            print "Country Code: %s" % geodata["countrycode"]
            print "Country Name: %s" % geodata["countryname"]
            print "Region Code: %s" % geodata["regioncode"]
            print "Region Name: %s" % geodata["regionname"]
            print "City: %s" % geodata["city"]
            print "Zip Code: %s" % geodata["zipcode"]
            print "Latitude: s%s" % geodata["latitude"]
            print "Longitude: %s" % geodata["longitude"]
            f=open("geolocation.txt","w")
            f.write(geodata["longitude"]+','+geodata["latitude"]+'\n')
            f.close()
            lg=open("log.txt","a+")
            lg.write(geodata["longitude"]+','+geodata["latitude"]+'\n')
            lg.close()

            # get_geodata(msg_dict[])
        print "Edits per min:--%.5f" %(Edit/60.0)    
        print 'END!....END!....END!....END!....END!....END!....END!....END!....END!....END!....END!....'
        

class MonitorFactory(ReconnectingClientFactory):
    def __init__(self, channel, ns_map):
        self.channel = channel
        self.ns_map = ns_map

    def buildProtocol(self, addr):
        irc_log.info('monitor IRC connected to %s', self.channel)
        self.resetDelay()
        return Monitor(self.ns_map, self)

    def startConnecting(self, connector):
        irc_log.info('monitor IRC starting connection to %s', self.channel)
        protocol.startConnecting(self, connector)

    def clientConnectionLost(self, connector, reason):
        irc_log.error('lost monitor IRC connection: %s', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        irc_log.error('failed monitor IRC connection: %s', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)

def start_monitor(lang=DEFAULT_LANG, project=DEFAULT_PROJECT):
    channel = '%s.%s' % (lang, project)
    api_url = 'http://%s.%s.org/w/api.php' % (lang, project)
    api_log.info('fetching namespaces from %r', api_url)
    wc = wapiti.WapitiClient('wikimon@hatnote.com', api_url=api_url)
    
    api_log.info('successfully fetched namespaces from %r', api_url)
    page_info = wc.get_source_info()
    ns_map = dict([(ns.title, ns.canonical)
                   for ns in page_info[0].namespace_map if ns.title])
    irc_log.info('connecting to %s...', channel)
    # geoip_db_monitor = monitor_geolite2.begin(geoip_db,
    #                                           geoip_update_interval)
    
    f = MonitorFactory(channel, ns_map)
    reactor.connectTCP(IRC_SERVER_HOST, IRC_SERVER_PORT, f)

"""def get_argparser():
    from argparse import ArgumentParser
    desc = "broadcast realtime edits to a Mediawiki project over websockets"
    prs = ArgumentParser(description=desc)
    prs.add_argument('--geoip_db', default=None,
                     help='path to the GeoLite2 database')
    prs.add_argument('--geoip-update-interval',
                     default=monitor_geolite2.DEFAULT_INTERVAL,
                     type=int,
                     help='how often (in seconds) to check'
                     ' for updates in the GeoIP db')
    prs.add_argument('--project', default=DEFAULT_PROJECT)
    prs.add_argument('--lang', default=DEFAULT_LANG)
    prs.add_argument('--port', default=DEFAULT_BCAST_PORT, type=int,
                     help='listen port for websocket connections')
    prs.add_argument('--debug', default=DEBUG, action='store_true')
    prs.add_argument('--loglevel', default='WARN',
                     help='e.g., DEBUG, INFO, WARN, etc.')
    return prs
"""

def main():
    start_monitor('en')
    start_monitor('fr')
    start_monitor('de')
    start_monitor('pt')
    start_monitor('ru')
    start_monitor('pl')
    start_monitor('cs')
    start_monitor('it')
    start_monitor('es')
    start_monitor('id')
    reactor.run()

if __name__ == '__main__':
    # global edit
    main()
