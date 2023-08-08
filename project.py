##########################################################################
from google.cloud import compute_v1
# Create a Compute Engine client
compute_client = compute_v1.InstancesClient()

# Project ID of your GCP project
project_id = 'project-389915'

# Zone where the instances are running, e.g., 'europe-west2-c'
zone = 'europe-west2-c'

# Call the API to list instances in the specified zone 
instances = compute_client.list(project=project_id, zone=zone)
instances_list = list(compute_client.list(project=project_id, zone=zone))
##########################################################################


from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS 
from flask_httpauth import HTTPBasicAuth

app = Flask("GCPInstancesAPI")
api = Api(app)
CORS(app)
auth = HTTPBasicAuth()

# Define your username and password
USERNAME = "admin"
PASSWORD = "password123"

# Basic authentication callback
@auth.verify_password
def verify_password(username, password):
    return username == USERNAME and password == PASSWORD


VMs = {
}


for instance in instances:
    VMs[instance.name] = {'Status': instance.status, 'External IP': instance.network_interfaces[0].access_configs[0].nat_i_p}

class VM(Resource):
    
    method_decorators = [auth.login_required]
    
    def get(self, instance_name=None):
        if instance_name is None:
            return jsonify(VMs)
        return jsonify(VMs[instance_name])
    
api.add_resource(VM, '/', '/<string:instance_name>')

if __name__ == '__main__':
    app.run()