from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///top-10-movies.db"
db = SQLAlchemy(app)

class RateMovieForm(FlaskForm):
    rating = StringField(label="Your Rating out of 10",validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    done = SubmitField(label="Done")

class AddMovieForm(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    done = SubmitField(label="Add Movie")


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(200), nullable=False)
    img_url = db.Column(db.String(200), unique=True, nullable=False)

# db.create_all()

@app.route("/", methods=['GET','POST'])
def home():
    all_movies = Movies.query.order_by(Movies.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)

@app.route('/edit/<num>', methods=['GET','POST'])
def edit(num):
    edit_movie = Movies.query.get(num)
    form = RateMovieForm()
    if request.method == 'POST' and form.validate_on_submit():
        edit_movie.rating = request.form['rating']
        edit_movie.review = request.form['review']
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', movie=edit_movie, form=form )

@app.route('/delete')
def delete():
    del_id = request.args.get('num')
    del_movie = Movies.query.get(del_id)
    db.session.delete(del_movie)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add', methods=['GET','POST'])
def add():
    form = AddMovieForm()
    if form.validate_on_submit():
        param = {
            'api_key': 'YOUR_API',
            'query': request.form['title']
        }
        response = requests.get(url='https://api.themoviedb.org/3/search/movie', params=param).json()
        return render_template('select.html', results=response['results'])
    return render_template('add.html', form=form)

@app.route('/find')
def find():
    movie_id = request.args.get('id')
    response = requests.get(url=f'https://api.themoviedb.org/3/movie/{movie_id}',
                            params={'api_key': 'YOUR_API', }).json()
    print(response)
    new_movie = Movies(
        title=response['original_title'],
        year=response['release_date'][:4],
        description=response['overview'],
        rating=7.3,
        ranking=10,
        review="My favourite character was the caller.",
        img_url=f"https://image.tmdb.org/t/p/w500{response['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', num=new_movie.id))



if __name__ == '__main__':
    app.run(debug=True)
