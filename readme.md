# Store Monitoring
This assignment will help identify restaurant owners identify how frequently their stores go offline. The assignment was built using Fast API and PostgreSQL.

The link to the demo is at [demo](https://www.loom.com/share/93028c52c5394195bd6e2a0fa26b0ef2?sid=4bed3565-1514-4e17-92b8-cfc0c2da7c46) 

## Data Cleaning
I did some EDA on all three datasets and found values that were absent in some of the datasets.
There were few stores that were present in business hour and timezone data that were missing from store data. Such data was removed. There were few stores that were present in stores but absent in business hour and timezone data. Such data was added according to the conditions specified in the task. (Timezone - America/Chicago , Business Hour - 00:00:00 - 23:59:59)
In the business hour dataset , there were some stores that contained data that were not accurate. For example, store with `id = 1481966498820158979` contained multiple business hours for each day of the week that were innacurate. It showed that the store was open from 00:00:00 to 00:10:00 and from 11:00:00 to 23:59:00 on Monday. Such duplicate and innacurate entries were removed.
After cleaning the datasets they were stored to the postgreql database.


## Computing uptime and downtime 
The logic for computing uptime and downtime for the last_hour, last_day, last_week is similar.
We iterate through the poll data of each store that is between the required time interval ( one hour or one day or one week ) and if the poll time is between the opening and closing time of the store for that day. We calculate the time difference between the points.

I will explain it with last_hour as example in detail below.
- The current datetime is hard coded to be the max poll time from store data. 
- time_one_hour_ago is calculated from the current datetime.
- all store_ids are queried from the timezone database
- We iterate through each store_id.
- The timezone of the store is retrieved.
- The poll data for a store that is between current time and time_one_hour_ago is queried from the database and sorted by ascending order wrt timestamp
- The current local time and local time_one_hour_ago is calculated using the timezone value.
- The opening and closing time for the store for that day is queried from the database
- If the poll time for a store is not within the opening and closing time, it is ignored.
- If the poll time for a store is within the opening and closing time, the time difference between the poll time and the opening time is calculated. 
- Once the loop iterates over the next poll time, the time difference between the current poll time and the previous poll time is calculated if current poll time is within the opening time and the closing time.
- The loop interates over every poll time and does the same.
- The time difference between the last poll time and the closing time or curent time (whichever is smaller) is calculated.
- The status of the poll is also checked upon each iteration and the time difference is added to uptime is status is active , else to downtime.

### Example
Question
- business hours for a store are 9 AM to 12 PM on Monday. We only have 2 observations for this store on a particular date (Monday) in our data at 10:14 AM and 11:15 AM

Answer
- For last hour

    - For the sake of simplicity, I am not using timezones here. Assume the current time is 11 AM. We fetch only the data that is between current time and time one hour ago i.e 10:00 AM to 11:10 AM . Here the only data between them is at 10:15. We check if 10:15 is within store timing. Here it is. We calculate the time difference between time_one_hour_ago and 10:15. If the status at 10:15 is active then the time difference for that period is added to uptime, else downtime. Then the time difference between 10:15 to 11:00 is calculated. Since there are no other poll data, if the prev status is active, the time difference is added to uptime , else donwtime.

- For last day
    - The current time is 11 AM on Monday. The datetime one day ago is 11 AM Sunday. We fetch poll data within that time frame. Let us assume the same observations exist for Sunday as well. So the available poll data within the time frame are 11:15 AM Sunday and 10:14 AM Monday. The time difference between time one day ago or opening time (whichever is greater) and 11:15 is calculated. Here it is 11:00 AM Sunday to 11:15 AM Sunday. Status is checked and uptime/downtime is calculated. Then the time difference between 11:15 and closing time is calculated and uptime/downtime is calculated. Then the time difference between opening time to 10:14 AM Monday is calculated and then and between 10:14 to 11:00 AM Monday.

## Running the store monitor

### clone the repository
    git clone https://github.com/johntharian/store-monitoring.git
### open the repository
    cd store-monitoring
#### create a virtual environment using conda
    conda create --name store_env
### activate the virtual environment
    conda activate store_env
### install pip 
    conda install pip
### install the required packages from requirements.txt
    pip install -r requirements.txt
## To run the store monitor
    python main.py 


# Tasks

-   /trigger_report endpoint that will trigger report generation from the data provided (stored in DB)
    - No input 
    - Output - report_id (random string) 
    - report_id will be used for polling the status of report completion
-   /get_report endpoint that will return the status of the report or the csv
    - Input - report_id
    - Output
        - if report generation is not complete, return “Running” as the output
        - if report generation is complete, return “Complete” along with the CSV file with the schema described above.

# Problems Faced
- The time taken to calculate uptime and downtime is very high for large number of store_ids even when using multi threading