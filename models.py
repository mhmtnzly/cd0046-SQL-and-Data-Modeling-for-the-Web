from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(30))  # genres
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))  # website link
    seeking_talent = db.Column(
        db.Boolean, nullable=False, default=False)  # looking for talent
    seeking_description = db.Column(db.String(120))  # seeking description
    shows = db.relationship('Show', backref='Venue',
                            lazy=True, cascade='all, delete')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def __repr__(self):
        return f'<Venue ID: {self.id}, Venue name: {self.name}'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))  # website link
    seeking_venue = db.Column(
        db.Boolean, nullable=False, default=False)  # looking for venues
    seeking_description = db.Column(db.String(120))  # seeking description
    shows = db.relationship('Show', backref='Artist',
                            lazy=True, cascade='all, delete')

    def __repr__(self):
        return f'<Venue ID: {self.id}, Artist name: {self.name}'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show ID: {self.id}, Artist ID:{self.artist_id}, Venue ID: {self.venue_id}'
