import re

class JsonUtils():
    
    re_table_name_json_path = r'(.*)->(.*)'
    re_json_field_index = r'(.+?)\[(\d+)\]'
    
    def obtain_value_from_path(json, path):
        
        keys = path.split('.')
        keys = [k.replace('[', '.').replace(']', '') for k in keys]
        
        value = json
        for key in keys:
            if '.' in key:
                field_idx = key.split('.')
                value = value.get(field_idx[0])[int(field_idx[1])]
            elif value != None:
                value = value.get(key)
        
        return value if value != json else None
    
    def obtain_value_from_path_unordered(json, path_return, related_fields, related_values):
        
        keys = path_return.split('.')
        relKeys = related_fields.split('@@')
        relValues = related_values.split('@@')

        if(len(relKeys) != len (relValues)):
            print("\nThe amount of relative values does not match the amount of relative fields!")
            return None
        
        rel_idx = 0
        value = json

        for key in keys:
            if '[?]' in key:
                field = key[:-3]
                value = value.get(field)
                relIdKeys = relKeys[rel_idx].split('&&&')
                relIdValues = relValues[rel_idx].split('&&&')

                matches = 0
                for item in value:

                    for idx, subKey in enumerate(relIdKeys):

                        if item[subKey] != relIdValues[idx]: break
                        else: matches+=1

                    if(matches == len(relIdKeys)):
                        value = item
                        break
                    else: matches = 0
                
                if(matches == 0):
                    print("\nNo value found corresponding to keys {}.".format(relIdKeys))
                    return None
                
                if(rel_idx+1 < len(relKeys)):
                    rel_idx+=1

            elif value != None:
                value = value.get(key)
        
        return value if value != json else None

    def format_select_query_column(expected_column_db):
        if "->" not in expected_column_db:
            return expected_column_db
        
        matches = re.match(JsonUtils.re_table_name_json_path, expected_column_db)
        table = matches.group(1)
        path_json = matches.group(2)
        fields_json = path_json.split(".")
        
        select = table
        for field in fields_json:
            if "[" in field:
                matches = re.match(JsonUtils.re_json_field_index, field)
                select += "->'{}'->{}".format(matches.group(1), matches.group(2))
            else:
                select += "->'{}'".format(field)
        
        return select