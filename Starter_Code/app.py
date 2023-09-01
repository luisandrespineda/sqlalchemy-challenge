# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify




#################################################
# Database Setup
#################################################

#Generating and connecting to the sql database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()


# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
print(Base.classes.keys())


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
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    last_date=session.query(func.max(measurement.date)).scalar()
    # Calculate the date one year from the last date in data set.
    one_yr_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
    results = session.query(measurement.date,measurement.prcp).filter(measurement.date <= last_date).filter(measurement.date >= one_yr_date).all()

    session.close()

    prcp_results = []
    for prcp, date in results:
        prcp_dict = {}
        prcp_dict["precipitation"] = prcp
        prcp_dict["date"] = date
        prcp_results.append(prcp_dict)

    return jsonify(prcp_results)

@app.route("/api/v1.0/stations", endpoint="stations")
def stations_results():
    session = Session(engine)

    station_qry = session.query(stations.station).all()
    
    session.close()
  
    stn_results = []
    for station in station_qry:
        stn_dict = {}
        stn_dict["station"] = station._asdict()['station']
        stn_results.append(stn_dict)

    return jsonify(stn_results)

@app.route("/api/v1.0/tobs", endpoint="tobs")
def temp_results():
    session = Session(engine)
    
    last_date=session.query(func.max(measurement.date)).scalar()
    one_yr_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    active_station = session.query(measurement.tobs,measurement.date).filter(measurement.station == 'USC00519281').\
    filter(measurement.date <= last_date).filter(measurement.date >= one_yr_date).all()

    session.close()
    
    temp_res = []
    for tobs, date in active_station:
        temp_dict = {}
        temp_dict["temp"] = tobs
        temp_dict["date"] = date
        temp_res.append(temp_dict)

    return jsonify(temp_res)    

@app.route("/api/v1.0/<date>", endpoint="data_by_date")
def data_by_date(date):
    session = Session(engine)
    
    date_obj = dt.datetime.strptime(date, "%Y-%m-%d")

    date_query = session.query(
    func.min(measurement.tobs).label("min_temp"),
    func.max(measurement.tobs).label("max_temp"),
    func.avg(measurement.tobs).label("avg_temp")
    ).filter(measurement.date > date_obj).all()


    session.close()

    date_results = {}
    for date_measurement in date_query:
        date_results["min_temperature"] = date_measurement._asdict()["min_temp"]
        date_results["max_temperature"] = date_measurement._asdict()["max_temp"]
        date_results["avg_temperature"] = date_measurement._asdict()["avg_temp"]

    return jsonify(date_results)


@app.route("/api/v1.0/<start_date>/<end_date>", endpoint="date_range")
def date_range(start_date,end_date):
    
    start_date_obj = dt.datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = dt.datetime.strptime(end_date, "%Y-%m-%d")

    session = Session(engine)

    results = session.query(
    func.min(measurement.tobs).label("range_min_temp"),
    func.max(measurement.tobs).label("range_max_temp"),
    func.avg(measurement.tobs).label("range_avg_temp")
    ).filter(measurement.date > start_date_obj).filter(measurement.date < end_date_obj).all()


    session.close()

    range_data_results = {}
    for range_min_temp, range_max_temp, range_avg_temp in results:
        range_data_results["min_temperature"] = range_min_temp
        range_data_results["max_temperature"] = range_max_temp
        range_data_results["avg_temperature"] = range_avg_temp

    return jsonify(range_data_results)


if __name__ == '__main__':
    app.run(debug=True)

