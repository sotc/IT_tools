#! /usr/bin/python
import subprocess
import shutil
import os
import zipfile
import json
import boto3
from boto3.s3.transfer import S3Transfer

# Create transfer object
client = boto3.client('s3', 'us-west-2')
transfer = S3Transfer(client)

class GetConfig():
    """ Parse json file
    """

    with open('nuke_config_list.json') as json_data:
        data = json.load(json_data)
    bucket = data["location"]["bucket"]
    nuke_lic = data["server_info"]["lic_server"]
    nuke_exec = data["location"]["nuke_exec"]
    nuke_file = os.path.basename(data["nuke"]["install"])
    flutil = os.path.basename(data["nuke"]["flu"])
    rlm_path = os.path.dirname(data["sys_path"]["rlm_path"])
    nuke_path = os.path.dirname(data["sys_path"]["nuke_path"])
    local_path = os.path.dirname(data["location"]["source"])

def download_from_bucket():
    """ Pull down files from S3 bucket.
    """

    bucket_files = GetConfig()
    for key, filename in bucket_files.data['nuke'].items():
        filename = os.path.basename(filename)
        full_path = os.path.join(bucket_files.local_path, filename)
        print('BucketName: %s  KeyName: %s PathName: %s' % (bucket_files.bucket, filename, full_path))
        transfer.download_file(bucket_files.bucket, filename, full_path)

def install_files():
    """ Unzip and install Nuke
    """

    json_data = GetConfig()
    nuke_tmp = os.path.join(json_data.local_path, json_data.nuke_file)
    flu_tmp = os.path.join(json_data.local_path, json_data.flutil)
    flu_exec = os.path.join(json_data.rlm_path, json_data.flutil)
    #print('Source: %s Destination: %s RLMpath: %s FLUtility: %s' % (nuke_tmp, json_data.nuke_path, json_data.rlm_path, flu_tmp))
    shutil.move(flu_tmp, json_data.rlm_path)
    zipfile.is_zipfile(nuke_tmp)
    zip_ref = zipfile.ZipFile(nuke_tmp, 'r')
    zip_ref.extractall(json_data.nuke_path)
    zip_ref.close()
    print "Changing permissions and licensing nuke"
    os.chmod(json_data.nuke_exec, 0744)
    os.chmod(flu_exec, 0744)
    args = '-c %s' % (json_data.nuke_lic)
    cmd = "%s %s" % (flu_exec, args)
    print cmd
    subprocess.call(cmd, shell=True)

def create_paths():
    """ Create paths for Nuke and FLU
    """

    path_data = GetConfig()
    for key, spath in path_data.data['sys_path'].items():
        print("sPath %s" % (spath))
        if not os.path.exists(spath):
            os.makedirs(spath)

def main():
    """ Runs the whole program
    """

    create_paths()
    download_from_bucket()
    install_files()

if __name__ == '__main__':

    main()
