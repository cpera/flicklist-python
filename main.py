import webapp2
import cgi
import jinja2
import os

env = jinja2.Environment(
		loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')),
		autoescape=True)
		
# a list of movies that nobody should be allowed to watch
terrible_movies = [
	"Gigli",
	"Star Wars Episode 1: Attack of the Clones",
	"Paul Blart: Mall Cop 2",
	"Nine Lives"
]


def getCurrentWatchlist():
	""" Returns the user's current watchlist """

	# for now, we are just pretending
	return [ "Star Wars", "Minions", "Freaky Friday", "My Favorite Martian" ]


class Index(webapp2.RequestHandler):
	""" Handles requests coming in to '/' (the root of our site)
		e.g. www.flicklist.com/
	"""

	def get(self):	
		template = env.get_template('edit.html')
		content = template.render(crossedoffmovie=getCurrentWatchlist(), error=self.request.get('error'))		
		self.response.write(content)


class AddMovie(webapp2.RequestHandler):
	""" Handles requests coming in to '/add'
		e.g. www.flicklist.com/add
	"""

	def post(self):
		# look inside the request to figure out what the user typed
		new_movie = self.request.get("new-movie")

		# if the user typed nothing at all, redirect and yell at them
		if (not new_movie) or (new_movie.strip() == ""):
			error = "Please specify the movie you want to add."
			self.redirect("/?error=" + cgi.escape(error, quote=True))

		# if the user wants to add a terrible movie, redirect and yell at them
		if new_movie in terrible_movies:
			error = "Trust me, you don't want to add '{0}' to your Watchlist".format(new_movie)
			self.redirect("/?error=" + cgi.escape(error, quote=True))

		# 'escape' the user's input so that if they typed HTML, it doesn't mess up our site
		new_movie_escaped = cgi.escape(new_movie, quote=True)

		# build response content		
		template = env.get_template('addmovies.html')
		content = template.render(movietoadd=new_movie_escaped)	
		self.response.write(content)


class CrossOffMovie(webapp2.RequestHandler):
	""" Handles requests coming in to '/cross-off'
		e.g. www.flicklist.com/cross-off
	"""

	def post(self):
		# look inside the request to figure out what the user typed
		crossed_off_movie = self.request.get("crossed-off-movie")

		if (crossed_off_movie in getCurrentWatchlist()) == False:
			# the user tried to cross off a movie that isn't in their list,
			# so we redirect back to the front page and yell at them

			# make a helpful error message
			error = "'{0}' is not in your Watchlist, so you can't cross it off!".format(crossed_off_movie)

			# redirect to homepage, and include error as a query parameter in the URL
			self.redirect("/?error=" + error)

		# if we didn't redirect by now, then all is well
		template = env.get_template('crossoff.html')
		content = template.render(crossedoffmovie=crossed_off_movie)	
		self.response.write(content)


app = webapp2.WSGIApplication([
	('/', Index),
	('/add', AddMovie),
	('/cross-off', CrossOffMovie)
], debug=True)
