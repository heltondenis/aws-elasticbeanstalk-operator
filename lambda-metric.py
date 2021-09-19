import json
import logging
import boto3
import datetime
from botocore.exceptions import ClientError

cloudwatch = boto3.client('cloudwatch')
sqs_client = boto3.client('sqs', region_name='us-east-1')

# Cria a métrica personalizada
def publish_metric(value):
    
    try:
        response = cloudwatch.put_metric_data(
            MetricData = [
                {
                    'MetricName': 'NumMessagesCreated',
                    'Dimensions': [
                        {
                            'Name': 'MessageSource',
                            'Value': 'Lambda'
                        }
                    ],
                    'Unit': 'None',
                    'Value': value
                },
            ],
            Namespace='BeanstalkScaling'
        )
    except ClientError as e:
        logging.error(e)
        return None
    return response
    
    
def send_sqs_message(QueueUrl, msg_body):
    """
    :param sqs_queue_url: URL da string da fila SQS existente
    :param msg_body: String corpo da mensagem
    :return: Dicionário contendo informações sobre a mensagem enviada. Se
        erro, retorna Null.
    """

    # Envia a mensagem SQS
    try:
        msg = sqs_client.send_message(QueueUrl=QueueUrl,
                                      MessageBody=json.dumps(msg_body))
    except ClientError as e:
        logging.error(e)
        return None
    return msg
    
def lambda_handler(event, context):
    """Teste send_sqs_message()"""

    QueueUrl = 'Adiciona a fila SQS'
    Duration = 10
    
    # Configurar registro
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(asctime)s: %(message)s')

    # Loop com mensagens
    msgCount = 0
    endTime = datetime.datetime.now() + datetime.timedelta(minutes=Duration)
    while datetime.datetime.now() < endTime:
        msg = send_sqs_message(QueueUrl,'mensagem ' + str(msgCount))
        msgCount = msgCount + 1
        publish_metric(msgCount)
        
        if msg is not None:
            logging.info(f'Enviar ID: {msg["MessageId"]}')
    
    return {
        'statusCode': 200,
        'body': 'Sent ' + str(msgCount) + ' mensagens'
    }