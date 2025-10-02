# hrb_communication.py

import ujson
import hrb_config

def send_data(moisture,temperature,humidity):
    # Create Python dictionary
    data_dict = {
        "moisture": round(moisture, 1),
        "temperature": temperature,
        "humidity": humidity
    }

    # Convert dictionary into a JSON txt string
    json_string = ujson.dumps(data_dict)

    # Send JSON sting and then a new line
    print(f"Sended: {json_string}")
    hrb_config.uart.write(json_string + '\n')
