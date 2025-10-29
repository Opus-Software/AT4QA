import zulu
import uuid
import crcmod
import time
import string
import random
import datetime
from test_classes.Storage import Storage
from common.utils.StringUtils import StringUtils

class Generators():

    def generate_uuid(storage_field):
        
        print("\n #################### Generating UUID #################### ")
        
        Storage.storage[storage_field] = uuid.uuid4()
        print("\nNew UUID generated: {}. Successfully stored in field: {}".format(Storage.storage[storage_field], storage_field))

    def generate_formatted_time(time, format, storage_field):

        print("\n #################### Generating time {} in format {} #################### ".format(time, format))

        if format == "zuluex":
            date = zulu.now()
            if(len(time.split(" "))> 1 and (time.split(" ")[1] == "ago")):
                date = date.subtract(seconds=int(time.split()[0]))
            elif(len(time.split(" "))> 1 and (time.split(" ")[1] == "ahead")):
                date = date.add(seconds=int(time.split()[0]))
        elif format == "zuluz":
            date = zulu.now()
            if(len(time.split(" "))> 1 and (time.split(" ")[1] == "ago")):
                date = date.subtract(seconds=int(time.split()[0]))
            elif(len(time.split(" "))> 1 and (time.split(" ")[1] == "ahead")):
                date = date.add(seconds=int(time.split()[0]))
            date = (str(date).split(".")[0] + "Z")
        elif format == "epoch":
            date = time.time()
            if(len(time.split(" "))> 1 and (time.split(" ")[1] == "ago")):
                date = date - float(time.split()[0])
            elif(len(time.split(" "))> 1 and (time.split(" ")[1] == "ahead")):
                date = date + float(time.split()[0])
        elif format.split("@@")[0] == "datetime":
            date = datetime.datetime.now()
            if(len(time.split(" "))> 1 and (time.split(" ")[1] == "ago")):
                date = date - datetime.timedelta(seconds=int(time.split()[0]))
            elif(len(time.split(" "))> 1 and (time.split(" ")[1] == "ahead")):
                date = date + datetime.timedelta(seconds=int(time.split()[0]))
            date = date.strftime(format.split("@@")[1])

        Storage.storage[storage_field] = date
        print("\nNew time in format {} generated: {}. Successfully stored in field: {}".format(format, Storage.storage[storage_field], storage_field))

    def generate_string(string_size, storage_field):
        
        print("\n #################### Generating random string of size {} #################### ".format(string_size))
        Storage.storage[storage_field] = ''.join(random.choice(string.ascii_letters) for i in range(int(string_size)))
        print("\nRandom string generated: {}. Successfully stored in field: {}".format(Storage.storage[storage_field], storage_field))

    def generate_crc(poly, init, xorValue, value_field, storage_field):
        value_field = StringUtils.replace_placeholder_value_with_stored_value(value_field, Storage.storage)
        print("\n #################### Calculating CRC with initial polynomial {} using initial value {} and XOR value {} for value {} and storing result in field {} #################### \n".format(poly, init, xorValue, value_field, storage_field))
        
        crc = crcmod.Crc(int(poly, 16), int(init,16), False, int(xorValue, 16))
        crc.update(value_field.encode("ascii"))
        Storage.storage[storage_field] = crc.hexdigest()

        print("\nCRC successfully stored in field {}!".format(storage_field))