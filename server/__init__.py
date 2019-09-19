from memcache import Client

cache = Client([("localhost", 11211), ("127.0.0.1", 11211)], debug=True)

