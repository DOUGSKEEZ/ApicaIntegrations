#!/usr/env/bin python

import json
import urllib2


headers = {'Content-Type': 'Application/json'}


def get_group_checks(groupid):
      url = (
            "https://api-wpm.apicasystem.com/"
            "v3/groups/{}/checks?"
            "&auth_ticket=#########Your API token Here############"
      )
      req = urllib2.Request(url.format(groupid), None, headers)
      resp = urllib2.urlopen(req)
      return json.load(resp)
      

def get_group_ids(results):
      for r in results:
            groupname = r.get('name')
            for subgroup in r.get('groups',[]):
                  subgroupname = subgroup.get('name')
                  subid = subgroup.get('id')
                  checkids = get_group_checks(subid)
                  for c in checkids:
                        checkresult = get_check_results(c)
                        checkresult['group_name'] = groupname
                        checkresult['sub_group_name'] = subgroupname
                        print json.dumps(checkresult, indent=4)

def get_check_results(cid):
      url = (
            "https://api-wpm.apicasystem.com/"
            "v3/checks/{}?"
            "&auth_ticket=#########Your API token Here############"
      )
      req = urllib2.Request(url.format(cid), None, headers)
      resp = urllib2.urlopen(req)
      return json.load(resp)
           

def remove_fields(data, fields=None):
      fields = fields or ['id', 'name']
      return {
            k: v
            for k,v in data.items()
            if k in ['id', 'name']
      }


def clean_results(data):
      for item in data:
            groups = map(
                remove_fields,
                item.get('groups', [])
            )
            _item = remove_fields(item)
            _item['groups'] = groups
            yield _item


def get_groups():
      group_url = "https://api-wpm.apicasystem.com/v3/groups?&auth_ticket=#########Your API token Here############"
      req = urllib2.Request(group_url, None, headers)
      resp = urllib2.urlopen(req)
      return json.load(resp)


if __name__=="__main__":
      results = list(clean_results(get_groups()))
      get_group_ids(results)