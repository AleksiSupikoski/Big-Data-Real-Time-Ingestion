# 1 - Batch data ingestion pipeline 

### 1.1 The ingestion will be applied to files of data. Define a set of constraints for files that mysimbdp will support for ingestion. Design a configuration model for the tenant service profile that can be used to specify a set of constraints for ingestion (e.g., maximum number of files and amount of data). Explain why you as a platform provider decide such constraints. Implement these constraints into simple configuration files and provide examples (e.g., JSON or YAML)

Service profile is defined in two .xml files for input and ouptut of the clientBatchIngestApp, One limits the number of files (per hour) and file extension that can be accepted and forwarded into clientBatchIngestApp, the other sets a constraint on size of data per hour that is allowed for ingestion from clientBatchIngestApp to the database. As a service platform provider we want to have control over disk access in StagingInputDirectory and reads, we also want to differentiate the client services based on their pay, for example tenant1 pays little and tenant2 pays alot for his service, this comes at a for mysimbdp, therefore we want to limit the amount of files and data that each tenant can process, depending on their service profile. Cheching file format and limiting uploadrates can also provide some safety to the system. 

For testing for each tenant (two tenants) a personal batch ingestion service profile has been developed, the first one limits user to stage 500 files of any format for ingestion per-hour and 1 Gigabyte per-hour, the second one limits user to stage 500 .csv files for ingestion per-hour and 100 Gigabytes per-hour. It is also possible to limit the file size:
```
<entry>
<key>Maximum File Size</key>
  <value>1 GB</value>
</entry>
```
The service profile also restricts clients to writing data in fields that do not belong to them.

#### TenantServiceProfile2:
inputTenantServiceProfile2:
```
<entry>
<key>File Filter</key>
  <value>[^\.].*.csv</value>
</entry>
...
<entry>
<key>Maximum Rate</key>
  <value>500</value>
</entry>
<entry>
<key>Rate Controlled Attribute</key>
</entry>
<entry>
<key>Time Duration</key>
  <value>1 h</value>
</entry>
```

outputTenantServiceProfile2:
```
...
<entry>
<key>Cassandra Contact Points</key>
  <value>cassandra-1:9042,cassandra-2:9042,cassanra-3:9042</value>
</entry>
<entry>
<key>Keyspace</key>
  <value>tenant2</value>
</entry>
...
<entry>
<key>Rate Control Criteria</key>
  <value>data rate</value>
</entry>
<entry>
<key>Maximum Rate</key>
  <value>100 GB</value>
</entry>
<entry>
<key>Rate Controlled Attribute</key>
</entry>
<entry>
<key>Time Duration</key>
  <value>1 h</value>
</entry>
...

```
Whenever a clientBatchIngestApp is deployed, these profiles are assigned to it as rateControllers (thus controlling & limiting the throughput of a pipeline accordingly to tenant's service profile)

### 1.2 Each tenant will put the tenant's data files to be ingested into a staging directory, client-staging- input-directory within mysimbdp (the staging directory is managed by the platform). Each tenant provides its ingestion programs/pipelines, clientbatchingestapp, which will take the tenant's files as input, in client-staging-input-directory, and ingest the files into mysimbdp-coredms. Any clientbatchingestapp must perform at least one type of data wrangling to transform data elements in files to another structure for ingestion. As a tenant, explain the design of clientbatchingestapp and provide one implementation. Note that clientbatchingestapp follows the guideline of mysimbdp given in the next Point 3.

In mysimbdp, a clientBatchIngestApp is an enclosed Nifi process group with one input and one output port. These ports connect at input to StagingInputDirectory (under their service plan constraints) and at output to the controlled database ingester (output is also controlled with service constraints). This provides a layer of enclosure to the customers application, having a remote process group can provide even more, but here it is done locally. Inside tenant's process group a tenant is free process files as they desire. This way the apps are essentially "black boxes" but still controllable and with constraints to what they can do.

In my case each tenant simply receives files from the clientStagingDirectory, then reads them and "wrangles" the data to build a cql insert statement. Outside clientBatchIngestApp the statement will only be accepted if the keyspace belongs to the tenant and datawrites per hor are not exceeded. Outside nifi, whenever a new clientBatchingestApp is created an abstratction of it is stored in manager (clientBatchIngestManager). The abstraction (in form of a python calss) keeps track of the application id and backup file the class also receives the pre defined serviceprofile, when it gets passed from the driver to the manager.

<p align="center"><img src="img/clientApp.png")<p>
  
clientApps get deployed automatically and get scheduled through Nifi's API. This is handled by the clientBatchIngestManager.
  
