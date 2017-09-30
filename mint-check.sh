#!/usr/bin/bash
declare startDate=`date --date="3 days ago" +"%m/%d/%Y"`
declare endDate=`date +"%m/%d/%Y"`
`"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" https://mint.intuit.com/transaction.event?startDate=$startDate\&endDate=$endDate`
