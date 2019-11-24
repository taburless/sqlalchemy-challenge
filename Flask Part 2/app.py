import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"Precipitation Numbers: "
        f"/api/v1.0/precipitation<br/>"
        f"Stations: "
        f"/api/v1.0/stations<br/>"
        f"Temperatures by Date: "
        f"/api/v1.0/tobs<br/>"
        f"User enters start date to return Temperatures: "
        f"/api/v1.0/<start><br/>"
        f"<br/>"
        f"<strong>Please enter start date on left side of last backslash and end date on the right side.</strong>"
        f"<br/>"
        f"User enters start and end date to return Temperatures: "
        f"/api/v1.0/<start>/<end><br/>"
        
    )


@app.route("/api/v1.0/precipitation")
def prcp_by_date():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all dates and precipitation amounts
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create dictionary and append it to a list of precipitation
    weather_list = []
    for date, prcp in results:
        weather_dict = {}
        weather_dict["date"] = date
        weather_dict["prcp"] = prcp
        weather_list.append(weather_dict)

    return jsonify(weather_list)

@app.route("/api/v1.0/stations")
def stations_data():
    session = Session(engine)

    results = session.query(Station.station).all()
    session.close()

    station_list = []
    for stat in results:
        station_dict = {}
        station_dict["station"] = stat
        station_list.append(station_dict)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs_data():
    session = Session(engine)
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= prev_year).all()
    session.close()

    tobs_list = []

    for date, tob in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tob
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_numbers(start):
    session = Session(engine)
    temp_year_start = dt.datetime.strptime(start, "%Y-%m-%d")
    temp_year_last = dt.timedelta(days=365)
    start = temp_year_start - temp_year_last
    end_date = dt.datetime(2017,8,23)

    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end_date).all()

    session.close()

    temp_list = list(np.ravel(temp_data))
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_numbers_start_end(start, end):
    session = Session(engine)
    temp_year_start = dt.datetime.strptime(start, "%Y-%m-%d")
    temp_year_end = dt.datetime.strptime(end, "%Y-%m-%d")
    temp_year_last = dt.timedelta(days=365)
    start = temp_year_start - temp_year_last
    end = temp_year_end - temp_year_last

    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    temp_list = list(np.ravel(temp_data))
    return jsonify(temp_list)


if __name__ == '__main__':
    app.run(debug=True)
