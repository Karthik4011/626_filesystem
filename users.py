from pyftpdlib.authorizers import DummyAuthorizer
authorizer = DummyAuthorizer()
authorizer.add_user('user', 'password', '/home/user', perm='elradfmwMT')

print(authorizer)