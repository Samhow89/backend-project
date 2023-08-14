from google.cloud import compute_v1
from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS 
from flask_httpauth import HTTPBasicAuth
import bcrypt
import time
from google.cloud import monitoring_v3
from datetime import datetime



project_id = 'project-389915'
zone = 'europe-west2-c'

#Login details to access the api
USERNAME = "admin"
# Hashed password for "password123"
PASSWORD = "$2b$12$lyR1usJNQWDo6ciYe/NBoO8co2urbyK4OHK7jhlVNqRPyCM9v5cyW"


compute_client = compute_v1.InstancesClient()
instances = compute_client.list(project=project_id, zone=zone)

VMs = {}


app = Flask("GCPInstancesAPI")
api = Api(app)
CORS(app)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    return username == USERNAME and bcrypt.checkpw(password.encode('utf-8'), PASSWORD.encode('utf-8'))

# I did not write this function myself
def cpu_utilization(project_id, zone, instance_id):
    client = monitoring_v3.MetricServiceClient()
    metric_type = "compute.googleapis.com/instance/cpu/utilization"
    resource_name = f"projects/{project_id}/zones/{zone}/instances/{instance_id}"
    interval = monitoring_v3.TimeInterval({"end_time": {"seconds": int(time.time())}, "start_time": {"seconds": int(time.time() - 3600)}})

    metric_results = client.list_time_series(name=f"projects/{project_id}", filter=f'resource.type="gce_instance" AND resource.label.instance_id="{instance_id}" AND metric.type="{metric_type}"', interval=interval, view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL)

    for result in metric_results:
        latest_point = result.points[-1]
        utilization = latest_point.value.double_value
        timestamp_seconds = latest_point.interval.end_time.timestamp_pb().seconds + latest_point.interval.end_time.timestamp_pb().nanos / 1e9
        timestamp = datetime.fromtimestamp(timestamp_seconds).strftime('%Y-%m-%d %H:%M:%S')
        return(f"{utilization:.2f}%") 



for instance in instances:
    VMs[instance.name] = {
        'Instance ID': instance.id,
        'CPU utilization': cpu_utilization(project_id, zone, instance.id),
        'Creation date': instance.creation_timestamp[:10],
        'Disk size': f"{instance.disks[0].disk_size_gb}GB",
        'External IP': instance.network_interfaces[0].access_configs[0].nat_i_p,
        'Status': instance.status,
        'OS': instance.disks[0].licenses[0].split('/')[-1]
        }
    


class VM(Resource):
    
    method_decorators = [auth.login_required]
    
    def get(self, instance_name=None):
        if instance_name is None:
            return jsonify(VMs)
        return jsonify(VMs[instance_name])
    
api.add_resource(VM, '/', '/<string:instance_name>')

if __name__ == '__main__':
    app.run()