from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, to_date, expr
import argparse
def get_spark(): return SparkSession.builder.appName('ecom-etl').getOrCreate()
def bronze_to_silver(spark,input_path,silver_path):
    df=spark.read.json(input_path)
    df_items=df.select(col('order_id'),col('user_id'),col('email'),to_date(col('order_ts')).alias('event_date'),explode(col('items')).alias('item'),col('total'))
    df_items=df_items.select('order_id','user_id','email','event_date',col('item.product_id').alias('product_id'),col('item.name').alias('product_name'),col('item.qty').alias('qty'),col('item.unit_price').alias('unit_price'),'total')
    df_items.write.mode('overwrite').partitionBy('event_date').parquet(silver_path)
def silver_to_gold(spark,silver_path,gold_path):
    df=spark.read.parquet(silver_path)
    agg=df.groupBy('event_date').agg(expr('sum(qty * unit_price) as revenue'),expr('count(distinct order_id) as orders'),expr('sum(qty) as items_sold'))
    agg.write.mode('overwrite').partitionBy('event_date').parquet(gold_path)
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--input',required=True); p.add_argument('--silver',required=True); p.add_argument('--gold',required=True)
    args=p.parse_args(); spark=get_spark(); bronze_to_silver(spark,args.input,args.silver); silver_to_gold(spark,args.silver,args.gold); spark.stop()
