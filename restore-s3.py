import csv
from boto3 import client
conn = client('s3')

#The intention of this script is to create a CSV inventory report for a customer
#This may be useful if a customer needs to run a batch op on a single prefix/bucket quickly
# and cannot wait for an inventory to be generated
#Optional prefix inventory


#Put Bucket Here
Bucket = ""
Prefix = ""

#Use Paginator ListV2 on specified bucket
paginator = conn.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=Bucket, Prefix=Prefix, MaxKeys=1000)

#Write to .Csv file named inventory.csv
#Interate through pages
#Write rows for Bucket name and object key to CSV file
with open('inventory1.csv', 'w') as file:
    for page in pages:
        for object in page['Contents']:
            #can add other columns here by adding for example to list storage class,
            #add ",(object['StorageClass'])
            key = [Bucket, (object['Key'])]
            print(key)
            csvwriter = csv.writer(file, delimiter=",")
            csvwriter.writerow(key)