### 1.3 As the mysimbdp provider, design and implement a component mysimbdp-batchingestmanager that invokes tenant's clientbatchingestapp to perform the ingestion for available files in client- staging-input-directory. mysimbdp imposes the model that clientbatchingestapp has to follow but clientbatchingestapp is, in principle, a blackbox to mysimbdp-batchingestmanager. Explain how mysimbdp-batchingestmanager knows the list of clientbatchingestapp and decides/schedules the execution of clientbatchingestapp for tenants.
  
clientBatchIngestManager is defined as a python object which keeps a list of clientBatchIngestApps and deploys, controls and monitors them over Nifi API. The manager requires a driver for it so physically it runs on a flask app container. The driver provides scheduling logic and a web interface for it & for its monitor. The driver also drives streamIngestManager (part 2). Please see clientbatchingestappmanager.py and driver: app.py. The code is well commented.

Whenever a new clientBatchIngestApp is deployed (they can only be deployed through the manager, invoked by the driver) the manager receives an abstraction of the clientBatchINgest app and stores it. It uses the abstraction to deploy, schedule and retrieve metrics (through the API) from the actual application running on Nifi.
  
The scheduling logic for the manager is defined in the driver. I have set it to schedule all batchIngestApplications running whenever the load on the mysimbdp is low, i.e. more than 50% streamIngestApplications are underperforming (more than 50% of stream apps processing less than 100 messages per hour). Additionally by default the streamBatchIngestApplications are scheduled to run at night, when the load on servers is expected to be lower. For testing purpoces i have commented it out of the code, please uncomment them if you want to test that feature.
  
For the driver (app.py, which runs the managers) I have developed a web interface that makes testing and monitoring easier. Please read the Deployment instructions to see how to do the tests.

  
### 1.4 Explain your design for the multi-tenancy model in mysimbdp: which parts of mysimbdp will be shared for all tenants, which parts will be dedicated for individual tenants so that you as a platform provider can add and remove tenants based on the principle of pay-per-use. Develop test clientbatchingestapp, test data, and test constraints of files, and test service profiles for tenants according your deployment. Show the performance of ingestion tests, including failures and exceptions, for at least 2 different tenants in your test environment and constraints. Demonstrate examples in which data will not be ingested due to a violation of constraints. Present and discuss the maximum amount of data per second you can ingest in your tests.
  
  
While explaining the previous parts i have already touched the aspect of accessible parts of mysimbdp. In essence, each clientBatchIngestApp can access (in real deployment) their own clientStagingInputDirectory, read files from it under their service profile specifications, and write data out (again, under their service profile specifications) only to their keyspace in cassandra cluster. The tenants applications simply will not receive file, if it violates the constraints and if data limit is exceded, the data will not be put into the database. If a clientBatchIngestApp tries to write to a keyspace not belonging to it, the data will be dropped as well as if data is in wrong format. The service profiles are configuresd in nifi controlRate -blocks outside the clientBatchIngestApplication, so it has no control over them. The service will simply not allow applications to violate the service.
  
For example, clientapp with service profile 1 has sent 1 GB of data for last 1 h, the service profile will not allow it to send any more data, so the data will be kept in a queue. after an hour passes after the ingestion started the queue will  be emptied for exactly 1 GB / h. Or for example clientapp has read 500 files for last hour, it willnot be allowed to read more (by the service) and when an hour passes, the queued files will be  be passed to it.
  
  #### MAX DATA TESTS STATS
  
### 1.5 Implement and provide logging features for capturing successful/failed ingestion as well as metrics about ingestion time, data size, etc., for files which have been ingested into mysimbdp. Logging information must be stored in separate files, databases or a monitoring system for analytics of ingestion. Explain how mysimbdp could use such logging information. Show and explain simple statistical data extracted from logs for individual tenants and for the whole platform with your tests.
  
Additionally to managing the clientBatchIngestApps the clientBatchIngestManager also retrieves Logs from them (though API). The service attaches LogAtribute processor to the end of the pipeline, to keep track of possible failed ingestions, it also retrieves information from the endpoint of the pipeline to keep track of ingestion time, data writes, speed, size etc. provided by the json. The monitoring system fuctionality is implemented in the driver, and can be accessed through it's web interface or with a http request. The data is updated with a moving 5-minute window, which is updated every nanosecond.

This data is especially interesting to the service provider, for example this data can be retrieved by a load balancer application, that will deploy another Nifi node or a Cassandra node to their clusters when it calculates that the pipeline / ingestion processing rate drops below a threshold, some threshold level.
