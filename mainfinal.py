import webapp2, os, urllib2, urllib, json
import jinja2
import logging

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


### Utility functions you may want to use
def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


apikey = '5BRInQ6lktfdklvFQWYwehr5hTKgkezIS0nDxHRn'


def safeGet(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.HTTPError as e:
        logging.error("The server couldn't fulfill the request.")
        logging.error("Error code: ", e.code)
    except urllib2.URLError as e:
        logging.error("We failed to reach a server")
        logging.error("Reason: ", e.reason)
    return None


# "https://api.propublica.org/congress/v1/116/senate/members.json"
def memberAPI(baseurl='https://api.propublica.org/congress/v1/',
    congress='116',
    chamber='senate',
    ):
    url = baseurl + congress + '/' + chamber + '/members.json'
    req = urllib2.Request(url=url, headers={"X-API-Key": apikey})
    result = safeGet(req)
    if result is not None:
        data = json.load(result)
        return data


print(memberAPI())


def memberparse(dict):
    templatevals = {}
    for item in dict['results'][0]['members']:
        first = item['first_name']
        last = item['last_name']
        templatevals[first + ' ' + last] = {}
        templatevals[first + ' ' + last]['dob'] = item['date_of_birth']
        templatevals[first + ' ' + last]['gender'] = item['gender']
        templatevals[first + ' ' + last]['state'] = item['state']
        templatevals[first + ' ' + last]['rank'] = item['state_rank']
        templatevals[first + ' ' + last]['title'] = item['title']
        templatevals[first + ' ' + last]['vpresent'] = item['total_present']
        templatevals[first + ' ' + last]['total_votes'] = item['total_votes']
        templatevals[first + ' ' + last]['withparty_pct'] = item['votes_with_party_pct']
        templatevals[first + ' ' + last]['againstparty_pct'] = item['votes_against_party_pct']
        templatevals[first + ' ' + last]['party'] = item['party']
        templatevals[first + ' ' + last]['inoffice'] = item['in_office']
        templatevals[first + ' ' + last]['nextelection'] = item['next_election']
        templatevals[first + ' ' + last]['id'] = item['id']

    return templatevals


class Member():
    def __init__(self, item):
        self.name = item['first_name'] + ' ' + item['last_name']
        self.dob = item['date_of_birth']
        self.gender = item['gender']
        self.state = item['state']
        self.rank = item['state_rank']
        self.title = item['title']
        self.vpresent = item['total_present']
        self.totalvotes = item['total_votes']
        self.withparty_pct = item['votes_with_party_pct']
        self.againstparty_pct = item['votes_against_party_pct']
        self.party = item['party']
        self.inoffice = item['in_office']
        self.nextelection = item['next_election']
        self.id = item['id']


# list = memberAPI()
# memberdict = memberparse(list)
# print(memberdict)

# print(pretty(list['results'][0]['members']))


class MainHandler(webapp2.RequestHandler):
    def genpage(self, member= None):
        templatevals = {}
        if member is not None:
           pass
        else:
            list = memberAPI()
            # memberobject = [Member(item) for item in list[0][0]['members']]
            templatevals['members'] = memberparse(list)
            templatevals['title'] = 'Search Results'
            templatevals['membernum'] = list['results'][0]['num_results']

        template = JINJA_ENVIRONMENT.get_template('finaltemplate.html')
        self.response.write(template.render(templatevals))

    def get(self):
        self.genpage()

    def post(self):
        member = self.request.get('member')
        self.genpage(member)
        # congress = self.request.get('congress')
        # self.genpage(congress)
        # chamber = self.request.get('chamber')
        # self.genpage(chamber)


application = webapp2.WSGIApplication([('/', MainHandler)], debug=True)