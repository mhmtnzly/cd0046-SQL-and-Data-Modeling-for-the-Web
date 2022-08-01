#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from codecs import ignore_errors
from multiprocessing import synchronize
from re import A
from ssl import VerifyMode
from flask_migrate import Migrate
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import func
import datetime
from models import Venue, db, Artist, Show
import os
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# Suggestion of previous attempt
DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '1903')
DB_NAME = os.getenv('DB_NAME', 'example')

DB_PATH = 'postgresql://{}:{}@{}/{}'.format(
    DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = DB_PATH

# Migration
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):  # doesn't work
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


def format_datetime2(value, format='full'):
    if format == 'full':
        return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime('%A %B %d at %H:%M%p')


app.jinja_env.filters['datetime'] = format_datetime2
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    venues_areas = Venue.query.with_entities(
        Venue.city, Venue.state).group_by(Venue.city, Venue.state).order_by(Venue.state.asc(), Venue.city.asc()).all()
    for area in venues_areas:
        venue = Venue.query.with_entities(Venue.id, Venue.name).filter(
            Venue.city == area[0], Venue.state == area[1]).all()
        data_venue = []
        for v in venue:
            data_venue.append({
                "id": v[0],
                "name": v[1],
                "num_upcoming_shows": 0})
        data.append({"city": area[0],
                     "state": area[1],
                     "venues": data_venue})

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = '%'+str(request.form.get('search_term', '')) + '%'
    result = Venue.query.with_entities(Venue.id, Venue.name).filter(
        Venue.name.ilike(search_term)).all()
    data = []
    for res in result:
        data.append({
            "id": res[0],
            "name": res[1],
            "num_upcoming_shows": 0,
        })
    count = len(data)
    response = {
        "count": count,
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.filter(Venue.id == venue_id).first()
    shows = Show.query.join(Artist).filter(Artist.id ==
                                           Show.artist_id, Show.venue_id == venue_id).all()
    upcoming_shows = []
    past_shows = []
    now = datetime.datetime.now()
    for show in shows:
        artist = Artist.query.filter(Artist.id == show.artist_id).first()
        if show.start_time < now:
            past_shows.append({
                "venue_id": venue.id,
                "venue_name": venue.name,
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time)
            })
        else:
            upcoming_shows.append({
                "venue_id": venue.id,
                "venue_name": venue.name,
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time)
            })
    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website_link': venue.website_link,
        'facebook_link': venue.facebook_link,
        'seeking_description': venue.seeking_description,
        'seeking_talent': venue.seeking_talent,
        'image_link': venue.image_link,
        'upcoming_shows_count': len(upcoming_shows),
        'past_shows_count': len(past_shows),
        'upcoming_shows': upcoming_shows,
        'past_shows': past_shows
    }
    print(venue.genres[0])

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    try:
        form = VenueForm(request.form)
        data = Venue(name=form.name.data,
                     city=form.city.data,
                     state=form.state.data,
                     address=form.address.data,
                     phone=form.phone.data,
                     genres=form.genres.data[0],
                     image_link=form.image_link.data,
                     facebook_link=form.facebook_link.data,
                     website_link=form.website_link.data,
                     seeking_talent=True if form.seeking_talent.data else False,
                     seeking_description=form.seeking_description.data)
        db.session.add(data)
        
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    # on successful db insert, flash success
    if not error:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    else:
        flash('An error occurred. Venue ' +
              data.name + ' could not be listed.')
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        Venue.query.filter(Venue.id == venue_id).delete(
            synchronize_session=False)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if not error:
        flash('was successfully deleted!')
    else:
        flash('An error occurred.')
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.all()

    return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = '%'+str(request.form.get('search_term', '')) + '%'
    result = Artist.query.with_entities(Artist.id, Artist.name).filter(
        Artist.name.ilike(search_term)).all()
    data = []
    for res in result:
        data.append({
            "id": res[0],
            "name": res[1],
            "num_upcoming_shows": 0,
        })
    count = len(data)
    response = {
        "count": count,
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.filter(Artist.id == artist_id).first()
    shows = Show.query.filter(Show.artist_id == artist_id).all()
    upcoming_shows = []
    past_shows = []
    now = datetime.datetime.now()
    for show in shows:
        venue = Venue.query.filter(Venue.id == show.venue_id).first()
        if show.start_time < now:
            past_shows.append({
                "venue_id": venue.id,
                "venue_name": venue.name,
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time)
            })
        else:
            upcoming_shows.append({
                "venue_id": venue.id,
                "venue_name": venue.name,
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time)
            })
    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website_link': artist.website_link,
        'facebook_link': artist.facebook_link,
        'seeking_description': artist.seeking_description,
        'seeking_venue': artist.seeking_venue,
        'image_link': artist.image_link,
        'upcoming_shows_count': len(upcoming_shows),
        'past_shows_count': len(past_shows),
        'upcoming_shows': upcoming_shows,
        'past_shows': past_shows
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.filter(Artist.id == artist_id).first()
    form = ArtistForm(obj=artist)
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    artist = Artist.query.filter(Artist.id == artist_id)
    try:
        form = ArtistForm(request.form)
        artist.update({Artist.name: form.name.data,
                      Artist.city: form.city.data,
                      Artist.state: form.state.data,
                      Artist.phone: form.phone.data,
                      Artist.genres: form.genres.data[0],
                      Artist.image_link: form.image_link.data,
                      Artist.facebook_link: form.facebook_link.data,
                      Artist.website_link: form.website_link.data,
                      Artist.seeking_venue: True if form.seeking_venue.data else False,
                      Artist.seeking_description: form.seeking_description.data
                       })
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    # on successful db update, flash success
    if not error:
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    # on unsuccessful db update, flash an error instead.
    else:
        flash('An error occurred. Artist ' +
              artist.name + ' could not be updated.')
    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.filter(Venue.id == venue_id).first()
    form = VenueForm(obj=venue)
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.filter(Venue.id == venue_id)
    error = False
    try:
        form = VenueForm(request.form)
        venue.update({Venue.name: form.name.data,
                      Venue.city: form.city.data,
                      Venue.state: form.state.data,
                      Venue.address: form.address.data,
                      Venue.phone: form.phone.data,
                      Venue.genres: form.genres.data[0],
                      Venue.image_link: form.image_link.data,
                      Venue.facebook_link: form.facebook_link.data,
                      Venue.website_link: form.website_link.data,
                      Venue.seeking_talent: True if form.seeking_talent.data else False,
                      Venue.seeking_description: form.seeking_description.data
                      })
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if not error:
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    else:
        flash('An error occurred. Venue ' +
              venue.name + ' could not be updated.')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    try:
        form = ArtistForm(request.form)
        data = Artist(name=form.name.data,
                      city=form.city.data,
                      state=form.state.data,
                      phone=form.phone.data,
                      genres=form.genres.data[0],
                      image_link=form.image_link.data,
                      facebook_link=form.facebook_link.data,
                      website_link=form.website_link.data,
                      seeking_venue=True if form.seeking_venue.data else False,
                      seeking_description=form.seeking_description.data)
        db.session.add(data)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    # on successful db insert, flash success
    if not error:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    else:
        flash('An error occurred. Artist ' +
              data.name + ' could not be listed.')
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = []
    shows = Show.query.all()
    for show in shows:
        venue = Venue.query.filter(Venue.id == show.venue_id).first()
        artist = Artist.query.filter(Artist.id == show.artist_id).first()
        data.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        })
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error = False
    try:
        form = ShowForm(request.form)
        data = Show(artist_id=form.artist_id.data,
                    venue_id=form.venue_id.data,
                    start_time=form.start_time.data)
        db.session.add(data)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    # on successful db insert, flash success
    if not error:
        flash('Show was successfully listed!')
    else:
        flash('An error occurred. Show could not be listed.')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
