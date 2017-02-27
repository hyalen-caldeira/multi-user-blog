import webapp2

class MainPage(webapp2.RequestHandler)
    def get(self)
        self.response.headers['content-type'] = 'text/plain'
        self.response.out.write("Hi guys, here I am ...")

app = webapp2.WSGIApplication(["/", MainPage], debug = true)