import re, requests 
import urllib
from xml.dom.minidom import parse
from operator import itemgetter

class MTVItaly():
    mtv_base_url =  'http://ondemand.mtv.it'

    def __init__(self, base_url):
        self._base_url = base_url

    def _build_url(self, query):
        return self._base_url + '?' + urllib.urlencode(query)

    def _getText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def list_shows(self):
        show_url = self.mtv_base_url + '/serie-tv/'
        start = '<section id="showsEpisodes"'
        end = '</section>'
        divider = '<li id='
        show_id = r'(?=<a).*href="/serie-tv/([^"]+)"'
        show_image = r'(?=<img).*data-original="([^\?|"]+)[\?"]'
        show_title = r'strong>([^<]+)</strong'
        show_list = requests.get(show_url).content.split(start,1)[-1].split(end,1)[0]
        show_list = show_list.replace('\n', ' ').split(divider)[1:]
        shows = []
        for s in show_list:
            s_id = re.search(show_id, s).group(1)
            s_image = re.search(show_image, s).group(1)
            s_title = re.search(show_title, s).group(1)
            shows.append(tuple([s_title, s_image, self._build_url({'show_id' : s_id, 'mode': 'list_seasons'})]))
        return sorted(shows, key = itemgetter(0))


    def list_seasons(self, show_id):
        seasons_url = self.mtv_base_url + '/serie-tv/' + show_id
        start = '<nav id="seasonNav"'
        end = '</nav>'
        divider = '<li>'
        season = r'(?=<a).*href="/serie-tv/' + show_id +'/([^"]+)"[^>]*>([^<]+)<'
        season_list = requests.get(seasons_url).content.split(start,1)[-1].split(end,1)[0]
        season_list = season_list.replace('\n', ' ').split(divider)[1:]
        seasons = []
        for s in season_list:
            groups = re.search(season, s)
            season_id = groups.group(1)
            season_title = groups.group(2)
            seasons.append(tuple([season_title, self._build_url({'show_id': show_id, 'season_id': season_id, 'mode': 'list_episodes'})]))
        return sorted(seasons, key = itemgetter(0))

    def list_episodes(self, show_id, show_season):
        mtv_url = self.mtv_base_url + '/serie-tv/' + show_id + '/' + show_season
        start = '<section id="season"'
        end = '</section>'
        divider = '<li itemprop="episode"'
        title = r'<strong itemprop="name">([^<]+)</strong>'
        image = r'(?<=img).*data-original="([^"]+)"'
        episode_number = r'<strong itemprop="episodeNumber">([^<]+)</strong'
        url = r'a href="([^"]+)"'
        episode_list = requests.get(mtv_url).content.split(start,1)[-1].split(end,1)[0]
        episode_list = episode_list.replace('\n', ' ').split(divider)[1:]
        episodes = []
        for episode in episode_list:
            ep_title = re.search(title, episode).group(1)
            ep_image = re.search(image, episode).group(1)
            ep_url = re.search(url, episode).group(1)
            try:
                ep_number = int(re.search(episode_number, episode).group(1))
            except:
                print 'Found no episode number for ' + ep_title + ', assuming is a promo'
                ep_number = 999
            episodes.append(tuple([ep_title, ep_number, ep_image, self._build_url({'episode_title': ep_title, 'episode_image': ep_image, 'episode_url' : self.mtv_base_url + ep_url, 'mode': 'showvid'})]))
        return sorted(episodes, key = itemgetter(1, 0))

    def build_video_url(self, episode_url):
        start = '<head>'
        end = '</head>'
        link = r'(?<=link rel="video).*/(.*)\.swf'
        base_video_url = 'http://intl.esperanto.mtvi.com/www/xml/media/mediaGen.jhtml?'
        episode_head = requests.get(episode_url).content.split(start,1)[-1].split(end,1)[0].replace('\n', ' ')
        video_id = re.search(link, episode_head).group(1).replace('videolist','video')
        video_url = base_video_url + urllib.urlencode({'uri' : video_id})
        dom = parse(urllib.urlopen(video_url))
        return self._getText(dom.getElementsByTagName("src")[0].childNodes)
