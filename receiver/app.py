import connexion 
from connexion import NoContent 
# import requests
import yaml 
import time 
import logging
import logging.config
import uuid
import datetime
import json
from pykafka import KafkaClient

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

current_retry = 0
max_retries = app_config["events"]["max_retries"]

while current_retry < max_retries:
    try:
        logger.info(f"Trying to connect to Kafka. Current retry count: {current_retry}")
        client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
        # topic = client.topics[str.encode(app_config["events"]["topic"])]
        # producer = first_topic.get_sync_producer()

        # First Topic events 
        first_topic = client.topics[str.encode(app_config["events"]["topics"][0])]
        first_producer = first_topic.get_sync_producer()

        # Second Topic event_log 
        second_topic = client.topics[str.encode(app_config["events"]["topics"][1])]
        second_producer = second_topic.get_sync_producer()

        break 

    except:
        logger.error("Connection failed.")
        time.sleep(app_config["events"]["sleep_time"])
        current_retry += 1

def book_hotel_room(body):
    """ Receives a hotel room booking event """

    trace_id = uuid.uuid4()
    body["trace_id"] = str(trace_id)

    logger.info("Received event Hotel Room Booking request with a trace id of %s", body["trace_id"])

    # headers = { "content-type": "application/json" }
    # response = requests.post(app_config["eventstore1"]["url"], json=body, headers=headers) # requests.post(url=event_one_url, json=body, headers=headers)
    # logger.info(f"Returned event Hotel Room Booking response (Id: ${body['trace_id']}) with status ${response.status_code}")
    
    # client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    # topic = client.topics[str.encode(app_config["events"]["topic"])]
    # producer = topic.get_sync_producer()
    msg = {
        "type": "hotel_room",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    # producer.produce(msg_str.encode('utf-8'))
    first_producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Returned event Hotel Room Booking response (Id: ${body['trace_id']}) with status 201")

    # return NoContent, response.status_code
    return NoContent, 201

def book_hotel_activity(body):
    """ Receives a hotel activity reservation event """

    trace_id = uuid.uuid4()
    body["trace_id"] = str(trace_id)


    logger.info("Received event Hotel Activity Booking request with a trace id of %s", body["trace_id"])

    # headers = { "content-type": "application/json" }
    # response = requests.post(app_config["eventstore2"]["url"], json=body, headers=headers) # requests.post(url=event_two_url, json=body, headers=headers)
    # logger.info("Returned event Hotel Activity Booking response (Id: %s) with status %d", body["trace_id"], response.status_code)

    # client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    # topic = client.topics[str.encode(app_config["events"]["topic"])]
    # producer = topic.get_sync_producer()
    msg = {
        "type": "hotel_activity",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    # producer.produce(msg_str.encode('utf-8'))
    first_producer.produce(msg_str.encode('utf-8'))

    logger.info("Returned event Hotel Activity Booking response (Id: %s) with status %d", body["trace_id"], 201)

    # return NoContent, response.status_code
    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", 
            strict_validation=True, 
            validate_responses=True) 

if __name__ == "__main__":
    app.run(port=8080)

