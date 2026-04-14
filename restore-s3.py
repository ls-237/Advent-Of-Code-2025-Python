import botocore
from boto3 import client
from datetime import datetime, timezone

conn = client('s3')

# --- Configuration ---
# Target S3 bucket for restoration
Bucket = ""
# Optional prefix filter. Leave empty "" to process the entire bucket
Prefix = ""

# Cutoff date: only restore objects modified AFTER this date
CUTOFF_DATE = datetime(2025, 12, 25, tzinfo=timezone.utc)

# Paginate through all objects in the bucket/prefix
paginator = conn.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=Bucket, Prefix=Prefix, PaginationConfig={
                               'MaxItems': 1000,
                               'PageSize': 1000,
                           })

for page in pages:
    for object in page['Contents']:
        # Skip objects modified on or before Dec 25, 2025
        if object['LastModified'] <= CUTOFF_DATE:
            print(f"Skipping {Bucket}/{object['Key']} — last modified {object['LastModified']} is before cutoff date.")
            continue

        try:
            # Only restore objects in GLACIER or DEEP_ARCHIVE storage classes
            # Change 'Standard' to 'Expedited' below for faster (but costlier) retrieval
            if object['StorageClass'] in ('GLACIER', 'DEEP_ARCHIVE'):
                restore = conn.restore_object(
                    Bucket=Bucket,
                    Key=object['Key'],
                    RestoreRequest={
                        'Days': 15,
                        'GlacierJobParameters': {'Tier': 'Standard'}
                    }
                )
                print(restore)
                print(f"Starting restore for {Bucket}/{object['Key']}")
            else:
                print(f"{Bucket}/{object['Key']} not in Glacier, skipping.")

        # Handle case where a restore is already in progress for this object
        except botocore.exceptions.ClientError as err:
            if err.response['Error']['Code'] == 'RestoreAlreadyInProgress':
                print(f"Restore already in progress for {Bucket}/{object['Key']}")
                continue

print(f"Restoration initiated for eligible objects in s3://{Bucket}/{Prefix}")
 
