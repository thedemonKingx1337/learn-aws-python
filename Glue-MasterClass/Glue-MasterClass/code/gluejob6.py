# OURS: adapted from the Udemy course "AWS Glue: The Complete Masterclass".
# Changes from the course version are marked "OURS:".
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsgluedq.transforms import EvaluateDataQuality

from pyspark.sql.functions import udf,col
from pyspark.sql.types import IntegerType, StringType
from pyspark.sql import SQLContext
from pyspark.context import SparkContext
from pyspark.sql import functions as F

from datetime import datetime

# OURS: moved up from the bottom of the file. The UDF below is pickled and sent to
# the executors when it is first applied to a column. In the course version this
# table was defined after that point, so the lookup failed with NameError, the
# bare "except:" hid it, and country_code_2 came out NULL for every row.
COUNTRY_NAME_TO_COUNTRY_CODE = {
    'Abkhazia': 'AB',
    'Afghanistan': 'AF',
    'Albania': 'AL',
    'Algeria': 'DZ',
    'American Samoa': 'AS',
    'Andorra': 'AD',
    'Angola': 'AO',
    'Anguilla': 'AI',
    'Antigua and Barbuda': 'AG',
    'Argentina': 'AR',
    'Armenia': 'AM',
    'Aruba': 'AW',
    'Australia': 'AU',
    'Austria': 'AT',
    'Azerbaijan': 'AZ',
    'Bahamas': 'BS',
    'Bahrain': 'BH',
    'Bangladesh': 'BD',
    'Barbados': 'BB',
    'Belarus': 'BY',
    'Belgium': 'BE',
    'Belize': 'BZ',
    'Benin': 'BJ',
    'Bermuda': 'BM',
    'Bhutan': 'BT',
    'Bolivia': 'BO',
    'Bonaire': 'BQ',
    'Bosnia and Herzegovina': 'BA',
    'Botswana': 'BW',
    'Bouvet Island': 'BV',
    'Brazil': 'BR',
    'British Indian Ocean Territory': 'IO',
    'British Virgin Islands': 'VG',
    'Virgin Islands, British': 'VG',
    'Brunei': 'BN',
    'Brunei Darussalam': 'BN',
    'Bulgaria': 'BG',
    'Burkina Faso': 'BF',
    'Burundi': 'BI',
    'Cambodia': 'KH',
    'Cameroon': 'CM',
    'Canada': 'CA'}


def get_country_code2(country_name):
    # OURS: a plain lookup, returning None for names not in the table. The course
    # version wrapped it in a bare "except:", which hid the error described above.
    return COUNTRY_NAME_TO_COUNTRY_CODE.get(country_name)


udf_get_country_code2 = udf(lambda z: get_country_code2(z), StringType())

# Creating GlueContext
glueContext = GlueContext(SparkContext.getOrCreate())

# Creating Glue Dynamic Frame
dynaFrame = glueContext.create_dynamic_frame.from_catalog(database="database101", table_name="csv")

# Script generated for node Evaluate Data Quality
EvaluateDataQuality_ruleset = """
   Rules = [
    RowCount between 50000 and 200000,
    IsComplete "uuid",
    StandardDeviation "uuid" between 246354546.02 and 272286603.49,
    Uniqueness "uuid" > 0.95,
    ColumnValues "uuid" between 100008903 and 999996460,
    IsComplete "country",
    ColumnLength "country" between 3 and 33,
    IsComplete "item type",
    ColumnValues "item type" in ["Office Supplies", "Cereal", "Baby Food", "Cosmetics", "Personal Care", "Meat", "Snacks", "Clothes", "Vegetables", "Household", "Fruits", "Beverages"],
    ColumnValues "item type" in ["Office Supplies", "Cereal", "Baby Food", "Cosmetics", "Personal Care", "Meat", "Snacks", "Clothes", "Vegetables", "Household", "Fruits"] with threshold >= 0.91,
    ColumnLength "item type" between 3 and 16,
    IsComplete "sales channel",
    ColumnValues "sales channel" in ["Online", "Offline"],
    ColumnLength "sales channel" between 5 and 8,
    IsComplete "order priority",
    ColumnValues "order priority" in ["M", "L", "C", "H"],
    ColumnLength "order priority" = 1,
    IsComplete "order date",    
    ColumnValues "units sold" <= 1000
    ]
"""

EvaluateDataQuality_DQ_Results = EvaluateDataQuality.apply(
    frame=dynaFrame,
    ruleset=EvaluateDataQuality_ruleset,
    publishing_options={
        "dataQualityEvaluationContext": "EvaluateDataQualitydynaFrame",
        "enableDataQualityCloudWatchMetrics": True,
        "enableDataQualityResultsPublishing": True,
    },
)
EvaluateDataQualitydynaFrame = dynaFrame

assert (
    EvaluateDataQuality_DQ_Results.filter(
        lambda x: x["Outcome"] == "Failed"
    ).count()
    == 0
), "The job failed due to failing DQ rules for GlueJob 6"


# Converting Glue Dynamic Frame to Spark Data Frame
dataframe = dynaFrame.toDF()
dataframe.printSchema()
# Renaming Columns as it has extra space so replacing space with _
renamed_df = dataframe.select([F.col(col).alias(col.replace(' ', '_')) for col in dataframe.columns])
renamed_df.printSchema()
# Adding country code column and getting the code from the UDF and function created
# Filtering on AUstraling and writing back as parquet
new_df = renamed_df.withColumn('country_code_2', udf_get_country_code2(col("country")))
new_df_aus = new_df.filter("country == 'Australia'").limit(10)
# OURS: was s3://awsglueudemycourse-datasoup-etl-targets/gluejob1, job 1's folder.
# With mode('overwrite') this job would delete job 1's output, so it writes to
# its own folder now.
new_df_aus.write.mode('overwrite').parquet("s3://bucket101pb/etl-targets/gluejob6")
