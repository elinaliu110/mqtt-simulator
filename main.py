import time
import random
import datetime
import wisepaasdatahubedgesdk.Common.Constants as constant

from wisepaasdatahubedgesdk.EdgeAgent import EdgeAgent
from wisepaasdatahubedgesdk.Common.Utils import RepeatedTimer
from wisepaasdatahubedgesdk.Model.Edge import EdgeAgentOptions, MQTTOptions, DCCSOptions, EdgeData, EdgeTag, EdgeStatus, EdgeDeviceStatus, EdgeConfig, NodeConfig, DeviceConfig, AnalogTagConfig, DiscreteTagConfig, TextTagConfig

# **
# Datahub 連線配置
# **
options = EdgeAgentOptions(
    reconnectInterval=1,    # MQTT重新連接間隔秒數
    nodeId='8d518411-7235-45b2-b3ae-f7fc14ec06d6',
    deviceId='deviceId',    # 如果類型為Device，則必須填寫DeviceId
    type=constant.EdgeType['Gateway'],  # 選擇您的邊緣是 Gateway 還是 Device，默認是 Gateway
    heartbeat=60,   # 默認值為 60 秒
    dataRecover=True,   # 斷開連接時是否需要恢復數據
    connectType=constant.ConnectType['DCCS'],   # 連接類型（DCCS，MQTT），默認為 DCCS
    MQTT=MQTTOptions(   # 如果連接類型為 MQTT，則必須填寫此選項
        hostName="127.0.0.1",
        port=1883,
        userName="admin",
        password="admin",
        protocalType=constant.Protocol['TCP']   # MQTT protocal (TCP, Websocket), default is TCP
    ),
    DCCS=DCCSOptions(
        apiUrl="https://api-dccs-ensaas.sa.wise-paas.com/", # DCCS API Url
        credentialKey="7338c13e255aa0c0eb815728e722e9wj"    # Creadential key
    )
)

edge_agent = EdgeAgent(options=options)


def generate_data(data, device_id, tag_name, value):
    tag = EdgeTag(device_id, tag_name, value)
    data.tagList.append(tag)


def send_data(data):
    edge_agent.sendData(data=data)


def handler_on_connected(agent, isConnected):
    # Connected: when EdgeAgent is connected to IoTHub.
    print("Connected successfully")

    # TODO: Put data sending here


def handler_on_disconnected(agent, isDisconnected):
    # Disconnected: when EdgeAgent is disconnected to IoTHub.
    print("Disconnected")


def handler_on_message(agent, messageReceivedEventArgs):
    '''
    MessageReceived: when EdgeAgent receives MQTT message FROM CLOUD. The message type is as follows:
        - WriteValue: Change tag value from cloud.
        - WriteConfig: Change config from cloud.
        - TimeSync: Returns the current time from cloud.
        - ConfigAck: The response of uploading config from edge to cloud.
    '''
    # messageReceivedEventArgs format: Model.Event.MessageReceivedEventArgs
    type = messageReceivedEventArgs.type
    message = messageReceivedEventArgs.message
    if type == constant.MessageType['WriteValue']:
        # message format: Model.Edge.WriteValueCommand
        for device in message.deviceList:
            print(f'deviceId: {device.id}')
            for tag in device.tagList:
                print(f'tagName: {tag.name}, Value: {tag.value}')
    elif type == constant.MessageType['WriteConfig']:
        print('WriteConfig')
    elif type == constant.MessageType['TimeSync']:
        # message format: Model.Edge.TimeSyncCommand
        print(str(message.UTCTime))
    elif type == constant.MessageType['ConfigAck']:
        # message format: Model.Edge.ConfigAck
        print(f'Upload Config Result: {str(message.result)}')


# Bind event handlers
edge_agent.on_connected = handler_on_connected
edge_agent.on_disconnected = handler_on_disconnected
edge_agent.on_message = handler_on_message

# Connect to the cloud
edge_agent.connect()
time.sleep(2)

# Sending data
while True:
    data = EdgeData()
    # Append the new tag value to the data
    generate_data(data, 'Device1', 'ATag1', 200)
    generate_data(data, 'Device1', 'BTag1', 300)
    generate_data(data, 'Device1', 'DTag1', random.randint(0, 1))
    generate_data(data, 'Device1', 'OEETag1', random.randint(0, 4))
    generate_data(data, 'Device1', 'RandomTag1', random.randint(0, 500))

    # data.timestamp = datetime.datetime.now()

    send_data(data)
    time.sleep(5)

# Drop the connection
edge_agent.disconnect()
