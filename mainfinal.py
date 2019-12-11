import webapp2, os, urllib2, urllib, json
import jinja2
import logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

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


# "https://api.propublica.org/congress/v1/members/K000388.json"
def searchMember(memberid, baseurl='https://api.propublica.org/congress/v1/'):
    url = baseurl + '/members/' + str(memberid) + '.json'
    req = urllib2.Request(url=url, headers={"X-API-Key": apikey})
    result = safeGet(req)
    if result is not None:
        data = json.load(result)
        return data


#   https://api.propublica.org/congress/v1/members/{first-member-id}/votes/{second-member-id}/{congress}/{chamber}.json
def compareMembers(mem1, mem2, baseurl='https://api.propublica.org/congress/v1/members/'):
    url = baseurl + mem1 + '/votes/' + mem2 + '/116/senate'
    req = urllib2.Request(url=url, headers={"X-API-Key": apikey})
    result = safeGet(req)
    if result is not None:
        data = json.load(result)
        return data


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


def specificparse(dictionary, id):
    templatevals = {}
    for item in dictionary['results']:
        first = item['first_name']
        last = item['last_name']
        templatevals[first + ' ' + last] = {}
        templatevals[first + ' ' + last]['id'] = id
        templatevals[first + ' ' + last]['dob'] = item['date_of_birth']
        templatevals[first + ' ' + last]['gender'] = item['gender']
        templatevals[first + ' ' + last]['inoffice'] = item['in_office']
        templatevals[first + ' ' + last]['party'] = item['current_party']
        templatevals[first + ' ' + last]['congress'] = item['roles'][0]['congress']
    return templatevals

def compareparse(dictionary, mem1, mem2):
    data = {}
    logging.warning(dictionary)
    data['firstmem'] = mem1
    data['secondmem'] = mem2
    data['commonvotes'] = dictionary['results'][0]['common_votes']
    data['disagree'] = dictionary['results'][0]['disagree_votes']
    data['agree_pct'] = dictionary['results'][0]['agree_percent']
    data['disagree_pct'] = dictionary['results'][0]['disagree_percent']
    logging.warning(data)
    return data
#
# class Member():
#     def __init__(self, item):
#         self.name = item['first_name'] + ' ' + item['last_name']
#         self.dob = item['date_of_birth']
#         self.gender = item['gender']
#         self.state = item['state']
#         self.rank = item['state_rank']
#         self.title = item['title']
#         self.vpresent = item['total_present']
#         self.totalvotes = item['total_votes']
#         self.withparty_pct = item['votes_with_party_pct']
#         self.againstparty_pct = item['votes_against_party_pct']
#         self.party = item['party']
#         self.inoffice = item['in_office']
#         self.nextelection = item['next_election']
#         self.id = item['id']


def findID(member):
    list = memberAPI()
    members = memberparse(list)
    memberid = None
    splitit = member.split()
    mfirst = splitit[0]
    mlast = splitit[1]
    logging.warning(mfirst)
    for item in members:
        split = item.split()
        firstname = split[0]
        lastname = split[1]
        if firstname == mfirst and lastname == mlast:
            memberid = members[item]['id']
            return memberid
    return memberid



class MainHandler(webapp2.RequestHandler):
    def genpage(self, member=None):
        templatevals = {}
        if member is not None:
            id = findID(member)
            if id is not None:
                currmemid = id
                data = searchMember(id)
                findata = specificparse(data, id)
                templatevals['member'] = member
                templatevals['data'] = findata
                templatevals['title1'] = 'Search Results'
                templatevals['message'] = 'Here is what we found'
            else:
                templatevals['message'] = 'Please enter a valid member'
        else:
            list = memberAPI()
            templatevals['members'] = memberparse(list)
            templatevals['membernum'] = list['results'][0]['num_results']
            templatevals['title1'] = 'Members of Congress'
            templatevals['title2'] = 'Number of Members: '

        template = JINJA_ENVIRONMENT.get_template('finaltemplate.html')
        self.response.write(template.render(templatevals))

    def compare(self, compare1=None, compare2=None):
        templatevals = {}
        if compare1 is not None and compare2 is not None:
            member1 = findID(compare1)
            member2 = findID(compare2)
            data = compareMembers(member1, member2)
            logging.warning(data)
            templatevals['data'] = compareparse(data, member1, member2)
            templatevals['message'] = 'Here is what we found'

        template = JINJA_ENVIRONMENT.get_template('finaltemplate.html')
        self.response.write(template.render(templatevals))

    def get(self):
        self.genpage()

    def post(self):
        if self.request.get('search') == 'search':
            member = self.request.get('member')
            if member is not None:
                self.genpage(member)
        elif self.request.get('home') == 'home':
            self.genpage()
        elif self.request.get('compare') == 'compare':
            comparemem = self.request.get('membersearch')
            compareme2 = self.request.get('membersearch2')
            if comparemem is not None and compareme2 is not None:
                self.compare(comparemem, compareme2)


application = webapp2.WSGIApplication([('/', MainHandler)], debug=True)