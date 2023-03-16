# 1 - Batch data ingestion pipeline 

### 1.1 The ingestion will be applied to files of data. Define a set of constraints for files that mysimbdp will support for ingestion. Design a configuration model for the tenant service profile that can be used to specify a set of constraints for ingestion (e.g., maximum number of files and amount of data). Explain why you as a platform provider decide such constraints. Implement these constraints into simple configuration files and provide examples (e.g., JSON or YAML)

Service profile is defined in two .xml files for input and ouptut of the clientBatchIngestApp, One limits the number of files (per hour) and file extension that can be accepted and forwarded into clientBatchIngestApp, the other sets a constraint on size of data per hour that is allowed for ingestion from clientBatchIngestApp to the database. For testing for each tenant (two tenants) a personal batch ingestion service profile has been developed, the first one limits user to stage 500 .csv files for ingestion per-hour and 1 Gigabyte per-hour, the second one limits user to stage 500 .csv files for ingestion per-hour and 100 Gigabytes per-hour. It is also possible to limit the file size:
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