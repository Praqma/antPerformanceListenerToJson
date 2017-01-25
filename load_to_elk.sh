#!/usr/bin/env bash

IP=$1
FILE=$2
INDEX=${3:-antprofiler}
MAPPINGS="mappings.json"
MESSAGE="Please run the command as follow: ${0} <elk ip> <file with data to upload> <index name, optional, default:AntProfiler>"

if [ -z "${IP}" ] || [ -z "${FILE}" ]
then
  echo ${MESSAGE}
  exit 1
fi

echo "Create mappings from ${MAPPINGS}"
curl -XPUT http://${IP}:9200/${INDEX} --data-binary "@${MAPPINGS}"

echo "Load data from ${FILE}"
curl -H "Expect:" -XPOST "${IP}:9200/${INDEX}/_bulk?pretty" --data-binary "@${FILE}"
