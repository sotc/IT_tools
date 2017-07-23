import os
import click
import boto3
from boto3.s3.transfer import S3Transfer

# Create Transfer object
s3client = boto3.client('s3', 'us-west-2')
s3resource = boto3.resource('s3')
transfer = S3Transfer(s3client)


@click.group()
def cli():
    """
    S3 directory structure copy 
    """

    click.echo("Verbosity has been set to %s" % ("on" if debug else "off"))

def create_paths(pathname):
    """
    Creates directory paths
    """

    print(pathname)
    if not os.path.exists(pathname):
        os.makedirs(pathname)

def get_subdir(bucket, subdir, dest):
    """
    Downloads all objects from an S3 bucket 
    """

    paginator = s3client.get_paginator('list_objects_v2')
    for result in paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=subdir):
        if result.get('CommonPrefixes') is not None:
            for subdir in result.get('CommonPrefixes'):
                #print(os.path.join(dest, subdir.get('Prefix')))
                create_paths(os.path.join(dest, subdir.get('Prefix')))
                get_subdir(bucket, subdir.get('Prefix'), dest)
        if result.get('Contents') is not None:
            for files in result.get('Contents'):
                filename = os.path.basename(files.get('Key'))
                if not filename == "":
                    s3_path = files.get('Key')
                    local_path = os.path.join(dest, s3_path)
                    #print(s3_path, local_path)
                    transfer.download_file(bucket, s3_path, local_path)

@cli.command("download")
@click.argument("bucket", nargs=1)
@click.argument("dest", nargs=1)
def download_files(bucket, dest):
    """
    Commandline interface to initiate s3 downloads
    """

    #click.echo(bucket)
    if not os.path.isdir(dest):
        print ("readable_dir:{0} is not a valid path".format(dest))
        print "Invalid Destination"
    else:
        paginator = s3client.get_paginator('list_objects_v2')
        for result in paginator.paginate(Bucket=bucket, Delimiter='/'):
            if result.get('CommonPrefixes') is not None:
                for subdir in result.get('CommonPrefixes'):
                    #click.echo(subdir.get('Prefix'))
                    get_subdir(bucket, subdir.get('Prefix'), dest)

def upload_to_s3(bucket, files):
    """
    s3 upload directory structure
    """

    key_file = files.strip("/")
    #print(files, bucket, key_file)
    transfer.upload_file(files, bucket, key_file)


@cli.command("upload")
@click.argument("bucket", nargs=1)
@click.argument("src", nargs=1)
def upload_files(bucket, src):
    """
    Upload directory structure to bucket
    """

    for dir_path, dir_name, file_name in os.walk(src):
        dir_name = dir_name
        for name in file_name:
            upload_to_s3(bucket, (os.path.join(dir_path, name)))
            #click.echo(os.path.join(dir_path, name))

@cli.command("list_buckets")
def list_bucket():
    """
    List all buckets
    """

    for bucket in s3resource.buckets.all():
        click.echo(bucket.name)

@cli.command("bucket_contents")
@click.argument("bucket_name", nargs=1)
def list_bucket_contents(bucket_name):
    """
    List contents of a bucket
    """

    click.echo("Your bucket name: %s" % (bucket_name))
    for obj in bucket_name.objects.all():
        click.echo(obj.key)


if __name__ == '__main__':
    cli()
