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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
#################################################
#         Vacation weather API
# Home page.
# List all routes that are available.
# /api/v1.0/precipitation
# Convert the query results to a Dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
# /api/v1.0/tobs
# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.
# /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Vacation weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation as json"""
    session = Session(engine)
    
    max_date = session.query(func.max(Measurement.date)).all()
    date_end = dt.datetime.strptime(max_date[0][0], '%Y-%m-%d')
    delta = dt.timedelta(days=365)
    date_start = date_end - delta
    start = date_start.strftime('%Y-%m-%d')
                             
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date>=start).all()
    # Create a dictionary from the row data and append to a list
    precipitations = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["value"] = prcp
        precipitations.append(prcp_dict)
    
    return jsonify(precipitations)

@app.route("/api/v1.0/stations")
def stations():
    """Return the stations list as json"""
    session = Session(engine)
    results = session.query(Station.station).all()
    # Convert list of tuples into normal list
    stations = list(np.ravel(results))
                             
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the list of Temperature Observations (tobs) for the previous year"""
    # query for the dates and temperature observations from a year from the last data point
    session = Session(engine)
        
    max_date = session.query(func.max(Measurement.date)).all()
    date_end = dt.datetime.strptime(max_date[0][0], '%Y-%m-%d')
    delta = dt.timedelta(days=365)
    date_start = date_end - delta
    start = date_start.strftime('%Y-%m-%d')
                                                          
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date>=start).all()
    temperature = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        temperature.append(tobs_dict)
                             
    return jsonify(temperature)

@app.route("/api/v1.0/<start_date>")
def daily_temp(start_date):
    """TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
                             
    return jsonify(session.query(*sel).filter(Measurement.date >= start_date).all())

@app.route("/api/v1.0/<start_date>/<end_date>")
def daily_temp_1(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        end   (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)] 
    
    return jsonify(session.query(*sel).filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all())


if __name__ == "__main__":
    app.run(debug=True)

