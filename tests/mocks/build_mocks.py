import os
import requests

video_url = 'http://intl.esperanto.mtvi.com/www/xml/media/mediaGen.jhtml?uri=mgid%3Auma%3Avideo%3Amtv.it%3A919998'
content = requests.get(video_url).content
fn = os.path.join(os.path.dirname(__file__), 'video_qualities_mock.xml')
f = open(fn, 'w')
f.write(content)
