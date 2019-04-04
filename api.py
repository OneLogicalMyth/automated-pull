from flask import Flask, abort, request, jsonify
from os.path import abspath, exists
from blacklist import blacklist
from database import database
from slack import slack
import sys, json, hashlib

f_config = abspath("config.json")
bl = blacklist()

# check if the config.json file is present
if not exists(f_config):
    print "config.json not found"
    sys.exit()

# first load the configuration
with open(f_config, 'r') as json_data:
    config = json.load(json_data)

# check database tables
db = database()
db.setup()
db.close()

# set vars based on config file
SERVER_NAME = config.get('server','Automated Pull API Beta')
SECRET = 'sha1=' + hashlib.sha1(config.get('secret','some-random-token-string')).hexdigest()
SLACK_WEBHOOK = config.get('slack_webhook',None)
BLACKLIST_TIMEOUT = int(config.get('blacklist_expiry_mins',60))

print ' * API starting'
print ' * Access token is ' + CONFIG_TOKEN
if SLACK_WEBHOOK:
    print 'Slack notifications enabled ' + SLACK_WEBHOOK
    s = slack(SLACK_WEBHOOK)

# start the application
app = Flask(__name__)

# perform so sanity checks before proceeding
@app.before_request
def run_prereq_tasks():

    # check if IP is black listed
    blacklisted = bl.check(request.remote_addr,BLACKLIST_TIMEOUT)
    if blacklisted:
        abort(403,description="You have been blacklisted")

    # this API only supports POST
    if not request.method == 'POST':
        abort(404)

    # this API only supports JSON
    if not request.is_json:
        abort(404)

    # this API expects data
    if not request.data:
        abort(404)

    # validate the token before any requests
    data = request.get_json(silent=True)
    req_secret = request.headers.get('X-Hub-Signature')

    # if token is an empty string or does not match return 403
    if not req_secret or not req_secret == SECRET:
        bl.add(request.remote_addr)
        if SLACK_WEBHOOK:
            s.send_message('The IP ' + request.remote_addr + ' has been blacklisted due to an incorrect token.')
        abort(403,description="Token is not valid")

# accept a POST request to /push
@app.route('/push',methods=['POST'])
def push():

    # send slack messaage
    if SLACK_WEBHOOK:
        s.send_message('A valid push request was sent by GitHub.')

    # return the result
    out = 'OK'
    return out, 200
