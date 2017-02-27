from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import os
import jinja2

# Configure Jinja to be used as template framework
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

form_html = """
<form>
    <h2>Add a food</h2>
    <input type='text' name='food'>
    <input type='hidden' name='food' value='eggs'>
    <button>Add</button>
</form>
"""


# gretting = "Hello, %s"
# print gretting % "Hyalen"
# Vai imprimir "Hello, Hyalen"

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
        n = self.request.get("n")

        if n:
            n = int(n)

        # self.write(form_html)
        self.render("shopping_list.html", n = n)

class FizzBuzz(Handler):
    def get(self):
        n = self.request.get("n", 0)

        n = n and int(n)

        self.render("fizzbuzz.html", n = n)

class AllConcepts(Handler):
    def get(self):
        items = self.request.get_all("food");
        self.render("all_concepts.html", items = items)

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/fizzbuzz', FizzBuzz),
                                      ('/all_concepts', AllConcepts)],
                                     debug = True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
