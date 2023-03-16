from clientStreamIngestApp import clientStreamIngestApp
from nipyapi import canvas, templates
import time
from apscheduler.schedulers.background import BackgroundScheduler

class streamingestmanager():
    def __init__(self):
        self.clientApps = []
        self.under_performing_apps = []
        

    def deploy_app(self, app: clientStreamIngestApp):
        #self.clientApps.append(app)
        # create tenantApplication under root process group
        root_pg_ID = canvas.get_root_pg_id()
        root_pg = canvas.get_process_group(root_pg_ID, 'id')

        template = templates.upload_template(pg_id=root_pg.id, template_file=app.get_appfile())
        templates.deploy_template(template_id = template.id, pg_id=root_pg.id, loc_x=10.0, loc_y=-700.0)
        
        temlate2 = templates.upload_template(pg_id=root_pg.id, template_file=app.get_app() + "PutCassandraQL.xml") # deploy "service template" for tenants stream
        templates.deploy_template(template_id = temlate2.id, pg_id=root_pg.id, loc_x=1500.0, loc_y=-700.0)

        # wait 3 seconds for everything to deploy
        time.sleep(3) 

        # delete templates
        templates.delete_template(t_id = template.id)
        templates.delete_template(t_id = temlate2.id)

        # create connections
        tenant_pg = canvas.get_process_group(app.get_app(), 'name') 
        output_ports = canvas.list_all_output_ports(tenant_pg.id)
        canvas.create_connection(source=output_ports[0], target=canvas.get_processor(app.get_app() + "PutCassandraQL", 'name'))
        

    def schedule_ON(self, app: clientStreamIngestApp):
        tenant_pg = canvas.get_process_group(app.get_app(), 'name')
        canvas.schedule_process_group(tenant_pg.id, True)

        p = canvas.get_processor(app.get_app() + "ConsumeMQTT", 'name')
        canvas.schedule_processor(p, True)

        p = canvas.get_processor(app.get_app() + "PutCassandraQL", 'name')
        canvas.schedule_processor(p, True)
        time.sleep(1) #too many requests
        p = canvas.get_processor(app.get_app() + "LogFails", 'name')
        canvas.schedule_processor(p, True)

    def schedule_OFF(self, app: clientStreamIngestApp):
        tenant_pg = canvas.get_process_group(app.get_app(), 'name')
        canvas.schedule_process_group(tenant_pg.id, False)

        p = canvas.get_processor(app.get_app() + "ConsumeMQTT", 'name')
        canvas.schedule_processor(p, False)

        p = canvas.get_processor(app.get_app() + "PutCassandraQL", 'name')
        canvas.schedule_processor(p, False)
        time.sleep(1) #too many requests
        p = canvas.get_processor(app.get_app() + "LogFails", 'name')
        canvas.schedule_processor(p, False)

    def get_apps_performance(self, app: clientStreamIngestApp): # <------------------------- Monitor, get messages processed in last 5 min.
        p = canvas.get_processor(app.get_app() + "PutCassandraQL", 'name')
        messagesN = p.status.aggregate_snapshot.flow_files_in
        return messagesN


    def get_apps_under_threshold(self): #<------------------------- Monitor, keeps track of apps under threshold.
        print("getting apps under threshold")
        threshold = 100 # messages more performance metrics can be added. (this one just tests if an app has only processed less thatn 100 messages in last 5 minutes)
        for app in self.clientApps:
            performance = self.get_apps_performance(app)
            if int(performance) < threshold:
                self.under_performing_apps.append(app)
                print("app " + app.app() + " is under performance threshold")
            else:
                self.under_performing_apps.remove(app)
        print("There are " + str(len(self.under_performing_apps)) + " clientStreamIngest apps that are underperforming.")

    def under_performing_ratio(self):
        n = len(self.clientApps)
        under_performing = len(self.under_performing_apps)
        
        try:
            ratio = under_performing / n
        except ZeroDivisionError:
            ratio = 0
        return ratio

        

    def get_metrics(self, app: clientStreamIngestApp): #  <---------------------------- MONITOR
        p = canvas.get_processor(app.get_app() + "PutCassandraQL", 'name')
        statsPUT = p.status.aggregate_snapshot.to_str()

        size = p.status.aggregate_snapshot.input

        duration = p.status.aggregate_snapshot.tasks_duration_nanos # The number of nanoseconds that this Processor has spent running in the last 5 minutes --NipyApi 
        messagesN = p.status.aggregate_snapshot.flow_files_in 
        try:
            AVG_ingestion_time = float(duration) / float(messagesN) # in nanosecs
        except:
            AVG_ingestion_time = "N/A"

        bytes = p.status.aggregate_snapshot.bytes_in
        try:
            processing_rate = float(bytes) / float(duration)
        except:
            processing_rate = "N/A"

        #p = canvas.get_processor(app.get_app() + "ConsumeMQTT", 'name')
        #tatsREC = p.status.aggregate_snapshot.to_str()

        p = canvas.get_processor(app.get_app() + "LogFails", 'name')
        ingestion_failures = p.status.aggregate_snapshot.flow_files_in
        return "Monitor for " + app.get_app() + " <br/> " + " Total ingestion size (records, size): " +  str(size) + " <br/> Average ingestion time: " + str(AVG_ingestion_time) + " NanoSeconds <br/>  Processing rate: " + str(processing_rate) + "Bytes/Nanosecond <br/> Number of messages: " + str(messagesN) + " <br/> Failed database ingestions: <br/>" + str(ingestion_failures) + " <br/> Raw data: <br/>" + statsPUT
