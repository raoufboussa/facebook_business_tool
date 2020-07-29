import requests
from bson.json_util import dumps

params = (
    ('fields', 'accounts{access_token,ad_campaign,posts}'),
    ('access_token', 'EAAt6AfVaOUABACRShBSMrBYB2YiECm0g6UYtDPK8HNGZCNpLstEhT6iv95RVaqAp7X39brDuxnZC2zlToiD1NLzqomaXR8BzXdaWojxmbd9TCzyWZAldr2UCO57viUbZBEJ8jpwzMfOf1LrxN4ZAIeAOmYXJQMFvptRIgtPRn5FP0VaZC2XCX0OsI7MZCBmmgzni3doDZBn4jkbr18j9ZBDjstZAc8XJj212xlObwbSRpnpPJzqjumvzBV'),
)

response = requests.get('https://graph.facebook.com/v5.0/me', params=params)
print(response.content)