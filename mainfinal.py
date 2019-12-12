# Avery Wolf
# HCDE 310 Final Project
# API: ProPublica

import webapp2, os, urllib2, urllib, json
import jinja2
import logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

apikey = '5BRInQ6lktfdklvFQWYwehr5hTKgkezIS0nDxHRn'

# method used to get data from the API and return an error if something goes wrong
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


# method will return data of all the members of the 116th congress from the API
# whole URL will look like: "https://api.propublica.org/congress/v1/116/senate/members.json"
def memberAPI(baseurl='https://api.propublica.org/congress/v1/'):
    congress = '116'
    chamber = 'senate'
    url = baseurl + congress + '/' + chamber + '/members.json'
    req = urllib2.Request(url=url, headers={"X-API-Key": apikey})
    result = safeGet(req)
    if result is not None:
        data = json.load(result)
        return data


# method will return data from the API about a specific member
# memberid:  a series of 7 numbers or letters corresponding to a specific member of congress
# whole URL will look like: "https://api.propublica.org/congress/v1/members/K000388.json"
def searchMember(memberid, baseurl='https://api.propublica.org/congress/v1/'):
    url = baseurl + '/members/' + str(memberid) + '.json'
    req = urllib2.Request(url=url, headers={"X-API-Key": apikey})
    result = safeGet(req)
    if result is not None:
        data = json.load(result)
        return data

# method will return data about two members of congress and their overlapping agreements/disagreements
# mem1: (member id) a series of 7 numbers or letters corresponding to a specific member of congress
# mem2: (member id) a series of 7 numbers or letters corresponding to a specific member of congress
# whole URL will look like: https://api.propublica.org/congress/v1/members/{first-member-id}/votes/{second-member-id}/{congress}/{chamber}.json
def compareMembers(mem1, mem2, baseurl='https://api.propublica.org/congress/v1/members/'):
    url = baseurl + mem1 + '/votes/' + mem2 + '/116/senate'
    req = urllib2.Request(url=url, headers={"X-API-Key": apikey})
    result = safeGet(req)
    if result is not None:
        data = json.load(result)
        return data


# method will return a data about a recent vote's information (title, description, verdict) and the roll call
# "https://api.propublica.org/congress/v1/115/senate/sessions/1/votes/17.json"
def recentVotes(url='https://api.propublica.org/congress/v1/116/senate/sessions/1/votes/100.json'):
    req = urllib2.Request(url=url, headers={"X-API-Key": apikey})
    result = safeGet(req)
    if result is not None:
        data = json.load(result)
        return data


# method will parse through a dictionary about recent vote info and return specific data that's relevant to a specific
# member of congress. Information from this method will be shown when users compare two members or search for a member
# dictionary: recent vote dictionary
# mem: name that the information will pertain to
def getvoteinfo(dictionary, mem):
    info = None
    for item in dictionary['results']['votes']['vote']['positions']:
        if item['name'] == mem:
            info = {}
            if len(dictionary['results']['votes']['vote']['bill']) is not 0:
                info['billid'] = dictionary['results']['votes']['vote']['bill']['bill_id']
                info['billtitle'] = dictionary['results']['votes']['vote']['bill']['title']
                info['latestaction'] = dictionary['results']['votes']['vote']['bill']['latest_action']
            info['description'] = dictionary['results']['votes']['vote']['description']
            info['result'] = dictionary['results']['votes']['vote']['result']
            info['date'] = dictionary['results']['votes']['vote']['date']
            info['demup'] = dictionary['results']['votes']['vote']['democratic']['majority_position']
            info['repup'] = dictionary['results']['votes']['vote']['republican']['majority_position']
            info['memposition'] = item['vote_position']
            info['name'] = item['name']
    return info


# method parses through a dictionary and creates and returns a dictionary of relevant information
# dict: dictionary of all member information
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


# method will parse through a dictionary and create and return a dictionary of relevant information pertaining to a
# specific member a user has searched
# dictionary: dictionary of specific member information
# id: member id for searched member
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


