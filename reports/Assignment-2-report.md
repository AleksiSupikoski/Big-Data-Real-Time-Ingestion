# 1 - Batch data ingestion pipeline 

### 1.1 The ingestion will be applied to files of data. Define a set of constraints for files that mysimbdp will support for ingestion. Design a configuration model for the tenant service profile that can be used to specify a set of constraints for ingestion (e.g., maximum number of files and amount of data). Explain why you as a platform provider decide such constraints. Implement these constraints into simple configuration files and provide examples (e.g., JSON or YAML)

Service profile is defined in two .xml files, One limits the number of files (per hour) and file extension that can be accepted, the other sets a constraint on size of data per hour that is allowed for ingestion. For testing for each tenant (two tenants) a personal batch ingestion service profile has been developed, the first one limits
’’’
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
’’’
