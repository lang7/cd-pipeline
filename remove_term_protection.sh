#!/bin/bash

instanceids=$(aws ec2 describe-instances --region sa-east-1 | grep InstanceId | awk {'print $2'} | sed 's/[",]//g')

for id in ${instanceids} 
do 
    aws ec2 modify-instance-attribute --instance-id ${id} --no-disable-api-termination  --region sa-east-1 --profile lang7
done