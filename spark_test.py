from pyspark.sql import SparkSession


spark = SparkSession.builder \
    .appName("MyApp") \
    .config("spark.master", "spark://localhost:7077") \
    .getOrCreate()

# Create a DataFrame and perform some operations
data = [("Alice", 25), ("Bob", 30), ("Charlie", 35)]
df = spark.createDataFrame(data, ["name", "age"])
df.show()

# Stop the SparkSession
spark.stop()
