from clientBatchIngestApp import clientBatchIngestApp
from batchingestmanager import batchingestmanager
from clientStreamIngestApp import clientStreamIngestApp
from streamingestmanager import streamingestmanager

from flask import Flask, render_template, request
from nipyapi import config, canvas
from apscheduler.schedulers.background import BackgroundScheduler

# **************************************************************************************************************************
# **************************************************************************************************************************
#
# A driver for BatchIngestAppManager and StreamIngestAppManager + Automatic Deployment, Monitoring & testing the features
#
# **************************************************************************************************************************
# **************************************************************************************************************************


#config.nifi_config.host = 'http://172.24.0.5:8080/nifi-api'
config.nifi_config.host = 'http://nifii:8080/nifi-api' # replace with your nifi host

manager = batchingestmanager() # BatchIngestManager
steammanager = streamingestmanager() # StreamIngestManager



# ---------------- near realtime monitor:  ------------------
# ------------------ invoke app performance monitor every 5 min. ------------------
sched = BackgroundScheduler(daemon=True)
sched.add_job(steammanager.get_apps_under_threshold,'interval',minutes=5)

# ---------------- ClientBatchIngestApp  Scheduler: ------------------
# ---------------- schedule ClientBatchIngestApps to run at night -----------------
# !!!!!! !!!!!! !!!!!!! !!!!!! !!!!!!! !!!!! !!!!!! !!!!!! !!!!!!! !!!!!! !!!! !!!!! !!!!!! !!!!!! !!!!!!
# THIS SECTION IS COMMENTED FOR DEMONSTARTION PURPOSES, UNCOMMENT FOR PRODUCTION --->
#def schedule_batch_when_MQTT_brokers_inactive():
#    ratio = steammanager.under_performing_ratio
#    if ratio >= 0.5:
#        manager.schedule_all_ON()
#    else:
#        manager.schedule_all_OFF()
#sched.add_job(schedule_batch_when_MQTT_brokers_inactive,'interval',minutes=5)
#sched.add_job(manager.schedule_all_ON, 'cron', hour=0, minute=0)
#sched.add_job(manager.schedule_all_OFF, 'cron', hour=3, minute=0)
# <------------ THIS SECTION IS COMMENTED FOR DEMONSTARTION PURPOSES, UNCOMMENT FOR PRODUCTION
sched.start()




# environment tester / controller ->
app = Flask(__name__)
@app.route("/")
def index():
    return render_template('index.html')


# ----------------------------------------------------------------------------------------------------------------------
# Tenant1
# ----------------------------------------------------------------------------------------------------------------------
app1 = clientBatchIngestApp('clientBatchIngestApp1', 'clientBatchIngestApp1.xml', 'TenantServiceProfile1')

@app.route("/tenant1/deploybatch")
def tenant1deploybatch():
    manager.deploy_app(app1)
    return f"TenantServiceProfile1 deployed and connected to BatchIngestPutCassandraQL under tenantServiceProfile1"
    #root_id = canvas.get_root_pg_id()
    #return f"hello {root_id}" # just for testing

@app.route("/tenant1/scheduleON")
def tenant1scheduleON():
    manager.schedule_ON(app1)
    return f"clientBatchIngestApp1 scheduled to run"

@app.route("/tenant1/scheduleOFF")
def tenant1scheduleOFF():
    manager.schedule_OFF(app1)
    return f"clientBatchIngestApp1 scheduled to stop"

@app.route("/tenant1/metrics")
def tenant1metrics():
    stats = manager.get_metrics(app1)

    return stats

@app.route('/tenant1/uploader', methods = ['GET', 'POST'])
def tenant1upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save('/app/clientBatchIngestApp1.xml')
      return 'file uploaded successfully'
# ----------------------------------------------------------------------------------------------------------------------
# Tenant1
# ----------------------------------------------------------------------------------------------------------------------