# method will parse information from a dictionary and create and return a dictionary with relevant information pertaining
# to two specific members and their overlap
# dictionary: dictionary of specific member information
# mem1: first member the user searched for
# mem2: second member the user searched for
def compareparse(dictionary, mem1, mem2):
    data = {}
    data['firstmem'] = mem1
    data['secondmem'] = mem2
    data['commonvotes'] = dictionary['results'][0]['common_votes']
    data['disagree'] = dictionary['results'][0]['disagree_votes']
    data['agree_pct'] = dictionary['results'][0]['agree_percent']
    data['disagree_pct'] = dictionary['results'][0]['disagree_percent']
    return data


# method will use the name that a user has input and return that members id
# member: the congress member's name the user has searched for
def findID(member):
    list = memberAPI()
    members = memberparse(list)
    memberid = None
    splitit = member.split()
    mfirst = splitit[0]
    mlast = splitit[1]
    for item in members:
        split = item.split()
        firstname = split[0]
        lastname = split[1]
        if firstname == mfirst and lastname == mlast:
            memberid = members[item]['id']
            return memberid
    return memberid

# class will handle all output and use of Jinja
class MainHandler(webapp2.RequestHandler):
    # method used for producing entire member list or specific member information when member is not None
    def genpage(self, member=None, voteinfo=None):
        templatevals = {}
        if member is not None:
            id = findID(member)
            if id is not None:
                if voteinfo is not None:
                    templatevals['voteinfo'] = voteinfo
                data = searchMember(id)
                findata = specificparse(data, id)
                templatevals['member'] = member
                templatevals['data'] = findata
                templatevals['title1'] = 'Search Results'
                templatevals['message'] = 'Here is what we found'
            else:
                templatevals['title1'] = 'Member of Congress'
                templatevals['message'] = 'Please enter a valid member'
                templatevals['subtitle'] = 'Welcome to your congress member resource! Take a look at the current congressmen and women of the 116th congress of the United States. Search a specific member, compare two members, or simply take a look at them all!'
        else:
            list = memberAPI()
            templatevals['members'] = memberparse(list)
            templatevals['membernum'] = list['results'][0]['num_results']
            templatevals['subtitle'] = 'Welcome to your congress member resource! Take a look at the current congressmen and women of the 116th congress of the United States. Search a specific member, compare two members, or simply take a look at them all!'
            templatevals['title1'] = 'Members of Congress'
            templatevals['title2'] = 'Number of Members: '

        template = JINJA_ENVIRONMENT.get_template('finaltemplate.html')
        self.response.write(template.render(templatevals))

    # method used when a user wants to compare two members
    def compare(self, compare1=None, compare2=None, vote1=None, vote2=None):
        templatevals = {}
        if compare1 is not None and compare2 is not None:
            member1 = findID(compare1)
            member2 = findID(compare2)
            data = compareMembers(member1, member2)
            newdata = compareparse(data, compare1, compare2)
            templatevals['data1'] = newdata
            templatevals['message1'] = 'Here is what we found'
            templatevals['title1'] = 'Search Results'
            if vote1 is not None and vote2 is not None:
                templatevals['comparevoteinfo1'] = vote1
                templatevals['comparevoteinfo2'] = vote2

        template = JINJA_ENVIRONMENT.get_template('finaltemplate.html')
        self.response.write(template.render(templatevals))

    def get(self):
        self.genpage()

    # receives user input and stores it and sends it to necessary methods, and then to necessary handlers
    def post(self):
        if self.request.get('search') == 'search':
            member = self.request.get('member')
            if member is not None:
                data = recentVotes()
                voteinfo = getvoteinfo(data, member)
                if voteinfo is not None:
                    self.genpage(member, voteinfo)
                else:
                    self.genpage(member)
        elif self.request.get('home') == 'home':
            self.genpage()
        elif self.request.get('compare') == 'compare':
            comparemem = self.request.get('membersearch')
            compareme2 = self.request.get('membersearch2')
            if comparemem is not None and compareme2 is not None:
                data = recentVotes()
                mem1info = getvoteinfo(data, comparemem)
                mem2info = getvoteinfo(data, compareme2)
                if mem1info is not None and mem2info is not None:
                    self.compare(comparemem, compareme2, mem1info, mem2info)
                else:
                    self.compare(comparemem, compareme2)


application = webapp2.WSGIApplication([('/', MainHandler)], debug=True)