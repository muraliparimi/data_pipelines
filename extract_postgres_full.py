import psycopg2
import csv
import boto3
import configparser

parser = configparser.ConfigParser()
parser.read("pipeline.conf")
hostname = parser.get("postgres_config","hostname")
port = parser.get("postgres_config","port")
username = parser.get("postgres_config","username")
dbname = parser.get("postgres_config","database")
password = parser.get("postgres_config","password")

conn = psycopg2.connect("dbname=" + dbname + " user=" + username+ " password=" + password + " host=" + hostname, port = port)

if conn is None:
	print("Error connecting to the postgres database")
else:
	print("postgres connection established!")



# Extract Orders data into a csv file
m_query = "Select * from Orders;"
local_filename = "order_extract.csv"

m_cursor = conn.cursor()
m_cursor.execute(m_query)
results = m_cursor.fetchall()

with open(local_filename,'w') as fp:
	csv_w = csv.writer(fp, delimiter="|")
	csv_w.writerows(results)


fp.close()
m_cursor.close()
conn.close()


# Upload Extracted Orders file to S3 Bucket

parser = configparser.ConfigParser()
parser.read("pipeline.conf")
access_key = parser.get("aws_boto_credentials","access_key")
secret_key = parser.get("aws_boto_credentials","secret_key")
bucket_name = parser.get("aws_boto_credentials","bucket_name")

s3 = boto3.client('s3',aws_access_key_id=access_key, aws_secret_access_key = secret_key)

s3_file = local_filename

s3.upload_file(local_filename, bucket_name, s3_file)
