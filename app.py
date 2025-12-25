from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/restaurant")
def restaurant():
    return render_template("restaurant.html")

@app.route("/resort")
def resort():
    return render_template("resort.html")

if __name__ == "__main__":
    app.run(debug=True)
    
@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/table-booking")
def table_booking():
    return render_template("table_booking.html")

@app.route("/rooms")
def rooms():
    return render_template("rooms.html")

@app.route("/room-booking")
def room_booking():
    return render_template("room_booking.html")
