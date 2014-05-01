from mtvit import MTVItaly
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import urlparse
import xbmc

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')
addon = xbmcaddon.Addon()

NO_EPISODES = 30001

mtv = MTVItaly(base_url)

mode = args.get('mode', None)

if mode is None:
    for show in mtv.list_shows():
        li = xbmcgui.ListItem(show[0], iconImage = show[1])
        xbmcplugin.addDirectoryItem(handle = addon_handle, url = show[2], listitem = li, isFolder = True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'list_seasons':
    show_id = args['show_id'][0]
    try:
        for season in mtv.list_seasons(show_id):
            li = xbmcgui.ListItem(season[0])
            xbmcplugin.addDirectoryItem(handle = addon_handle, url = season[1], listitem = li, isFolder = True)

        xbmcplugin.endOfDirectory(addon_handle)
    except:
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('MTV Italy Ondemand', addon.getLocalizedString(NO_EPISODES))

elif mode[0] == 'list_episodes':
    season_id = args['season_id'][0]
    show_id = args['show_id'][0]
    for episode in mtv.list_episodes(show_id, season_id):
        li = xbmcgui.ListItem(episode[0], iconImage=episode[2])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=episode[3], listitem=li, isFolder = True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'showvid':
    episode_title = args['episode_title'][0]
    episode_image = args['episode_image'][0]
    episode_url = args['episode_url'][0]
    video_url = mtv.build_video_url(episode_url)
    li = xbmcgui.ListItem(episode_title, iconImage=episode_image)
    li.setInfo('video', { 'Title' : episode_title})
    xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(video_url + ' swfurl=http://media.mtvnservices.com/player/prime/mediaplayerprime.2.7.14.swf swfvfy=true', li)
