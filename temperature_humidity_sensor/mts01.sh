// read status and configuration
curl --location --request POST "192.168.1.124/hardware/operation" --header 'Content-Type: application/json' --data-raw '{
    "event":"now",
    "actions": [["i2c", 0, "write", 20, 21, 50, 69, 243, 45, 0],["i2c", 0, "read", 20, 21, 50, 69, -1, -1, 3]]
}'

// single read
curl --location --request POST "192.168.1.124/hardware/operation" --header 'Content-Type: application/json' --data-raw '{
    "event":"now",
    "actions": [["i2c", 0, "write", 20, 21, 50, 69, 204, 68, 0],["i2c", 0, "read", 20, 21, 50, 69, -1, -1, 3]]
}'

// set repeat read
curl --location --request POST "192.168.1.124/hardware/operation" --header 'Content-Type: application/json' --data-raw '{
    "event":"now",
    "actions": [["i2c", 0, "write", 20, 21, 50, 69, 82, 6, 3, 12, 255, 153],["i2c", 0, "write", 20, 21, 50, 69, 204, 68, 0]]
}'

// read repeat read value
curl --location --request POST "192.168.1.124/hardware/operation" --header 'Content-Type: application/json' --data-raw '{
    "event":"now",
    "actions": [["i2c", 0, "read", 20, 21, 50, 69, -1, -1, 3]]
}'

