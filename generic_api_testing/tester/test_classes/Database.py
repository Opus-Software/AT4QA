from test_classes.Storage import Storage
from common.utils.JsonUtils import JsonUtils
from common.utils.StringUtils import StringUtils
from test_classes.APICalls import APICalls
from common.config.database.DatabaseConnection import DatabaseConnection

class Database():
    
    def define_database_connection(name, host, port, user, password, database):
        
        print("\n #################### Defining database connection #################### \n")
        
        DatabaseConnection.define_connection(name, host, port, user, password, database)

        print("\nConnection with database {} defined successfully!".format(name))

    def check_database_column_value(database_name, database_table, database_analised_column, comparison, expected_value, query_where_column, query_where_column_type, query_where_value, field_name, field_origin):
        
        print("\n #################### Checking value in database {}, table {} #################### \n".format(database_name, database_table))

        DatabaseConnection.obtain_connection(database_name)
        
        query_where_value = Database.obtain_field_value(field_origin, field_name, query_where_value)
        where_field = "'{}'".format(query_where_value) if (query_where_column_type == "uuid" or query_where_column_type == "varchar") else query_where_value
        database_analised_column = JsonUtils.format_select_query_column(database_analised_column)
        
        query = "select {} from \"{}\" where \"{}\" = {}".format(database_analised_column, database_table, query_where_column, where_field)
        print("\nExecuting query: {}".format(query))
        query_result = DatabaseConnection.select_one(database_name, query)
        
        if query_result:
            query_result_value = "NULL" if query_result[0] == None else query_result[0]
            print("\nValue {} found successfully in column {}!".format(query_where_value, query_where_column))
            print("query_result from select: {}".format(query_result_value))
        else:
            print("\nValue {} not found in column {}!".format(query_where_value, query_where_column))
            return False

        if comparison == "equals to":
            if expected_value == "equal to where":
                return True
            elif expected_value == "empty":
                print("\nExpected value: {}. Obtained value from query: {}".format(expected_value, query_result_value))
                return query_result_value == "NULL"
            else:
                expected_value = StringUtils.replace_placeholder_value_with_stored_value(expected_value, Storage.storage)
                print("\nExpected value: {}. Obtained value from query: {}".format(expected_value, query_result_value))
                return str(query_result_value) == expected_value
        else:
            if expected_value == "equal to where":
                print("\nConfiguration error. The parameter '{}' should not be used with the parameter '{}'".format(comparison, expected_value))
                return False
            elif expected_value == "empty":
                print("\nValue should be different from: {}. Value obtained from query: {}".format(expected_value, query_result_value))
                return query_result_value != "NULL"
            else:
                expected_value = StringUtils.replace_placeholder_value_with_stored_value(expected_value, Storage.storage)
                print("\nValue should be different from: {}. Value obtained from query: {}".format(expected_value, query_result_value))
                return expected_value != query_result_value

    def update_database_column_value(database_name, database_table, update_column, update_column_type, update_field_column, update_value, update_value_type, database_column_where, database_column_where_type, where_value, field_name, field_origin):

        print("\n #################### Updating value in DB {}, table {}, column {} #################### \n".format(database_name, database_table, update_column))

        DatabaseConnection.obtain_connection(database_name)
        
        query_where_value = Database.obtain_field_value(field_origin, field_name, query_where_value)
        where_field = "'{}'".format(query_where_value) if (database_column_where_type == "uuid" or database_column_where_type == "varchar") else query_where_value
        set_field = None
        if update_column_type == "uuid" or update_column_type == "varchar":
            set_field = "'{}'".format(update_value)
        elif update_column_type == "jsonb":
            field_value = "'{}'".format(update_value) if (update_value_type == "uuid" or update_value_type == "varchar") else update_value
            set_field = "jsonb_set(\"" + update_column + "\", '{" + update_field_column + "}', '" + field_value + "')"
        else:
            set_field = update_value

        query = "update \"{}\" set \"{}\" = {} where \"{}\" = {}".format(database_table, update_column, set_field, database_column_where, where_field)
        print("\nExecuting a query: {}".format(query))
        DatabaseConnection.update(database_name, query)

        print("\nValue {} updated successfully in column {}!".format(update_value, update_column))

    def execute_database_query(database_name, query, expected_value):

        print("\n #################### Executing arbitrary query on DB {} #################### \n".format(database_name))

        DatabaseConnection.obtain_connection(database_name)
        query = StringUtils.replace_placeholder_value_with_stored_value(query, Storage.storage)
        print("\nExecuting query: {}".format(query))        
        
        if not "where" in query:
            print("Only 'where' queries can be executed!")
            return False
        
        if "update" in query or "delete" in query:
            DatabaseConnection.update(database_name, query)
            return True
        else:
            query_result = DatabaseConnection.select_one(database_name, query)
            if expected_value == "omitted":
                return True
            else:
                expected_value = StringUtils.replace_placeholder_value_with_stored_value(expected_value, Storage.storage)
                if(query_result is not None):
                    print("Expected Value: {}. Returned Value: {}".format(expected_value, str(query_result[0])))
                    return str(expected_value) == str(query_result[0])
                else:
                    print("Expected Value: {}. Returned Value: {}".format(expected_value, str(query_result)))
                    return str(expected_value) == str(query_result)

    def obtain_field_value(field_origin, field_name, field_value):

        if (field_origin == "response header"):
            field_value = APICalls.api_response.headers[field_name]
        elif (field_origin == "response body"):
            field_value = JsonUtils.obtain_value_from_path(APICalls.api_response.json(), field_name)
        
        return field_value