# ----------------------------------------------------------------------------------------------------------------------
# Tenant2
# ----------------------------------------------------------------------------------------------------------------------
app2 = clientBatchIngestApp('clientBatchIngestApp2', 'clientBatchIngestApp2.xml', 'TenantServiceProfile2')
@app.route("/tenant2/deploybatch")
def tenant2deploybatch():
    manager.deploy_app(app2)
    return f"TenantServiceProfile1 deployed and connected to BatchIngestPutCassandraQL under tenantServiceProfile1"

@app.route("/tenant2/scheduleON")
def tenant2scheduleON():
    manager.schedule_ON(app2)
    return f"clientBatchIngestApp1 scheduled to run"

@app.route("/tenant2/scheduleOFF")
def tenant2scheduleOFF():
    manager.schedule_OFF(app2)
    return f"clientBatchIngestApp1 scheduled to stop"

@app.route("/tenant2/metrics")
def tenant2metrics():
    stats = manager.get_metrics(app2)
    return stats

@app.route('/tenant2/uploader', methods = ['GET', 'POST'])
def tenant2upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save('/app/clientBatchIngestApp2.xml')
      return 'file uploaded successfully'

# ----------------------------------------------------------------------------------------------------------------------
# Tenant2
# ----------------------------------------------------------------------------------------------------------------------

#@app.route("/tenant1/delete") # need to empty queues before deleting.
#def tenant1delete():
#    p = canvas.get_processor('TenantServiceProfile1', 'name')
#    canvas.delete_processor(p, force=True)
#    tenant_pg = canvas.get_process_group('clientBatchIngestApp1', 'name')
#    canvas.delete_process_group(tenant_pg, force=True)
#    return f"deleted"



# ***************************************************************************************************************************
# Streaming ----->
# ***************************************************************************************************************************


streamapp1 = clientStreamIngestApp('clientStreamIngestApp1', 'clientStreamIngestApp1.xml')

@app.route("/tenant1/deploystream")
def tenant1deploystream():
    steammanager.deploy_app(streamapp1)
    return f"clientSteamIngestApp deployed and connected to BatchIngestPutCassandraQL"

@app.route("/tenant1/schedulestreamON")
def tenant1schedulestreamON():
    steammanager.schedule_ON(streamapp1)
    return f"clientStreamIngestApp scheduled to run"

@app.route("/tenant1/schedulestreamOFF")
def tenant1schedulestreamOFF():
    steammanager.schedule_OFF(streamapp1)
    return f"clientStreamIngestApp scheduled to stop"

@app.route("/tenant1/metricsstream")
def tenant1metricsstream():
    stats = steammanager.get_metrics(streamapp1)
    return stats

@app.route('/tenant1/uploaderstream', methods = ['GET', 'POST'])
def tenant1upload_filestream():
   if request.method == 'POST':
      f = request.files['file']
      f.save('/app/clientStreamIngestApp1.xml')
      return 'file uploaded successfully'

# ----------------------------------------------------------------------------------------------------------------------
streamapp2 = clientStreamIngestApp('clientStreamIngestApp2', 'clientStreamIngestApp2.xml')
@app.route("/tenant2/deploystream")
def tenant2deploystream():
    steammanager.deploy_app(streamapp2)
    return f"clientSteamIngestApp deployed and connected to BatchIngestPutCassandraQL"

@app.route("/tenant2/schedulestreamON")
def tenant2schedulestreamON():
    steammanager.schedule_ON(streamapp2)
    return f"clientStreamIngestApp scheduled to run"

@app.route("/tenant2/schedulestreamOFF")
def tenant2schedulestreamOFF():
    steammanager.schedule_OFF(streamapp2)
    return f"clientStreamIngestApp scheduled to stop"

@app.route("/tenant2/metricsstream")
def tenant2metricsstream():
    stats = steammanager.get_metrics(streamapp2)
    return stats

@app.route('/tenant2/uploaderstream', methods = ['GET', 'POST'])
def tenant2upload_filestream():
   if request.method == 'POST':
      f = request.files['file']
      f.save('/app/clientStreamIngestApp2.xml')
      return 'file uploaded successfully'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)
    
