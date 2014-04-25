import sys
import xbmcgui
import xbmcplugin
import re, requests, HTMLParser, os, pipes
import urllib, urlparse
import xbmc
from xml.dom.minidom import parse

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

mtv_base_url =  'http://ondemand.mtv.it'

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def list_seasons(series_name):
    seasons_url = mtv_base_url + '/serie-tv/' + series_name
    start = '<nav id="seasonNav"'
    end = '</nav>'
    divider = '<li>'
    season = r'(?=<a).*href="/serie-tv/' + series_name +'/([^"]+)"[^>]*>([^<]+)<'
    season_list = requests.get(seasons_url).content.split(start,1)[-1].split(end,1)[0]
    season_list = season_list.replace('\n', ' ').split(divider)[1:]
    seasons = []
    for s in season_list:
        groups = re.search(season, s)
        season_id = groups.group(1)
        season_title = groups.group(2)
        seasons.append(tuple([season_title, build_url({'season_id': season_id, 'mode': 'list_episodes'})]))
    return seasons

def list_episodes(series_name, series_season):
    mtv_url = mtv_base_url + '/serie-tv/' + series_name + '/' + series_season
    start = '<section id="season"'
    end = '</section>'
    divider = '<li itemprop="episode"'
    title = r'<strong itemprop="name">([^<]+)</strong>'
    image = r'(?<=img).*data-original="([^"]+)"'
    url = r'a href="([^"]+)"'
    episode_list = requests.get(mtv_url).content.split(start,1)[-1].split(end,1)[0]
    episode_list = episode_list.replace('\n', ' ').split(divider)[1:]
    episodes = []
    for episode in episode_list:
        ep_title = re.search(title, episode).group(1)
        ep_image = re.search(image, episode).group(1)
        ep_url = re.search(url, episode).group(1)
        episodes.append(tuple([ep_title, ep_image, build_url({'episode_url' : mtv_base_url + ep_url, 'mode': 'showvid'})]))
    print episodes
    return episodes

def build_video_url(episode_url):
    start = '<head>'
    end = '</head>'
    link = r'(?<=link rel="video).*/(.*)\.swf'
    base_video_url = 'http://intl.esperanto.mtvi.com/www/xml/media/mediaGen.jhtml?'
    episode_head = requests.get(episode_url).content.split(start,1)[-1].split(end,1)[0].replace('\n', ' ')
    video_id = re.search(link, episode_head).group(1).replace('videolist','video')
    video_url = base_video_url + urllib.urlencode({'uri' : video_id})
    dom = parse(urllib.urlopen(video_url))
    return getText(dom.getElementsByTagName("src")[0].childNodes)


mode = args.get('mode', None)

if mode is None:
    for season in list_seasons('the-valleys'):
        li = xbmcgui.ListItem(season[0])
        xbmcplugin.addDirectoryItem(handle = addon_handle, url = season[1], listitem = li, isFolder = True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'list_episodes':
    season_id = args['season_id'][0]
    for episode in list_episodes('the-valleys', season_id):
        li = xbmcgui.ListItem(episode[0], iconImage=episode[1])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=episode[2], listitem=li, isFolder = True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'showvid':
    print 'in mode showvid'
    episode_url = args['episode_url'][0]
    video_url = build_video_url(episode_url)
    xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(video_url + ' swfurl=http://media.mtvnservices.com/player/prime/mediaplayerprime.2.7.14.swf swfvfy=true')
