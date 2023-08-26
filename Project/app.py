from flask import Flask, render_template, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import webview

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(basedir, "data.sqlite")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "shopping_calculator"
window = webview.create_window("Shopping Calculator", app)


db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Shopping(db.Model):
    __tablename__ = "shopping"
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float)

    def __init__(self, total):
        self.total = total


class ShoppingForm(FlaskForm):
    num_input = FloatField("", render_kw={"autofocus": True})
    submit = SubmitField("Calculate")


class DeleteForm(FlaskForm):
    del_btn = SubmitField("Clear All")


app.app_context().push()
db.create_all()


@app.route("/", methods=["GET", "POST"])
def index():
    form = ShoppingForm()
    del_form = DeleteForm()
    total_price = ""
    lst = ""

    if form.validate_on_submit():
        prices = form.num_input.data
        add_numbers = Shopping(total=prices)
        db.session.add(add_numbers)
        db.session.commit()

        total_price = db.session.execute(db.select(Shopping)).scalars()
        data = [x.total for x in total_price]
        lst = sum(data)
        session["lst"] = lst
        return redirect(url_for("index"))
    return render_template("index.html", form=form, del_form=del_form)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    delete_all_data = db.session.execute(db.select(Shopping)).scalars()
    for data in delete_all_data:
        db.session.delete(data)
    db.session.commit()
    total_price = db.session.execute(db.select(Shopping)).scalars()
    data = [x.total for x in total_price]
    lst = sum(data)
    session["lst"] = lst
    return redirect(url_for("index"))


if __name__ == "__main__":
    # app.run(debug=True)
    webview.start()
