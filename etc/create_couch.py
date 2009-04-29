#!/usr/bin/env python

import sys
sys.path.extend(["lib", "../lib"])

from twisted.internet import reactor, defer

from twitterspy import db, cache

def parse_timestamp(ts):
    return None

@defer.deferredGenerator
def create_database():
    couch = db.get_couch()
    d = couch.createDB(db.DB_NAME)
    wfd = defer.waitForDeferred(d)
    yield wfd
    print wfd.getResult()

    doc="""
{"language":"javascript","views":{"counts":{"map":"function(doc) {\n  if(doc.doctype == 'User') {\n    var cnt = 0;\n    if(doc.tracks) {\n        cnt = doc.tracks.length;\n    }\n    emit(null, {users: 1, tracks: cnt});\n  }\n}","reduce":"function(key, values) {\n  var result = {users: 0, tracks: 0};\n  values.forEach(function(p) {\n     result.users += p.users;\n     result.tracks += p.tracks;\n  });\n  return result;\n}"},"status":{"map":"function(doc) {\n  if(doc.doctype == 'User') {\n    emit(doc.status, 1);\n  }\n}","reduce":"function(k, v) {\n  return sum(v);\n}"}}}
"""
    d = couch.saveDoc(db.DB_NAME, doc, '_design/counts')
    wfd = defer.waitForDeferred(d)
    yield wfd
    print wfd.getResult()

    doc="""
{"language":"javascript","views":{"query_counts":{"map":"function(doc) {\n  if(doc.doctype == 'User') {\n    doc.tracks.forEach(function(query) {\n      emit(query, 1);\n    });\n  }\n}","reduce":"function(key, values) {\n   return sum(values);\n}"}}}
"""

    d = couch.saveDoc(db.DB_NAME, doc, '_design/query_counts')
    wfd = defer.waitForDeferred(d)
    yield wfd
    print wfd.getResult()

    doc="""
{"language":"javascript","views":{"active":{"map":"function(doc) {\n  if(doc.doctype == 'User' && doc.active) {\n    emit(null, doc._id);\n  }\n}"}}}
"""

    d = couch.saveDoc(db.DB_NAME, doc, '_design/users')
    wfd = defer.waitForDeferred(d)
    yield wfd
    print wfd.getResult()

    reactor.stop()

reactor.callWhenRunning(cache.connect)
reactor.callWhenRunning(create_database)
reactor.run()
