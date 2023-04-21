import boto3

def success() -> dict:
  """Lambda success response
  """
  return {
      "statusCode": 200,
      "body": "SUCCESS"
  }

def error() -> dict:
  """Lambda error response
  """
  return {
      "statusCode": 500,
      "body": "ERROR"
  }

def init_client():
  """Init AWS client object.
  """
  global client
  client = boto3.client('ec2')

def get_ec2_instances() -> list:
  """Looking EC2 concerned, meaning looking for ec2 with tag "soloio:autoscaledown:ec2" set to true.
  """
  ret_instances = []

  global client

  instances = client.describe_instances(Filters=[
    {
      'Name': 'tag:soloio:autoscaledown:ec2',
      'Values': ['true']
    },
    {
      'Name': 'instance-state-name',
      'Values': ['running']
    }
  ])

  if len(instances["Reservations"]) > 0:
    for i in instances["Reservations"][0]["Instances"]:
      ret_instances.append(i["InstanceId"])

  return ret_instances

def stop_instances(instance_ids:list = []) -> bool:
  """Stop all instances identified by instance_ids.
  """
  global client
  
  ret = True
  try:
    if len(instance_ids) > 0:
      print(f'Stopping EC2s : {instance_ids}')
      client.stop_instances(InstanceIds=instance_ids)

  except Exception as e:
    print(f'Instances could not be stopped : {e}')
    ret = False

  return ret

def lambda_handler(event, context):
  # Init AWS client
  init_client()

  # Getting all clusters
  ec2s_to_stop = get_ec2_instances()

  # Launching the scale down
  if stop_instances(ec2s_to_stop):
    return success()
  else:
    return error()
