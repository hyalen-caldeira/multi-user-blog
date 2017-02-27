import os
import jinja2
import urllib2
import httplib
import logging
from xml.dom import minidom
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext import memcache

DEBUG = os.environ["SERVER_SOFTWARE"].startswith("Development")

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

art_key = db.key.from_path("ASCIIChan", "arts")

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    coords = db.GeoPtProperty()

GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"

def gmaps_img(points):
    markers = "&".join("marks=%s%s" % (p.lat, p.lon) for p in points)
    return GMAPS_URL + markers


IP_URL = "http://www.hostip.info/?ip="
def get_coords(ip):
    ip = "4.2.2.2"
    url = IP_URL + ip

    content = None

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
        }

        req = urllib2.Request(url, headers)
        content = urllib2.urlopen(req)
        print content.read()
        # content = urllib2.urlopen(url).read()
    except urllib2.HTTPError, e:
        # checksLogger.error('HTTPError = ' + str(e.code))
        print 'HTTPError = ' + str(e.code)
        print e.fp.read()
    except urllib2.URLError, e:
        # checksLogger.error('URLError = ' + str(e.reason))
        print 'URLError = ' + str(e.reason)
    except httplib.HTTPException, e:
        # checksLogger.error('HTTPException')
        print 'HTTPException'
    except Exception:
        # import traceback
        # checksLogger.error('generic exception: ' + traceback.format_exc())
        print 'generic exception: ' # + traceback.format_exc()

    if content:
        d = minidom.parseString(content)

        coords = d.getElementsByTagName("gml:coordinates")

        if coords and coords[0].childNodes[0].nodeValue:
            lon, lat = coords[0].childNodes[0].nodeValue.split(",")
            return db.GeoPt (lat, lon) # Data type especifico para localizacao - Google App Egine

class BaseHandler(webapp.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **kw):
        t = jinja_env.get_template(template)
        return t.render(kw)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# CACHE = {}
# def top_arts(update = False):
#     key = "top"

#     if not update and key in CACHE:
#         arts = CACHE[key]
#     else:
#         loggin.error("DB QUERY, this is not an error. Just a debug ...")
#         arts = db.GqlQuery("SELECT * FROM Art WHERE ANCESTOR IS :1 ORDER BY created DESC LIMIT 10", art_key)

#         # Prevent the running of multiple queries
#         arts = list(arts)

#         CACHE[key] = arts

#     return arts

def top_arts(update = False):
    key = "top"

    arts = memcache.get(key) # Key must be string

    if arts is None or update:
        loggin.error("DB QUERY, this is not an error. Just a debug ...")
        arts = db.GqlQuery("SELECT * FROM Art WHERE ANCESTOR IS :1 ORDER BY created DESC LIMIT 10", art_key)

        # Prevent the running of multiple queries
        arts = list(arts)

        memcache.set(key, arts)

    return arts

class MainPage(BaseHandler):
    def render_main_page(self, title="", art="", error=""):
        arts = top_arts()

        img_url = None
        # Find witch arts have coords
        points = filter(None, (a.coords for a in arts))
##      A linha acima faz o mesmo que o codigo abaixo
##        points = []
##        for a in arts:
##            if a.coords:
##                points.append(a.coords)

        if points:
            img_url = gmaps_img(points)

        self.render("main_page.html", title=title, art=art, error=error, arts=arts, img_url=img_url)

    def get(self):
        self.write(repr(get_coords(self.request.remote_addr)))
        self.render_main_page()

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            art_instance = Art(title = title, art = art)
            coords = get_coords(self.request.remote_addr)
            if coords:
                art_instance.coords = coords

            art_instance.put()
            # CACHE.clear()
            # Instead of clear the cache, rerun the query and update the cache
            # Updating the cache avoid too many operations at the same time trying to access the DB.
            # Think concurrently
            top_arts(True)
            # reload de page
            self.redirect("/asciichan/main")
            # self.write("Isso ai, ate agora tudo certo ...")
        else:
            error_msg = "Todos os campos precisam ser preenchidos ..."
            self.render_main_page(title, art, error_msg)

app = webapp.WSGIApplication([('/asciichan/main', MainPage)],
                              debug=True)
