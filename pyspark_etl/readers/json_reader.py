# Reads every *.json file under a folder recursively
class JsonFolderReader:

    @staticmethod
    def read(spark, folder_path, schema=None):
        reader = spark.read.option("multiLine", True).option("recursiveFileLookup", True)

        if schema is not None:
            reader = reader.schema(schema)

        return reader.json(str(folder_path))