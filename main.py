import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db
import re

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

# a list of movies that nobody should be allowed to watch
terrible_movies = [
	"Gigli",
	"Star Wars Episode 1: Attack of the Clones",
	"Paul Blart: Mall Cop 2",
	"Nine Lives"
]

class User(db.Model):
	username = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	

class Movie(db.Model):
	title = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	watched = db.BooleanProperty(required = True, default = False)
	rating = db.StringProperty()

class Handler(webapp2.RequestHandler):
	""" A base RequestHandler class for our app.
		The other handlers inherit form this one.
	"""

	def renderError(self, error_code):
		""" Sends an HTTP error code and a generic "oops!" message to the client. """

		self.error(error_code)
		self.response.write("Oops! Something went wrong.")

	def get_user_by_username(self, username):
		result = db.GqlQuery("SELECT * FROM User WHERE username = '%s'" % username)
		return result.get()
	

class Index(Handler):
	""" Handles requests coming in to '/' (the root of our site)
		e.g. www.flicklist.com/
	"""

	def get(self):
		unwatched_movies = db.GqlQuery("SELECT * FROM Movie where watched = False")
		t = jinja_env.get_template("frontpage.html")
		content = t.render(
						movies = unwatched_movies,
						error = self.request.get("error"))
		self.response.write(content)

class AddMovie(Handler):
	""" Handles requests coming in to '/add'
		e.g. www.flicklist.com/add
	"""

	def post(self):
		new_movie_title = self.request.get("new-movie")

		# if the user typed nothing at all, redirect and yell at them
		if (not new_movie_title) or (new_movie_title.strip() == ""):
			error = "Please specify the movie you want to add."
			self.redirect("/?error=" + cgi.escape(error))

		# if the user wants to add a terrible movie, redirect and yell at them
		if new_movie_title in terrible_movies:
			error = "Trust me, you don't want to add '{0}' to your Watchlist.".format(new_movie_title)
			self.redirect("/?error=" + cgi.escape(error, quote=True))

		# 'escape' the user's input so that if they typed HTML, it doesn't mess up our site
		new_movie_title_escaped = cgi.escape(new_movie_title, quote=True)

		# construct a movie object for the new movie
		movie = Movie(title = new_movie_title_escaped)
		movie.put()

		# render the confirmation message
		t = jinja_env.get_template("add-confirmation.html")
		content = t.render(movie = movie)
		self.response.write(content)


class WatchedMovie(Handler):
	""" Handles requests coming in to '/watched-it'
		e.g. www.flicklist.com/watched-it
	"""

	def renderError(self, error_code):
		self.error(error_code)
		self.response.write("Oops! Something went wrong.")


	def post(self):
		watched_movie_id = self.request.get("watched-movie")

		watched_movie = Movie.get_by_id( int(watched_movie_id) )

		# if we can't find the movie, reject.
		if not watched_movie:
			self.renderError(400)
			return

		# update the movie's ".watched" property to True
		watched_movie.watched = True
		watched_movie.put()

		# render confirmation page
		t = jinja_env.get_template("watched-it-confirmation.html")
		content = t.render(movie = watched_movie)
		self.response.write(content)


class MovieRatings(Handler):

	def get(self):
		watched_movies = db.GqlQuery("SELECT * FROM Movie where watched = True order by created desc")
		t = jinja_env.get_template("ratings.html")
		content = t.render(movies = watched_movies)
		self.response.write(content)

	def post(self):
		rating = self.request.get("rating")
		movie_id = self.request.get("movie")

		movie = Movie.get_by_id( int(movie_id) )

		if movie and rating:
			movie.rating = rating
			movie.put()

			# render confirmation
			t = jinja_env.get_template("rating-confirmation.html")
			content = t.render(movie = movie)
			self.response.write(content)
		else:
			self.renderError(400)
class Register(Handler):
	
	def verify_username(self, username):
		USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3-20}$")
		return username and USER_RE.match(username)
		
	def verify_password(self, password):
		USER_RE = re.compile(r"^.{3-20}$")
		return password and USER_RE.match(password)
			
	def passwords_match(self, password, verify):
		return password == verify
	
	
	def get(self):
		t = jinja_env.get_template("register.html")
		content = t.render(error = {})
		self.response.write(content)
	
	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		verify = self.request.get("verify")
		
		username_error = self.verify_username(username)
		password_error = self.verify_password(username)
		verify_error = self.passwords_match(password, verify)		
		username_taken = self.get_user_by_username(username)
		
		error = {}
		hasError = False
		
		if(username_taken):
			error['user_error'] = "That name is already taken"
		else:		
			#elif(username_error pr password_error or verify_error):
			if (not username_error):
				error['user_error'] = "Invalid username"
			if(not password_error):
				error['password_error'] = "Invalid password"
			if(verify_error):
				error['verify_error'] = "Passwords do not match"
		
		if(error):
			t = jinja_env.get_template("register.html")
			content = t.render(error = error)
			self.response.write(content)		
		else:
			new_user = User(username = username, password = password)
			new_user.put()
			self.redirect("/")


class Login(Handler):

	def get(self):
		t = jinja_env.get_template("login.html")
		content = t.render(error = {})
		self.response.write(content)
	
	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")		
		user = self.get_user_by_username(username)
		
		if (not user):
			t = jinja_env.get_template("login.html")
			content = t.render(user_error = "User does not exist")
			self.response.write(content)
		else:
			if (user.password != password):
				t = jinja_env.get_template("login.html")
				content = t.render(password_error = "Password is incorrect")
				self.response.write(content)
			else:
				self.redirect("/")
			

app = webapp2.WSGIApplication([
	('/', Index),
	('/add', AddMovie),
	('/watched-it', WatchedMovie),
	('/ratings', MovieRatings),
	('/register', Register)
], debug=True)
