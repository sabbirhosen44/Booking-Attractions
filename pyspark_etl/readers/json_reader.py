# Reads every *.json file under a data folder

def read_json_folder(spark, folder_path, schema=None):
    reader = spark.read.option("multiLine", True).option("recursiveFileLookup", True)

    if schema is not None:
        reader = reader.schema(schema)

    return reader.json(str(folder_path))