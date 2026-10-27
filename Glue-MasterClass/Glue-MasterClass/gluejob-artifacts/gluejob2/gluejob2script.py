# OURS: adapted from the Udemy course "AWS Glue: The Complete Masterclass".
# No names to change in the code: both locations arrive as job arguments. Ours are
#   --s3_source_bucket       bucket101pb/gluejob2-source
#   --s3_destination_bucket  bucket101pb/etl-targets/gluejob2
# Each is "bucket/prefix" rather than a bare bucket name. That works because the
# script only drops them into "s3a://{0}/..." strings.
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
import sys
import datetime


print('Process Started')
print('Reading the argument')

# Reading the parameter
args = getResolvedOptions (sys.argv,['s3_source_bucket','s3_destination_bucket'])
source_bucket = args['s3_source_bucket']
target_bucket = args['s3_destination_bucket']
print(source_bucket)


# Create the Spark Context
glue_context = GlueContext(SparkContext())
spark = glue_context.spark_session
extracted = datetime.datetime.today().strftime('%Y-%m-%d')

# Read and Write data
df = spark.read.format("csv").option("header",True).load("s3a://{0}/*".format(source_bucket))
df = df.filter( (df.Country == "Algeria") & (df.City == "Algiers") & (df.Year > 2016) )
df.write.mode('overwrite').partitionBy("Year").parquet("s3a://{0}/extracted_date={1}/".format(target_bucket, extracted))


