#!/usr/bin/env python

"""
Self contained script which listens for commands on the queue, executes
them locally and then sends an http request back to the webhook url
with the results.
"""

# standard library
import sys
import commands

# external
import httplib2
from django.utils import simplejson
from amqplib import client_0_8 as amqp

# devine the location of your message queue
QUEUE_ADDRESS = '172.16.142.128'

def recv_callback(msg):
    "Callback function each time a message is recieved"
    # get the JSON document from the message body
    obj = simplejson.loads(msg.body)

    # run the specified command
    code, output = commands.getstatusoutput(obj['command'])

    # send post request to obj['webhook']
    # containing the following data
    pre_json = {"status": code,"output": output}

    # convert to json
    json = simplejson.dumps(pre_json)

    # setup the http client
    h = httplib2.Http()
    # make a post request
    resp, content = h.request(
        obj['webhook'],
        "POST", body=json,
        headers={'content-type':'application/json'}
    )

def run(host, queue, exchange, key):
    "Long running message queue processor"

    # we define a tag based on the queue name
    tag = "%s_tag" % queue

    # set up a connection to the server
    conn = amqp.Connection(host)
    # and get a channel
    chan = conn.channel()

    # define your queue and exchange
    # if they already exist then we check they are of the correct type
    chan.exchange_declare(exchange=exchange, type="direct", 
    durable=False, auto_delete=True)
    # for our purposes queues want to be unique between implementations
    # and exchanges are defined by the paperboy service
    chan.queue_declare(queue=queue, durable=False, 
                       exclusive=False, auto_delete=True)

    # and wire the queue and exchange together
    chan.queue_bind(queue=queue, exchange=exchange, routing_key=key)

    # register our callback function for when we see something on the queue
    chan.basic_consume(queue=queue, no_ack=True, 
                       callback=recv_callback, consumer_tag=tag)

    # set the script to be long running
    try:
        while True:
            chan.wait()
    except KeyboardInterrupt:
        # if we do exit then tell the server
        chan.basic_cancel(tag)

        # and close everything
        chan.close()
        conn.close()

        sys.exit()

if __name__ == '__main__':
    run(
        host = QUEUE_ADDRESS,
        queue = "asteroid_queue",
        exchange = "asteroid",
        key = "all",
    )