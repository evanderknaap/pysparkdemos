## README 

A demo of streaming fake sensory data to pubsub.

## SETUP 
### Run the the script to generate fake message 

``` bash
source env/bin/activate
python publish.py 
```

### DEMO notes
Build a batch pipeline (SAP CSV on GCS)
    Explore [ ] hamburger menu: (SDK) 
                Portable (SDK, management)
                pipelines, studio, wrangler & metadata 
                Explore local data export
    
            SAP export
                Deploy
                Clean (missing values, filtering)
                JavaScript 
                Join
                JDBC connector 
            BigQuery
                Count the join

Deploying a pipeline
    Show the summary 
    Show the pipelines

Real-time
    Time series features
    Error cleaning
    Aggregate windows  [30sec]
    Metadata 

