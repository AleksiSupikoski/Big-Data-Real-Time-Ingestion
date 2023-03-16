from clientBatchIngestApp import clientBatchIngestApp
from nipyapi import canvas, templates
import time

class batchingestmanager():
    def __init__(self):
        self.clientApps = []
        
    def deploy_app(self, app: clientBatchIngestApp):
        self.clientApps.append(app)
        # create process group under root process group for a clientBatchIngestApp
        root_pg_ID = canvas.get_root_pg_id()
        root_pg = canvas.get_process_group(root_pg_ID, 'id')
        tenant_pg = canvas.create_process_group(parent_pg=root_pg, new_pg_name=app.get_app(), location=(10, 10))

        # deploy the clientBatchIngestApp in clients process group
        template = templates.upload_template(pg_id=tenant_pg.id, template_file=app.get_appfile())
        templates.deploy_template(template_id = template.id, pg_id=tenant_pg.id)

        # debploy tenantServiceProfile controller, connect it to the clientBatchIngestApp and connect clientBatchIngestApp to the mysimbdp-coredms
        service_template = templates.upload_template(pg_id=root_pg.id, template_file="output" + app.get_tenantServiceProfile() + ".xml")
        templates.deploy_template(template_id = service_template.id, pg_id=root_pg.id, loc_x=1000, loc_y=10)
        
        # wait 3 seconds for everything to deploy
        time.sleep(3) 

        # delete templates
        templates.delete_template(t_id = service_template.id)
        templates.delete_template(t_id = template.id)

        #s = canvas.get_processor("output" + app.get_tenantServiceProfile(), 'name') #canvas.get_processor('TenantServiceProfile1', 'name')
        #dest = app.get_app() + 'PutCassandraQL'
        #t = canvas.get_processor(dest, 'name') #canvas.get_processor('clientBatchIngestApp1PutCassandraQL', 'name')
        #canvas.create_connection(source=s, target=t, relationships=['success'])
        #canvas.create_connection(source=canvas.get_processor(app.get_tenantServiceProfile(), 'name'), target=canvas.get_processor(dest, 'name'), relationships=['success'])

        # add connections
        output_ports  = canvas.list_all_output_ports(tenant_pg.id)
        #print("output_ports: ", output_ports)
        #print("port type: ", type(output_ports[0]))
        #print("port id: ", output_ports[0].id)
        #print("component dto? : ", output_ports[0].component)
        #print("component name?: ", output_ports[0].component.name)
        #print("name ", output_ports[0].name)
        canvas.create_connection(source=output_ports[0], target=canvas.get_processor("output" + app.get_tenantServiceProfile(), 'name'))

        input_service_template = templates.upload_template(pg_id=root_pg.id, template_file="input" + app.get_tenantServiceProfile() + ".xml")
        templates.deploy_template(template_id = input_service_template.id, pg_id=root_pg.id, loc_x=-800, loc_y=10)

        # wait 3 seconds for everything to deploy
        time.sleep(3) 

        # delete template
        templates.delete_template(t_id = input_service_template.id)

        # add connections
        sour = canvas.get_processor("input" + app.get_tenantServiceProfile(), 'name') #canvas.get_processor('TenantServiceProfile1', 'name')
        canvas.create_connection(source=sour, target=canvas.list_all_input_ports(tenant_pg.id)[0], relationships=['success'])
        print(app.app)

    def schedule_all_ON(self):
        for app in self.clientApps:
            self.schedule_ON(app)

    def schedule_all_OFF(self):
        for app in self.clientApps:
            self.schedule_OFF(app)
        

    def schedule_ON(self, app: clientBatchIngestApp):
        tenant_pg = canvas.get_process_group(app.get_app(), 'name')
        canvas.schedule_process_group(tenant_pg.id, True)

        p = canvas.get_processor("output" + app.get_tenantServiceProfile(), 'name')
        canvas.schedule_processor(p, True)

        p = canvas.get_processor("input" + app.get_tenantServiceProfile(), 'name')
        canvas.schedule_processor(p, True)

        p = canvas.get_processor("StagingInputDirectory" + app.get_tenantServiceProfile(), 'name')
        canvas.schedule_processor(p, True)

        p = canvas.get_processor(app.get_app() + "PutCassandraQL", 'name')
        canvas.schedule_processor(p, True)
        time.sleep(1) #too many requests
        p = canvas.get_processor(app.get_app() + "LogFails", 'name')
        canvas.schedule_processor(p, True)

    def schedule_OFF(self, app: clientBatchIngestApp):
        tenant_pg = canvas.get_process_group(app.get_app(), 'name')
        canvas.schedule_process_group(tenant_pg.id, False)

        p = canvas.get_processor("output" + app.get_tenantServiceProfile(), 'name')
        canvas.schedule_processor(p, False)

        p = canvas.get_processor("input" + app.get_tenantServiceProfile(), 'name')
        canvas.schedule_processor(p, False)

        p = canvas.get_processor("StagingInputDirectory" + app.get_tenantServiceProfile(), 'name')
        canvas.schedule_processor(p, False)

        p = canvas.get_processor(app.get_app() + "PutCassandraQL", 'name')
        canvas.schedule_processor(p, False)
        time.sleep(1) #too many requests
        p = canvas.get_processor(app.get_app() + "LogFails", 'name')
        canvas.schedule_processor(p, False)

    def get_metrics(self, app: clientBatchIngestApp):
        p = canvas.get_processor(app.get_app() + "PutCassandraQL", 'name')
        stats = p.status.aggregate_snapshot.to_str()

        #p = canvas.get_processor("input" + app.get_tenantServiceProfile(), 'name')
        #files_read = p.status.aggregate_snapshot.to_str()

        #p = canvas.get_processor("StagingInputDirectory" + app.get_tenantServiceProfile(), 'name')
        #wrong_format = p.status.aggregate_snapshot.to_str()

        #p = canvas.get_processor("output" + app.get_tenantServiceProfile(), 'name')
        #data_dropped = p.status.aggregate_snapshot.to_str()

        p = canvas.get_processor(app.get_app() + "LogFails", 'name')
        ingestion_failures = p.status.aggregate_snapshot.flow_files_in

        return "Stats Monitor for "+ app.get_app() + " <br/> Number of failed ingestions: " + str(ingestion_failures) + "  <br/> Ingestion data for ClientBatchIngestApp (raw): " + stats
        #return "Cassandra ingestion stats: <br/> " + stats + " <br/> Files read stats (or dropped due to file limit, look for failure): <br/> " + files_read + " <br/> Files dropped stats (wrong file format, look for failure): <br/> " + wrong_format + " <br/> Data dropped (data limit violation, look for faliure)" + data_dropped
