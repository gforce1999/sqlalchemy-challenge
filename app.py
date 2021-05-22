import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a dictionary using date as the key and prcp as the value."""
    # Query 
    # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_ago).\
    filter(Measurement.date<= dt.date(2017,8,23)).all()

    session.close()

    # Convert list of tuples into normal list
    results_lst = list(np.ravel(results))
    
    #Convert list to dictionary
    res_dct = {results_lst[i]: results_lst[i + 1] for i in range(0, len(results_lst), 2)}

    return jsonify(res_dct)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query 
    results = session.query(Measurement.station).\
    group_by(Measurement.station).\
    order_by((Measurement.station).desc()).all() 
    #results = session.query(Station.station)

    session.close()

    # Convert list of tuples into normal list
    results_lst = list(np.ravel(results))

    return jsonify(results_lst)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature observations of the most active station for the last year of data."""
    # Query 

   # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs).\
    filter(Measurement.station=='USC00519281').\
    filter(Measurement.date >= year_ago).\
    filter(Measurement.date<= dt.date(2017,8,23)).all()

    session.close()

    # Convert list of tuples into normal list
    results_lst = list(np.ravel(results))

    #Convert list to dictionary
    res_dct = {results_lst[i]: results_lst[i + 1] for i in range(0, len(results_lst), 2)}

    return jsonify(results_lst)

@app.route("/api/v1.0/<start>")
def startdate(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, 
       the average temperature, and the max temperature 
       for a given start or start-end range"""
    # Query 

    # Get the start date 
    start_date = dt.datetime.strptime(start,"%Y-%m-%d")

    # Query- calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
    
    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()

    # Convert list of tuples into normal list
    results_lst = list(np.ravel(results))

    #Convert list to dictionary
    #res_dct = {results_lst[i]: results_lst[i + 1] for i in range(0, len(results_lst), 2)}

    return jsonify(results_lst)
    
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, 
       the average temperature, and the max temperature 
       for a given start or start-end range"""
    # Query 

    # Get the start date 
    start_date = dt.datetime.strptime(start,"%Y-%m-%d")

    # Get the end date 
    end_date = dt.datetime.strptime(end,"%Y-%m-%d")

    # Query- calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive. 
    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()

    session.close()

    # Convert list of tuples into normal list
    results_lst = list(np.ravel(results))

    #Convert list to dictionary
    #res_dct = {results_lst[i]: results_lst[i + 1] for i in range(0, len(results_lst), 2)}

    return jsonify(results_lst)    

if __name__ == '__main__':
    app.run(debug=True)
