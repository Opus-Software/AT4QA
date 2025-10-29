
import json
import requests
from dateutil.parser import parse
from test_classes.Storage import Storage
from common.utils.JsonUtils import JsonUtils
from common.utils.StringUtils import StringUtils
from common.utils.ReportUtils import ReportUtils
from common.utils.FieldBuilders import FieldBuilders

class APICalls():

    api_response = None

    def makes_api_call(verb, url, headers, params, api_payload):
        
        url = StringUtils.replace_placeholder_value_with_stored_value(url, Storage.storage)
            
        print("\n ================================== {} {}  ================================== ".format(verb, url))
        headers = FieldBuilders.build_json_object(headers, Storage.storage)
        params = FieldBuilders.build_json_object(params, Storage.storage)
        
        json_payload = None
        data_payload = None

        try:
            json.loads(api_payload)
            json_payload = FieldBuilders.build_json_object(api_payload, Storage.storage)
        except ValueError as e:
            data_payload = StringUtils.replace_placeholder_value_with_stored_value(api_payload, Storage.storage)

        if verb == "GET":
            APICalls.api_response = requests.get(url, params=params, headers=headers)
        elif verb == "POST":
            APICalls.api_response = requests.post(url, params=params, headers=headers, data=data_payload, json=json_payload)
        elif verb == "PUT":
            APICalls.api_response = requests.put(url, params=params, headers=headers, data=data_payload, json=json_payload)
        elif verb == "PATCH":
            APICalls.api_response = requests.patch(url, params=params, headers=headers, data=data_payload, json=json_payload)
        elif verb == "DELETE":
            APICalls.api_response = requests.delete(url, params=params, headers=headers, data=data_payload, json=json_payload)

        print("\nRequest Url ({}): {}".format(verb, str(APICalls.api_response.url)))
        print("\nRequest Headers: {}".format(str(headers)))
        
        if json_payload != None :
            print("\nRequest Body: {}".format(str(json.dumps(json_payload))))
        else:
            print("\nRequest Body: {}".format(str(data_payload)))
        print("\nResponse Status: {}".format(str(APICalls.api_response.status_code)))
        print("\nResponse Headers: {}".format(str(APICalls.api_response.headers)))

        if(len(APICalls.api_response.content) > 0):
            print("\nResponse body: {}".format(str(json.dumps(APICalls.api_response.json()))))
        else:
            print("\nResponse body: There is no response!")
        
        return APICalls.api_response

    def check_api_status_code(status_code):
        ReportUtils.print_debug("\n  #################### Checking status code #################### \n")
        ReportUtils.print_debug(f"Received status code = {APICalls.api_response.status_code} Expected status = {status_code}\n")
        return APICalls.api_response.status_code == int(status_code)

    def check_api_response_values(api_returned_field, api_return_origin, comparison_type, api_response_expected_values):

        print("\n #################### Checking response value(s) from the API call #################### \n")

        fields = api_returned_field.split("@@")
        expected_values = api_response_expected_values.split("@@")
        print("Checking value(s) from the field(s): {}".format(fields))
        
        returned_values = []
        for field in fields:    
            if api_return_origin == "body":
                returned_values.append(JsonUtils.obtain_value_from_path(APICalls.api_response.json(), field))
            elif api_return_origin == "header":
                returned_values.append(APICalls.api_response.headers[field])

        divergencies = []
        for idx, returned_value in enumerate(returned_values):
            expected_values[idx] = StringUtils.replace_placeholder_value_with_stored_value(expected_values[idx], Storage.storage)
            if ((comparison_type == "equals" and not str(returned_value) == str(expected_values[idx])) or 
                (comparison_type == "different" and str(returned_value) == str(expected_values[idx]))):
                print("Value expected as {}: {}. Value returned from field {} of {} in response: {}".format(comparison_type, expected_values[idx], fields[idx], api_return_origin, returned_value))
                divergencies.append(fields[idx])
            elif((comparison_type == "greater or equal" or comparison_type == "less or equal")):
                try: 
                    expected_value_parsed = parse(str(expected_values[idx]))
                    value_response_parsed = parse(str(returned_value))
                except ValueError:
                    expected_value_parsed = str(expected_values[idx])
                    value_response_parsed = str(returned_value)
                if ((comparison_type == "greater or equal" and not str(value_response_parsed) >= str(expected_value_parsed)) or 
                    (comparison_type == "less or equal" and not str(value_response_parsed) <= str(expected_value_parsed))):
                    print("Value expected as {}: {}. Value returned from field {} of {} in response: {}".format(comparison_type, expected_values[idx], fields[idx], api_return_origin, returned_value))
                    divergencies.append(fields[idx])
            
                
        if divergencies:
            print("\nThe following field(s) have divergent value from what's expected: {}".format(divergencies))
            return False
        else:
            print("\nValue(s) from the response match(es) the expected value(s)")
            return True

    def check_api_response_values_in_unordered_fields(field_response_api, field_related_api, value_related_api, value_expected_response_api):

        print("\n #################### Checking value of API response #################### \n")

        print("\nChecking field value: {}".format(field_response_api))
        print("\nRelative to the value(s): {}".format(value_related_api))
        print("\nRespectively relative to the field(s): {}".format(field_related_api))

        value_response = JsonUtils.obtain_value_from_path_unordered(APICalls.api_response.json(), field_response_api, field_related_api, value_related_api)

        value_expected_response_api = StringUtils.replace_placeholder_value_with_stored_value(value_expected_response_api, Storage.storage)
        print("Expected Value: {}. Value returned from field {} of response body: {}".format(value_expected_response_api, field_response_api, value_response))
        if not str(value_response) == str(value_expected_response_api):
            print("\nThe following field has a divergent value from what's expected: {}".format(field_response_api))
            return False
        else:
            print("\nValue(s) from the response match(es) the expected value(s)")
            return True

    def check_api_response_fields(api_returned_field, field_situation, api_return_origin):

        print("\n #################### Checking field(s) from the API response #################### \n")

        fields = api_returned_field.split("@@")
        situation = "presence" if field_situation == "present" else "absence"
        print("Checking {} of field(s): {}".format(situation, fields))

        result = True
        situation = "present" if field_situation == "present" else "absent"
        for field in fields:
            if api_return_origin == "body":
                if situation == "present" and JsonUtils.obtain_value_from_path(APICalls.api_response.json(), field) == None:
                    result = False
                    print("Field {} not found in body of API response".format(field))
                elif situation == "absent" and JsonUtils.obtain_value_from_path(APICalls.api_response.json(), field) != None:
                    result = False
                    print("Field {} found in body of API response".format(field))
            elif api_return_origin == "header":
                if situation == "present" and not field in APICalls.api_response.headers:
                    result = False
                    print("Field {} not found in header of API response".format(field))
                elif situation == "absent" and field in APICalls.api_response.headers:
                    result = False
                    print("Field {} found in header of API response".format(field))
        
        if result:
            print("\nThe expected field(s) is(are) {} in the API response".format(situation))

        return result