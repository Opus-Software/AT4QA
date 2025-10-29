from common.utils.JsonUtils import JsonUtils
from common.utils.StringUtils import StringUtils
from common.config.database.DatabaseConnection import DatabaseConnection

class Storage():

    storage = {}

    def store_api_response(api_field, field_origin, storage_field, api_response):
        print("\n #################### Storing value of field {} from {} of API response in field named {} #################### \n".format(api_field, field_origin, storage_field))
        
        if field_origin == "body":
            Storage.storage[storage_field] = JsonUtils.obtain_value_from_path(api_response.json(), api_field)
        elif field_origin == "header":
            Storage.storage[storage_field] = api_response.headers[api_field]
        
        print("Value {} stored in field {}".format(Storage.storage[storage_field], storage_field))

    def store_api_response_in_unordered_field(api_return_field, related_api_fields, related_values, storage_field, api_response):

        print("\n #################### Storing value of field {} from API response in field named {} #################### \n".format(api_return_field, storage_field))

        print("\nRelative to the value(s): {}".format(related_values))
        print("\nRespectively relative to the field(s): {}".format(related_api_fields))

        Storage.storage[storage_field] = JsonUtils.obtain_value_from_path_unordered(api_response.json(), api_return_field, related_api_fields, related_values)

        print("Value {} stored in field {}".format(Storage.storage[storage_field], storage_field))


    def store_response_field_database(db_name, query, storage_field):

        print("\n #################### Storing value returned on query {} from database {} in field named {} #################### \n".format(query, db_name, storage_field))

        DatabaseConnection.obtain_connection(db_name)
        query = StringUtils.replace_placeholder_value_with_stored_value(query, Storage.storage)
        print("\nExecuting query: {}".format(query))
        
        if not "where" in query:
            print("Only queries with 'where' conditionals can be executed!")
            return False
        
        if query.split(" ")[0] == "update" or query.split(" ")[0] == "delete":
            print("Only select queries can be executed with this statement!")
            return False
        
        result = DatabaseConnection.select_one(db_name, query)

        if(result != None and len(result) > 1 ):
            Storage.storage[storage_field] = result
        elif(result == None):
            Storage.storage[storage_field] = str(result)
        else:
            Storage.storage[storage_field] = str(result[0])
        print("\n{} stored in field {}".format(Storage.storage[storage_field], storage_field))