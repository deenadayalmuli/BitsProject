from pyspark.sql import SparkSession


spark = SparkSession.builder \
    .appName("Data PreProcessing") \
    .getOrCreate()
    
    
    
    
    
    
    
    
course_df = spark.read.csv('/user/hadoop/dataset/synthetic_txn_data_new_1.csv',header='true')


course_df.count()





from pyspark.sql.functions import col,isnan, when, count
course_df.select([count(when(isnan(c) | col(c).isNull(), c)).alias(c) for c in course_df.columns]).show()




#drop duplicates: 

dist_course_df = course_df.distinct()
print("Distinct count: "+str(dist_course_df.count()))
dist_course_df.show(truncate=False)




#Drop duplicates
course_df_dropdup = dist_course_df.dropDuplicates()
print("Distinct count: "+str(course_df_dropdup.count()))
course_df_dropdup.show(truncate=False)


course_df_dropdup.count()

   
   
Null values removal:  
   
from pyspark.sql.functions import col,isnan,when,count
course_df1 = course_df_dropdup.select([count(when(col(c).contains('None') | \
                            col(c).contains('NULL') | \
                            (col(c) == '' ) | \
                            col(c).isNull() | \
                            isnan(c), c 
                           )).alias(c)
                    for c in course_df.columns])
                    
                    
   
   


course_df1 = course_df_dropdup.dropna()

course_df1.count()






#Z-score Outlier removal:

from pyspark.sql.types import IntegerType,DoubleType

from  pyspark.sql.functions import col

course_df1 = course_df1.withColumn("Amount", course_df1["order_price"].cast(DoubleType()))\
						.drop(course_df1["order_price"])



from pyspark.sql.functions import *
column_subset = course_df1.columns
for col in column_subset:
    if course_df1.select(col).dtypes[0][1]=="string":
        pass
    else:
        print("column"+col)
        mean1 = course_df1.select(mean(col)).collect()[0][0]
        print("mean1 "+str(mean1))
        stddev = course_df1.select(stddev(col)).collect()[0][0]
        print("stddev "+str(stddev))
        upper_limit = mean1 + (3*stddev)
        print("upper_limit "+str(upper_limit))
        lower_limit = mean1 - (3*stddev)
        print("lower_limit "+str(lower_limit))
        dataframe = course_df1.filter((course_df1[col]>lower_limit) & (course_df1[col]<upper_limit))
        
        
dataframe.count()
dataframe.show()



dataframe = dataframe.dropDuplicates()

course_df1.count()


dataframe.coalesce(1).write.csv("/user/hadoop/dataset/synthetic_txn_data_new_preprocessed.csv",header='true')

