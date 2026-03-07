import json
import logging
from math import log
from multiprocessing import Value
from tkinter import N
from token import OP
from typing import Optional, assert_type

import pika
from pika.adapters.blocking_connection import BlockingConnection, BlockingChannel
from pika.spec import BasicProperties

from core.abstractions import BaseSender
from core.infrastructure.config.rabbit_config import RabbitMQConfig


# Inicializacion del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RabbitMQSender(BaseSender[dict]):
    """
    Responsabilidad :
    - Conectar el RABBITMQ
    - Serializar de DICT a JSON
    - Publicar los eventos
    - Manejar los errores de conexiones
    """

    def __init__(self, config: RabbitMQConfig):
        """
        Args:
        - Config : Le pasamos la configuracion del RABBITMQ
        """

        self._config = config
        self._connection: Optional[BlockingConnection] = None
        self._channel: Optional[BlockingChannel] = None

        self._connect() # Lo estamos haciendo de forma de eager para no tener porblemas de latencia. Ademas si no se puede connectar por problemas de IT se nota rapiod

    def send(self, message:dict) -> None:
        """
        Responsabilidad:
        - Mandar un mensaje a la cola de salida

        Args:
        - message: Dict que representa el mensaje a enviar (serializacion en JSON)

        Raises:
        - ValueError: SI el msj no se serializa en JSON
        - Exception: SI hay un problema de conexion
        """

        try:

            self._ensure_connection()

            # 1. Serializar de DICT -> JSON
            body =  json.dumps(message, ensure_ascii=False)

            # 2. Configurar las propiedades del  mensaje
            properties = BasicProperties(
                delivery_mode=2, # Mensaje persistente
                content_type='application/json',
                content_encoding='utf-8'
            )

            assert self._channel is not None, "Channel debe estar inicializado"

            # 3. Publicar en la cola

            self._channel.basic_publish(
                exchange='', #Exchange vacio -> publicar directamente en la cola
                routing_key=self._config.output_queue,
                body=body.encode('utf-8'),
                properties=properties,
                mandatory=True # Falla si la cola no existe
            )

            logger.info(
                f"Mensaje existosamente enviado a '{self._config.output_queue}': "
                f"{message.get('transferencia_id','N/A')}"
            )



        except (TypeError, ValueError) as e :
            logger.error(f"Error al serializar el mensaje: {e}")
            raise ValueError(f"Mensaje no serializado: {e}") from e
        except Exception as e:
            logger.error(f"Error enviando el mensaje {e}")
            self._reconnect()
            raise


    def close(self)-> None:
        """
        Cierra la conexion a RabbitMQ
        """

        logger.info(f"Cerrando la conexion del sender...")

        if self._channel and self._channel.is_open:
            self._channel.close()

        if self._connection and self._connection.is_open:
            self._connection.close()

        logger.info(f"Sender cerrado exitosamente")

    def _connect(self)-> None:
        """
        Establece la conexion con RABBITMQ

        Este conectame atravez de un eager
        """

        logger.info(
            f"Connectando el Sender a RabbitMQ en"
            f"{self._config.host}:{self._config.port}"
             )

        # Crendiales
        credentials = pika.PlainCredentials(
            username=self._config.username,
            password=self._config.password
        )

        # Parameatros de la conexion
        parameters = pika.ConnectionParameters(
            host=self._config.host,
            port=self._config.port,
            virtual_host=self._config.virtual_host,
            credentials=credentials,
            heartbeat=self._config.heartbeat,
            blocked_connection_timeout=self._config.connection_timeout

        )

        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()

        # Declaramos la cola de salida
        self._channel.queue_declare(
            queue=self._config.output_queue,
            durable=True, #Persistir colas en disco
            exclusive=False, #Permitir multiples sender/consumer
            auto_delete=False # No borrar actomaticamente
        )


    def _ensure_connection(self) -> None:

        if self._connection is None or self._connection.is_closed:
            self._reconnect()


    def _reconnect(self) -> None:
        """
        Intenta reconectar después de un error.

        Estrategia simple: cerrar todo y volver a conectar.

        Para producción, considerá:
        - Exponential backoff
        - Límite de reintentos
        - Circuit breaker pattern
        """
        logger.warning(" Intentando reconectar...")

        try:
            self.close()
        except Exception:
            pass  # Ignorar errores al cerrar

        try:
            self._connect()
            logger.info(" Reconexión exitosa")
        except Exception as e:
            logger.error(f" Falló la reconexión: {e}")
            raise






















