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
  'replication_factor' : 2
  };
```

```
CREATE KEYSPACE tenant2
  WITH REPLICATION = {
  'class' : 'SimpleStrategy',
  'replication_factor' : 2
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


## Deploy and Confugure Apache NiFi
### Deploy NiFi in a Container

In terminal pull latest Apache NiFi container: `docker pull apache/nifi:latest`


Deploy the container with
```
docker run -p 8080:8080 -d \
-e NIFI_WEB_HTTP_HOST="0.0.0.0" \
-e NIFI_WEB_HTTP_PORT="8080" \
-e NIFI_WEB_HTTPS_PORT="" \
-e NIFI_WEB_PROXY_CONTEXT_PATH="/" \
-e NIFI_WEB_PROXY_HOST="" \
-e NIFI_WEB_PROXY_PORT="" \
-e NIFI_WEB_SECURITY_ENABLED="false" \
--network="code_default" --name nifii \
-e JVM_HEAP_SIZE=8g \
```
This will deploy a single node nifi container (if you want to try out a 3-node nifi cluster use the yml file for it in /code. We give the nifi extra heap, for better logging. Note that we wet the network to the docker network of the cassandra cluter, by default it will be called "code_default". Makse sure that the containers have beend deployed to the same network with:
`docker ps --format '{{ .ID }} {{ .Names }} {{ json .Networks }}'`
go to [http://localhost:8080/nifi](http://localhost:8080/nifi) to see the web interface and log in with the received credentials.
