import redis
import psycopg2
import boto3
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

def test_connections():
    print("🚀 Starting Service Connectivity Tests...\n")

    # 1. Test Postgres
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host='localhost',
            port='5432'
        )
        print("✅ Postgres: Connected successfully.")
        conn.close()
    except Exception as e:
        print(f"❌ Postgres: Failed - {e}")

    # 2. Test Redis
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        if r.ping():
            print("✅ Redis: Connected successfully.")
    except Exception as e:
        print(f"❌ Redis: Failed - {e}")

    # 3. Test MinIO (S3 SDK)
    try:
        s3 = boto3.client(
            's3',
            endpoint_url='http://localhost:9000',
            aws_access_key_id=os.getenv('MINIO_ROOT_USER'),
            aws_secret_access_key=os.getenv('MINIO_ROOT_PASSWORD')
        )
        s3.list_buckets()
        print("✅ MinIO: Connected successfully.")
    except Exception as e:
        print(f"❌ MinIO: Failed - {e}")

    # 4. Test Neo4j
    try:
        uri = "bolt://localhost:7687"
        driver = GraphDatabase.driver(
            uri, 
            auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
        )
        with driver.session() as session:
            session.run("RETURN 1")
        print("✅ Neo4j: Connected successfully.")
        driver.close()
    except Exception as e:
        print(f"❌ Neo4j: Failed - {e}")

if __name__ == "__main__":
    test_connections()
