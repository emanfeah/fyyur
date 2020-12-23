# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import sys

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from sqlalchemy import func
from models import *
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    all_areas = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
    data = []

    for area in all_areas:
        area_venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
        venue_data = []
        for venue in area_venues:
            venue_data.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(
                    db.session.query(Show).filter(Show.venue_id == 1).filter(Show.start_time > datetime.now()).all())
            })
        data.append({
            "city": area.city,
            "state": area.state,
            "venues": venue_data
        })

    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term')
    search_results = Venue.query.filter(
        Venue.name.ilike(
            '%{}%'.format(search_term))).all()

    response = {}
    response['count'] = len(search_results)
    response['data'] = search_results

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)

    if not venue:
        return render_template('errors/404.html')

    upcoming_shows_query = Show.query.filter(Show.venue_id == venue_id).filter(
        Show.start_time > datetime.now()).all()

    past_shows_query = Show.query.filter(Show.venue_id == venue_id).filter(
        Show.start_time < datetime.now()).all()
    data = {
        'venue': venue,
        'past_shows': past_shows_query,
        'upcoming_shows': upcoming_shows_query,
        'past_shows_count': len(past_shows_query),
        'upcoming_shows_count': len(upcoming_shows_query),
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    form = VenueForm(request.form)
    if form.validate():
        try:
            venue = Venue()
            venue.name = request.form['name']
            venue.city = request.form['city']
            venue.state = request.form['state']
            venue.address = request.form['address']
            venue.phone = request.form['phone']
            venue.genres = request.form.getlist('genres')
            venue.facebook_link = request.form['facebook_link']
            venue.image_link = request.form['image_link']
            venue.facebook_link = request.form['facebook_link']
            venue.seeking_description = request.form['seeking_description']
            venue.seeking_talent = True if request.form.get(
                'seeking_talent') in ('y', True) else False
            venue.website_link = request.form['website_link']
            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        flash(form.errors)
        flash('An error occured. Venue ' + request.form['name'] + ' Could not be listed!')

    return render_template('pages/home.html')


# delete venues
@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
    error = False
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be deleted ')
    finally:
        db.session.close()
    return render_template("pages/home.html")


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term')
    search_results = Artist.query.filter(
        Artist.name.ilike(
            '%{}%'.format(search_term))).all()

    response = {}
    response['count'] = len(search_results)
    response['data'] = search_results

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)

    if not artist:
        return render_template('errors/404.html')

    upcoming_shows_query = Show.query.filter(Show.artist_id == artist_id).filter(
        Show.start_time > datetime.now()).all()

    past_shows_query = Show.query.filter(Show.artist_id == artist_id).filter(
        Show.start_time < datetime.now()).all()
    data = {
        'artist': artist,
        'past_shows': past_shows_query,
        'upcoming_shows': upcoming_shows_query,
        'past_shows_count': len(past_shows_query),
        'upcoming_shows_count': len(upcoming_shows_query),
    }
    print(data['upcoming_shows_count'])
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)

    error = False
    try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.facebook_link = request.form['facebook_link']
        artist.image_link = request.form['image_link']
        db.session.add(artist)
        db.session.commit()
        flash('An successfully occurred.artist ' + artist.name)
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. artist ' + artist.name + ' could not be updated.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


# delete artist
@app.route('/artists/<artists_id>', methods=['POST'])
def delete_artist(artists_id):
    error = False
    try:
        Artist.query.filter_by(id=artists_id).delete()

        flash('Done deleted')
        db.session.commit()
    except:
        db.session.rollback()
        flash('An error occurred. artist ' + request.form['name'] + ' could not be deleted ')
    finally:
        db.session.close()
    return redirect(url_for('index'))


# edit venues
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)

    error = False
    try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.facebook_link = request.form['facebook_link']
        venue.image_link = request.form['image_link']
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be updated.')
        else:
            flash('Venue ' + request.form['name'] +
                  ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist done
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    form = ArtistForm(request.form)
    if form.validate():
        try:
            artist = Artist()
            artist.name = request.form['name']
            artist.city = request.form['city']
            artist.state = request.form['state']
            artist.phone = request.form['phone']
            artist.genres = request.form.getlist('genres')
            artist.facebook_link = request.form['facebook_link']
            artist.image_link = request.form['image_link']

            db.session.add(artist)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

    else:
        flash(form.errors)
    flash('Artist ' + request.form['name'] +
          ' was successfully listed!')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = Show.query.all()
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
        flash('Show is successfully ')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
