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

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def list_episodes(series_name, series_season):
    mtv_base_url =  'http://ondemand.mtv.it'
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
    return episodes

def build_video_url(episode_url):
    start = '<head>'
    end = '</head>'
    link = r'(?<=link rel="video).*/(.*)\.swf'
    base_video_url = 'http://intl.esperanto.mtvi.com/www/xml/media/mediaGen.jhtml?'
    episode_head = requests.get(episode_url).content.split(start,1)[-1].split(end,1)[0].replace('\n', ' ')
    video_id = re.search(link, episode_head).group(1).replace('videolist','video')
    video_url = base_video_url + urllib.urlencode({'uri' : video_id})
    print video_url
    dom = parse(urllib.urlopen(video_url))
    print getText(dom.getElementsByTagName("src")[0].childNodes)
    return getText(dom.getElementsByTagName("src")[0].childNodes)


mode = args.get('mode', None)

if mode is None:
    for episode in list_episodes('the-valleys', 's03'):
        li = xbmcgui.ListItem(episode[0], iconImage=episode[1])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=episode[2], listitem=li)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'showvid':
    episode_url = args['episode_url'][0]
    video_url = build_video_url(episode_url)
    xbmc.Player().play(video_url)
