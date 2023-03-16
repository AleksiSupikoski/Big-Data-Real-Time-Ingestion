## Deploy and Set Up Apache Cassandra Cluster
### Deploy Cassandra Cluster in Docker
It is expected that Docker is installed on the system. 

In terminal cd into .../code and execute
`docker-compose up`

When the cluster sets up, get their container ids with 
`docker ps` and enter one of them with 
`docker exec -it <containerID> bash`

### Configure the Cluster
Enter CQL with `cqlsh` then create the needed keyspace for a tenant with
```
CREATE KEYSPACE tenant1
  WITH REPLICATION = {
  'class' : 'SimpleStrategy',
  'replication_factor' : 3
  };
```

```
CREATE KEYSPACE tenant2
  WITH REPLICATION = {
  'class' : 'SimpleStrategy',
  'replication_factor' : 3
  };
```

Then create table into the keyspace for our data with 
```
CREATE TABLE tenant1.ddata (
time text,
readable_time timestamp,
acceleration float,
acceleration_x int,
acceleration_y int,
acceleration_z int,
battery int,
humidity float,
pressure float,
temperature float,
dev_id text,
PRIMARY KEY (dev_id, readable_time));
```
```
CREATE TABLE tenant2.ddata (
time text,
readable_time timestamp,
acceleration float,
acceleration_x int,
acceleration_y int,
acceleration_z int,
battery int,
humidity float,
pressure float,
temperature float,
dev_id text,
PRIMARY KEY (dev_id, readable_time));
```
after that our nifi cluster is set ready for the data to be put into it.
