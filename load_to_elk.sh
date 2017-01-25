#!/usr/bin/env bash

IP=$1
FILE=$2
INDEX=${3:-antprofiler}
MESSAGE="Please run the command as follow: ${0} <elk ip> <file with data to upload> <index name, optional, default:AntProfiler>"

if [ -z "${IP}" ] || [ -z "${FILE}" ]
then
  echo ${MESSAGE}
  exit 1
fi

curl -XPUT http://${IP}:9200/${INDEX} -d '
{
 "mappings" : {
  "_default_" : {
   "properties" : {
    "task_name" : {"type": "string" },
    "duration" : { "type" : "integer" },
    "timestamp" : { "type" : "date" }
   }
  }
 }
}
';

curl -XPOST "${IP}:9200/${INDEX}/_bulk?pretty" --data-binary @${FILE}
