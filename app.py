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

# Save reference to the table
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
        f"Welcome to the Hawaii Weather Data!<br/>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>Precipitation data for the last year</a><br/>"
        f"<a href='/api/v1.0/stations'> List of stations </a><br/>"
        f"<a href='/api/v1.0/tobs'> Temperature observations of the most active station for the last year of data. </a><br/>"
        f"<a href='/api/v1.0/start'> Temperature for greater than and equal to the start date.</a><br/>"
        f"<a href='/api/v1.0/start/end'> Temperature for dates between the start and end date inclusive.</a><br/>"
       
    )

@app.route("/api/v1.0/precipitation")   
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Convert string of date to datetime
    s_last_date = dt.datetime.strptime(last_date[0], "%Y-%m-%d").date()

    # Find one year prior
    year_ago = s_last_date - dt.timedelta(days=365)

   # Perform a query to retrieve the data and precipitation score
    prcp_results = session.query(Measurement.date, Measurement.prcp)\
                .filter(Measurement.date >= year_ago).all()            

    
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_prcp = []
    for date, prcp in prcp_results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)
    
   



@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of each stations"""
    station_results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station_results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
   # Create our session (link) from Python to the DB
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Convert string of date to datetime
    s_last_date = dt.datetime.strptime(last_date[0], "%Y-%m-%d").date()

    # Find one year prior
    year_ago = s_last_date - dt.timedelta(days=365)

    """Query the dates and temperature observations of the most active station for the last year of data. """
    most_active_station = session.query(Measurement.station,func.count(Measurement.station))\
                    .filter(Measurement.date >= year_ago)\
                    .group_by(Measurement.station)\
                    .order_by(func.count(Measurement.station).desc()).all()

    active_station_tobs = session.query(Measurement.station, Measurement.tobs)\
                            .filter(Measurement.station == most_active_station[0][0]).all()

    session.close() 

     
    # Convert list of tuples into normal list
    all_tobs = list(np.ravel(active_station_tobs))
    
    

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def tobs_start(start):
    # Create our session (link) from Python to the DB

    session = Session(engine)

    start_tobs = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
                           .filter(Measurement.date >= start).all()
    
    session.close() 

    # Convert list of tuples into normal list
    all_start = list(np.ravel(start_tobs))

    return jsonify(all_start)

@app.route("/api/v1.0/<start>/<end>")
def tobs_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    end_tobs = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
                           .filter(Measurement.date >= start)\
                            .filter(Measurement.date <= end).all()   
    
    session.close() 

    # Convert list of tuples into normal list
    all_end = list(np.ravel(end_tobs))

    return jsonify(all_end)   

if __name__ == '__main__':
    app.run(debug=True)
