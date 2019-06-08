import boto3
import botocore
import click


session=boto3.Session(profile_name="demoProject")
ec2=session.resource('ec2')

def filter_instances(project):
	instances=[]

	if project:
		filters=[{'Name':'tag:Project','Values':[project]}]
		instances=ec2.instances.filter(Filters=filters)
	else:
		instances=ec2.instances.all()

	return instances

@click.group()
def cli():
	"""This program manages volumes and instances"""


@cli.group('volumes')
def volumes():
	"""Commands for Volumes"""

@volumes.command('list')
@click.option('--project',default=None,help="Only volumes for project (tag Project:<name>)")

def list_volumes(project):
	"List EC2 Volumes"

	instances=filter_instances(project)

	for i in instances:
		for v in i.volumes.all():
			print(', '.join([v.id,
							i.id,
							v.state,
							str(v.size)+"GiB",
							v.encrypted and "Encrypted" or "Not Encrypted"]))

	return

@cli.group('snapshots')
def snapshots():
	"""Commands for Snapshots"""

@snapshots.command('list')
@click.option('--project',default=None,help="Only snapshots for project (tag Project:<name>)")
@click.option('--all','list_all',default=False,is_flag=True,help="List all snapshots for the volume")

def list_snapshots(project,list_all):
	"List Snapshots for EC2 Volumes"

	instances=filter_instances(project)

	for i in instances:
		for v in i.volumes.all():
			for s in v.snapshots.all():
				print(', '.join([s.id,
							v.id,
							i.id,
							s.state,
							s.progress,
							s.start_time.strftime("%c")]))
				if (s.state == "completed" and not list_all): break
	return

@cli.group('instances')
def instances():
	"""Commands for Instances"""

@instances.command('snapshot')
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")

def create_snapshots(project):
	"Create snapshots for instances"

	instances=filter_instances(project)

	for i in instances:
		print("Stopping {0}...".format(i.id))
		i.stop()
		i.wait_until_stopped()
		for v in i.volumes.all():
			print("Creating snapshot of {0}...".format(v.id))
			v.create_snapshot(Description="Creating snapshot from program ec2-list.py")
		print("Starting {0}...".format(i.id))
		i.start()
		i.wait_until_running()
	return


@instances.command('list')
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")

def list_instances(project):
	"List Ec2 Instances"

	instances=filter_instances(project)

	for i in instances:
		tags={t['Key']:t['Value'] for t in i.tags or []}
		print(', '.join([
		 i.id,
		 i.instance_type,
		 i.placement['AvailabilityZone'],
		 i.state['Name'],
		 i.public_dns_name,
		 tags.get('Project', '<no project>')]))

	return

@instances.command('stop')
@click.option('--project',default=None, help="Stop Instances for project")

def stop_instances(project):
	"Stop EC2 Instances."

	instances=filter_instances(project)

	for i in instances:
		print("Stopping {0} ...".format(i.id))
		try:
			i.stop()
		except botocore.exceptions.ClientError as e:
			print ("Could not stop {0}...".format(i.id) + str(e))
	return

@instances.command('start')
@click.option('--project',default=None, help="Start Instances for project")

def start_instances(project):
	"Start EC2 Instances."

	instances=filter_instances(project)

	for i in instances:
		print("Starting {0}...".format(i.id))
		try:
			i.start()
		except botocore.exceptions.ClientError as e:
			print("Could not start {0}...".format(i.id) + str(e))
	return


if __name__ == '__main__':
	cli()
