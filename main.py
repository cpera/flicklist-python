import webapp2
import random

class Index(webapp2.RequestHandler):

    def getRandomMovie(self):

        # TODO: make a list with at least 5 movie titles
		 mvList = ["God Father", "Titanic", "Legend", "Avatar", "2012"]		
        # TODO: randomly choose one of the movies, and return it
		 randVal =random.randrange(0,len(mvList))
		 randomMvPick = mvList[randVal]
		 return randomMvPick # "The Big Lebowski"

    def get(self):
        # choose a movie by invoking our new function 
		movie = self.getRandomMovie() 
		tomorrow_movie = self.getRandomMovie() 
		# build the response string 
		content = "<h1>Movie of the Day</h1>" 
		content += "<p>" + movie + "</p>" 
		# TODO: pick a different random movie, and display it under
		content += "<h1>Movie for tomorrow's movie: </h1>"
		content += "<p>" + tomorrow_movie + "</p>"
		self.response.write(content)
        

app = webapp2.WSGIApplication([
    ('/', Index)
], debug=True)
