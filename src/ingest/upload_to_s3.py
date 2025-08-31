import os, boto3, argparse
def upload_folder(local_dir,bucket,prefix,endpoint=None,aws_key=None,aws_secret=None,region=None):
    s3_args={}
    if endpoint: s3_args['endpoint_url']=endpoint
    if aws_key and aws_secret: s3_args['aws_access_key_id']=aws_key; s3_args['aws_secret_access_key']=aws_secret
    if region: s3_args['region_name']=region
    s3=boto3.client('s3',**s3_args)
    for root,_,files in os.walk(local_dir):
        for fn in files:
            full=os.path.join(root,fn); rel=os.path.relpath(full,local_dir); key=f"{prefix}/{rel}"
            print(f"Uploading {full} to s3://{bucket}/{key}"); s3.upload_file(full,bucket,key)
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--local',required=True); p.add_argument('--bucket',required=True); p.add_argument('--prefix',default='bronze')
    p.add_argument('--endpoint',default=None); p.add_argument('--aws-key',default=None); p.add_argument('--aws-secret',default=None); p.add_argument('--region',default=None)
    args=p.parse_args(); upload_folder(args.local,args.bucket,args.prefix,args.endpoint,args.aws_key,args.aws_secret,args.region)
