from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import os
import jinja2
import hashlib
import hmac
import string
import random

# Configure Jinja to be used as template framework
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

SECRET = "imsosecret"

# -------------- hash para passwords
def make_salt():
    # http://www.pythonforbeginners.com/basics/list-comprehensions-in-python
    return "".join(random.choice(string.letters) for x in xrange(5))

# implement the function make_pw_hash(name, pw) that returns a hashed password
# of the format:
# HASH(name + pw + salt),salt
# use sha256
def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()

    h = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s|%s" % (h, salt)

# Implement the function valid_pw() that returns True if a user's password
# matches its hash. You will need to modify make_pw_hash.
def valid_pw(name, pw, h):
    salt = h.split("|")[1]
    return h == make_pw_hash(name, pw, salt)

#h = make_pw_hash('spez', 'hunter2')
#print valid_pw('spez', 'hunter2', h)

# --------------- hash para cookies
def hash_str(s):
    # return hashlib.md5(s).hexdigest()
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    val = h.split("|")[0]
    if h == make_secure_val(val):
        return val

class Handler(webapp.RequestHandler):
    # Load the template
    # template below is the template file name
    def render_str(self, template, **kw):
        t = jinja_env.get_template(template)
        return t.render(**kw)

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def get(self):
        # Testa geracao de password
        h = make_pw_hash("Hyalen", "Moreira")
        print h
        print valid_pw("Hyalen", "Moreira", h)

        self.response.headers["content-type"] = "text/plain"

        # Testa cookie com hash
        # default value
        visits = 0

        visit_cookie_str = self.request.cookies.get("visits")

        if visit_cookie_str:
            cookie_val = check_secure_val(visit_cookie_str)

            if cookie_val:
                visits = int(cookie_val)

        visits += 1
        new_value = make_secure_val(str(visits))

        self.response.headers.add_header("Set-Cookie", "visits=%s" % new_value)

        self.write("You've been here %s times ..." % visits)

app = webapp.WSGIApplication([('/', MainPage)],
                                     debug = True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
