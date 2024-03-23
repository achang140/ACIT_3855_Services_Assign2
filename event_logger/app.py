import connexion 
from connexion import FlaskApp
from flask_cors import CORS, cross_origin

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from base import Base
from event_stats import EventStats

import yaml 
import logging
import logging.config
import requests
import datetime
import pytz
from pytz import utc 
from pytz import timezone

from apscheduler.schedulers.background import BackgroundScheduler


with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

# Connect to the database (db name: event_stats.sqlite)
DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_event_stats():
    """ Gets Hotel Room and Hotel Activity processsed statistics """

    # Log an INFO message indicating request has started
    logger.info("Request Started")

    # Read in the current statistics from the SQLite database (i.e., the row with the most recent last_update datetime stamp.
    session = DB_SESSION() 

    stats = session.query(EventStats).order_by(EventStats.last_updated.desc()).first() 

    # If no stats exist, log an ERROR message and return 404 and the message “Statistics do not exist” OR return empty/default statistics
    if stats is None:
        logger.error("Statistics do not exist")
        return "Statistics do not exist", 404

    vancouver_timezone = timezone('America/Vancouver')
    last_updated_vancouver = stats.last_updated.astimezone(vancouver_timezone)

    # Convert them as necessary into a new Python dictionary such that the structure matches that of your response defined in the openapi.yaml file.
    statistics = {
        "num_hotel_room_reservations": stats.num_hotel_room_reservations,
        "max_hotel_room_ppl": stats.max_hotel_room_ppl,
        "num_hotel_activity_reservations": stats.num_hotel_activity_reservations,
        "max_hotel_activity_ppl": stats.max_hotel_activity_ppl,
        "last_updated": last_updated_vancouver.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    }

    # "last_updated": stats.last_updated 

    # Log a DEBUG message with the contents of the Python Dictionary
    logger.debug(statistics)

    # Log an INFO message indicating request has completed
    logger.info("Request Completed!")

    session.close() 

    # Return the Python dictionary as the context and 200 as the response code
    return statistics, 200 

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True) 

CORS(app.app)
app.app.config["CORS_HEADERS"] = "Content-Type"




def init_scheduler():
    # sched = BackgroundScheduler(daemon=True, timezone=utc)
    sched = BackgroundScheduler(daemon=True, timezone=timezone('America/Vancouver'))
    sched.add_job(populate_stats, 
                  'interval',
                   seconds=app_config['scheduler']['period_sec'])
    sched.start()



app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True) 

CORS(app.app)
app.app.config["CORS_HEADERS"] = "Content-Type"



if __name__ == "__main__":
    init_scheduler()
    app.run(host="0.0.0.0", port=8100)