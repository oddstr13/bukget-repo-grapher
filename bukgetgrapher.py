#!/usr/bin/python
import rrdtool
import os
import sys
import json
import urllib2

repo_url = "http://bukget.org/repo.json"
workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
rrd_file = os.path.join(workdir, "repo.rrd")
rrd_file_exists = os.path.exists(rrd_file)
rrd_file_isfile = os.path.isfile(rrd_file)
png_file = os.path.join(workdir, "graph.png")

def create_rrd(fn):
    rrdtool.create(fn, "--step", "3600",
      "DS:packages:GAUGE:3600:0:U",
      "DS:authors:GAUGE:3600:0:U",
      "DS:categories:GAUGE:3600:0:U",
      "DS:versions:GAUGE:3600:0:U",
      "RRA:AVERAGE:0:1:87840",
    )

USER_AGENT = "BukGet repo statestics by Oddstr13"
DEBUG = 0

def update_rrd(fn):
#{'versions': 67, 'packages': 25, 'categories': 13, 'authors': 17}
    r = get_data()    
    rrdtool.update(fn,
      "--template", "packages:authors:categories:versions",
      "N:%s:%s:%s:%s" %(r['packages'], r['authors'], r['categories'], r['versions'])
    )

def graph_rrd(fn, output, start="-1w", end="N", width="600", height="200"):
    width = str(width); height = str(height)
    rrdtool.graph(output,
      "--title", "BukGet repo statesticks",
      "--start", start,
      "--end", end,
      "--width", width,
      "--height", height,
      "--full-size-mode",
      "--lower-limit", "0",
#      "--no-gridfit",
      "--units=si",
      "--base", "1000",
      "--slope-mode",
      "--watermark", "BukGet repo statestics by Oddstr13",
      "DEF:packages=%s:packages:AVERAGE" %(fn),
      "DEF:authors=%s:authors:AVERAGE" %(fn),
      "DEF:versions=%s:versions:AVERAGE" %(fn),
      "DEF:categories=%s:categories:AVERAGE" %(fn),
      "VDEF:Packages=packages,LAST",
      "VDEF:Authors=authors,LAST",
      "VDEF:Versions=versions,LAST",
      "VDEF:Categories=categories,LAST",
      "LINE1:packages#0000ff:Packages",
      "GPRINT:Packages:%0.0lf",
      "LINE1:authors#ff0000:Authors",
      "GPRINT:Authors:%0.0lf",
      "LINE1:versions#00ff00:Versions",
      "GPRINT:Versions:%0.0lf",
      "LINE1:categories#00ffff:Categories",
      "GPRINT:Categories:%0.0lf\n",
    )

def get_http(url):
    _http_req = urllib2.Request(url)
    _http_handler = urllib2.HTTPHandler(debuglevel=DEBUG)
    _http_opener = urllib2.build_opener(_http_handler)
    _http_req.add_header('User-Agent', USER_AGENT)
    _http_res = _http_opener.open(_http_req).read()
    return _http_res


def get_data():
    repo = json.loads(get_http(repo_url))
    _packages = len(repo)
    _versions = 0
    __c = []
    __a = []
    for p in repo:
#        print p
        for _a in p['authors']:
            if _a not in __a: __a.append(_a)
        _versions += len(p['versions'])
        for _c in p['categories']:
            if not _c in __c: __c.append(_c)
    _authors = len(__a)
    _categories = len(__c)
    return {
      'authors'     : _authors,
      'packages'    : _packages,
      'versions'    : _versions,
      'categories'  : _categories,
    }

if __name__ == "__main__":
    if not rrd_file_exists:
        create_rrd(rrd_file)
    if ("-u" in sys.argv) or ("--update" in sys.argv):
        update_rrd(rrd_file)
    if ("-g" in sys.argv) or ("--graph" in sys.argv):
        graph_rrd(rrd_file, png_file, start="-1w", width=800, height=300)

#    print get_data()
