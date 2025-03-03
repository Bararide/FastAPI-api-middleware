import pika
import json
import logging
import asyncio

from fastapi import HTTPException
from typing import Optional


class MessagePublisher:
    def __init__(self):
        self.connection_params = pika.ConnectionParameters("localhost")
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()

    async def publish_message(self, queue, message):
        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.basic_publish(exchange="", routing_key=queue, body=message)
        logging.info(f"Sent: {message}")

    async def get_response_from_queue(self, queue):
        def callback(ch, method, properties, body):
            nonlocal response
            logging.info(f"Received: {body.decode()}")
            response = body.decode()
            ch.basic_ack(delivery_tag=method.delivery_tag)
            ch.stop_consuming()

        response = None
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()

        channel.queue_declare(queue=queue, durable=True)

        logging.info(f"Waiting for messages from queue: {queue}")
        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=False)

        try:
            channel.start_consuming()
        except Exception as e:
            logging.error(f"Error consuming message: {e}")
        finally:
            connection.close()

        return json.loads(response)

    async def process_request(
        self,
        action: str,
        request_query: str,
        query: str,
        payload: Optional[dict] = None,
    ) -> dict:
        """
        Универсальная функция для обработки запросов через RabbitMQ.

        :param action: Название действия (например, "get_countries").
        :param payload: Дополнительные параметры для RabbitMQ.
        :return: Ответ из очереди RabbitMQ.
        """
        try:
            message = {"action": action}
            if payload:
                message.update(payload)

            await self.publish_message(request_query, json.dumps(message))

            response = await self.get_response_from_queue(query)
            if response is None:
                raise HTTPException(
                    status_code=500, detail=f"No data received for action: {action}"
                )

            return {"source": "backend", "data": response}

        except Exception as e:
            logging.error(f"Error processing action '{action}': {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to process action '{action}': {str(e)}"
            )
