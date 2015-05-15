# -*- coding: utf-8 -*-
# try something like
#def index(): return dict(message="hello from mon.py")

def index():
    import json
    from json import dumps
    import datetime
    from twisted.words.protocols import irc
    from twisted.internet import reactor, protocol
    from twisted.internet.protocol import ReconnectingClientFactory
    import wapiti
    from parsers import parse_irc_message
    
    DEFAULT_LANG = 'en'
    DEFAULT_PROJECT = 'wikipedia'
    DEFAULT_BCAST_PORT = 9000
    IRC_SERVER_HOST = 'irc.wikimedia.org'
    IRC_SERVER_PORT = 6667

    def strip_colors(msg):
        def _extract(formatted):
            if not hasattr(formatted, 'children'):
                return formatted
            return ''.join(map(_extract, formatted.children))

        return _extract(irc.parseFormattedText(msg))


    class Monitor(irc.IRCClient):
        
        nickname = 'wikimon'
        GEO_IP_KEY = 'geo_ip'

        def __init__(self,ns_map,factory):
            #self.geoip_db_monitor = geoip_db_monitor
            #self.broadcaster = bsf
            self.ns_map = ns_map
            self.factory = factory
            #irc_log.info('created IRC monitor...')

        def connectionMade(self):
            irc.IRCClient.connectionMade(self)
            #irc_log.info('connected to IRC server...')

        def signedOn(self):
            self.join(self.factory.channel)
            #irc_log.info('joined %s ...', self.factory.channel)

        def privmsg(self, user, channel, msg):
            msg = strip_colors(msg)

            try:
                msg = msg.decode('utf-8')
            except UnicodeError as ue:
                #bcast_log.warn('UnicodeError: %r on IRC message %r', ue, msg)
                return

            msg_dict = parse_irc_message(msg, self.ns_map)
            #print "----------------------"
            #print msg_dict
            if 'url' in msg_dict:
                #message="SomeOne editted page: %s || URL: %s"%(msg_dict['page_title'],msg_dict['url'])
                #print message
                u=msg_dict['url']
                pt=msg_dict['page_title']
                anonym=str(msg_dict['is_anon'])
                username='gaurav'
                userid='192.168.1.100'
                language='en'
                c=str(datetime.datetime.utcnow())
                #print "page_url=u,page_title=pt,user_name=username,is_anon=anonym,user_id=userid,lang=language,created=c"
                db.changes.insert(page_url=u,page_title=pt,user_name=username,is_anon=anonym,user_id=userid,lang=language,created=c)
                #message={'page_title':pt,'page_url':u,'is_anon':anonym,'username':username,'userid':userid,'lang':language,'timestamp':c}
                #return message
                

    class MonitorFactory(ReconnectingClientFactory):
        def __init__(self, channel,ns_map):
            self.channel = channel
            self.ns_map = ns_map

        def buildProtocol(self, addr):
            #irc_log.info('monitor IRC connected to %s', self.channel)
            self.resetDelay()
            return Monitor(self.ns_map, self)

        def startConnecting(self, connector):
            #irc_log.info('monitor IRC starting connection to %s', self.channel)
            protocol.startConnecting(self, connector)

        def clientConnectionLost(self, connector, reason):
            #irc_log.error('lost monitor IRC connection: %s', reason)
            ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

        def clientConnectionFailed(self, connector, reason):
            #irc_log.error('failed monitor IRC connection: %s', reason)
            ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                             reason)

    def start_monitor(lang=DEFAULT_LANG, project=DEFAULT_PROJECT):
        channel = '%s.%s' % (lang, project)
        api_url = 'http://%s.%s.org/w/api.php' % (lang, project)
        #api_log.info('fetching namespaces from %r', api_url)
        wc = wapiti.WapitiClient('wikimon@hatnote.com', api_url=api_url)
        #api_log.info('successfully fetched namespaces from %r', api_url)
        page_info = wc.get_source_info()
        ns_map = dict([(ns.title, ns.canonical)
                       for ns in page_info[0].namespace_map if ns.title])
        #irc_log.info('connecting to %s...', channel)
        #geoip_db_monitor = monitor_geolite2.begin(geoip_db,
                                                 # geoip_update_interval)
        f = MonitorFactory(channel,ns_map)
        reactor.connectTCP(IRC_SERVER_HOST, IRC_SERVER_PORT, f)
    


    start_monitor()
    reactor.run(installSignalHandlers=False)
    return locals()
