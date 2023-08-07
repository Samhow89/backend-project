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


from flask import Flask
from flask_restful import Resource, Api 

app = Flask("GCPInstancesAPI")
api = Api(app)


VMs = {
}


for instance in instances:
    VMs[instance.name] = {'Status': instance.status}

class VM(Resource):
    
    def get(self, instance_name=None):
        if instance_name is None:
            return VMs
        return VMs[instance_name]
    
api.add_resource(VM, '/', '/<string:instance_name>')

if __name__ == '__main__':
    app.run()