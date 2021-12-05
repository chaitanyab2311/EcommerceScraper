from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra.auth import PlainTextAuthProvider

from cassandra.cluster import ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import WhiteListRoundRobinPolicy
from cassandra.query import tuple_factory

cluster = Cluster()


def insert_prices(prices_data):
  try:
    session = cluster.connect('products')

    for website in prices_data:
      for data in prices_data[website]:
        rows = session.execute("INSERT INTO products.products (uid,productName,productPrice,website) VALUES (uuid(),'"+ data + "','" + prices_data[website][data] + "','" + website + "');")
        print("prices added to db")
  except Exception as e:
    print("Exception occured" + str(e))
