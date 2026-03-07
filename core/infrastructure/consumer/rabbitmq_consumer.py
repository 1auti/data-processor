import json
import logging
from typing import Callable, Optional


import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.spec import Basic, BasicProperties

from core.abstractions import BaseConsumer
from core.infrastructure.config.rabbit_config import RabbitMQConfig

# Configuramos el logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RabbitMQConsumer(BaseConsumer[dict]):
    """ Esta es una implementacion concreta del consumer para RabbitMQ
    Donde sus responsabilidad es

    Connectarme a RabbitMQ
    Consumir mensajes
    Deserializar de json a dict
    Delegar a un handler
    Gestionar ACKs/NACKs segun el resultado """


    def __init__(self,config: RabbitMQConfig):
        """
        Args:
             config: Configuracoin de conexion a Rabbit
        """

        self._config = config
        assert self._connection is not None
        assert  self._channel is not None
        #Si preferis tener una inicializacion con eager en vez de lazing lo poner en el init
        #self._connect()

    def start(self, handler: Callable[[dict]]):
        """
        Inicio del consumo de msj
        """

        try:

            # 1. Establecer la conexion
            self._connect()

            # 2. Declarar la cola
            self._declare_queue()

            # 3. Configurar quality of service
            self._setup_qos()

            # 4. Crear callback wrapper que maneja el ack/noack
            def callback_wrapper(
                    channel:BlockingChannel,
                    method: Basic.Deliver,
                    properties: BasicProperties,
                    body: bytes
            )-> None:
                """ Este wrapper es necesario porque basic_consume espera una funcion con esta firma especifica
                (channel, method, properties, body )

                Nosotros delegamos al _process_message que tambien recibe el handler"""

                self._process_message(channel, method, properties, body, handler)

            # 5. Registrar el consumer
            logger.info(f"Esperando mensaje de cola '{self._config.input_queue}...")
            self._channel.basic_consume(
                queue=self._config.input_queue,
                on_message_callback=callback_wrapper,
                auto_ack=False # Utilizamos un ACK MANUAL
            )

            # 6. Iniciar loop de consumo (blocking)
            logger.info("Consumer iniciado...")
            self._channel.start_consuming()


        except KeyboardInterrupt:
            logger.info("Consumer ha sido detenido manualmente")
            self.stop()
        except Exception as e:
            logger.error("Error fatal en el consumer: {e}",exc_info=True)
            self.stop()
            raise

    def stop(self) -> None:
        """
        Detiene el consumer
        """

        logger.info("Deteniendo consumer")

        if self._channel and self._channel.is_open:
            self._channel.stop_consuming()
            self._channel.close()

        if self._connection and self._connection.is_open:
            self._connection.close()

        logger.info("Consumer detenido correctamente")

    def _connect(self) -> None:
        """Establece conexion con RabbitMQ usando Pika ( libreria ) """

        logger.info("Conectando a RabbitMQ en {self._config.host}:{self._config.port}")

        # Parametros de conexion
        credentials = pika.PlainCredentials(
            username=self._config.username,
            password=self._config.password
        )

        parameters = pika.ConnectionParameters(
            host = self._config.host,
            port = self._config.port,
            virtual_host= self._config.virtual_host,
            heartbeat = self._config.heartbeat,
            blocked_connection_timeout = self._config.connection_timeout,
            credentials = credentials
        )

        # Estblecemos la conexion
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()

        logger.info("Conexion establecida")


    def _declare_queue(self) -> None:
        """
        Declara la cola de entrada.
        - Operación IDEMPOTENTE (no falla si ya existe)
        - Asegura que la cola tiene las propiedades correctas
        - Evita "queue not found" en ambientes nuevos

        Parámetros importantes:
        - durable=True: La cola sobrevive a restart de RabbitMQ
        - exclusive=False: Múltiples consumers pueden conectarse
        - auto_delete=False: No se borra cuando se desconecta el consumer
        """
        self._channel.queue_declare(
            queue=self._config.input_queue,
            durable=True,        # Persistir cola en disco
            exclusive=False,     # Permitir múltiples consumers
            auto_delete=False    # No borrar automáticamente
        )
        logger.info(f" Cola '{self._config.input_queue}' lista")


    def _setup_qos(self) -> None:
        """
        Configura Quality of Service (QoS).

        prefetch_count: Cuántos mensajes "en vuelo" puede tener este worker.

        Ejemplo con prefetch_count=10:
        - RabbitMQ envía 10 mensajes al worker
        - Worker procesa de a uno
        - Cuando hace ACK del primero, RabbitMQ envía el #11
        - Siempre mantiene 10 "en tránsito"

        ¿Por qué no prefetch_count=1?
        - Muy lento (espera ACK antes de enviar siguiente)

        ¿Por qué no prefetch_count=1000?
        - Si el worker crashea, pierdes 1000 mensajes en proceso

        Valor típico: 10-50 según velocidad de procesamiento
        """
        self._channel.basic_qos(prefetch_count=self._config.prefetch_count)
        logger.info(f" QoS configurado: prefetch={self._config.prefetch_count}")


    def _process_message(
        self,
        channel: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
        handler: Callable[[dict], None]
    ) -> None:
        """
        Procesa un mensaje individual con manejo de errores.

        Estrategia de ACK/NACK:
        1. Deserialización OK + Handler OK → ACK
        2. JSON inválido → NACK (no reencolar, es irrecuperable)
        3. Handler lanza excepción → Depende del tipo de error

        Args:
            channel: Canal de RabbitMQ
            method: Metadatos del mensaje (delivery_tag, routing_key, etc)
            properties: Propiedades AMQP (headers, correlation_id, etc)
            body: Payload crudo en bytes
            handler: Función de procesamiento
        """
        delivery_tag = method.delivery_tag

        try:
            # 1. Deserializar JSON → dict
            mensaje_str = body.decode('utf-8')
            mensaje_dict = json.loads(mensaje_str)

            logger.info(f" Mensaje recibido: {mensaje_dict.get('transferencia_id', 'N/A')}")

            # 2. Delegar al handler (aquí está la lógica de negocio)
            handler(mensaje_dict)

            # 3. TODO OK → Confirmar procesamiento
            channel.basic_ack(delivery_tag=delivery_tag)
            logger.info(f" Mensaje {delivery_tag} procesado correctamente")

        except json.JSONDecodeError as e:
            # JSON malformado → Error permanente, NO reencolar
            logger.error(f" JSON inválido en mensaje {delivery_tag}: {e}")
            channel.basic_nack(delivery_tag=delivery_tag, requeue=False)
            # TODO: Enviar a Dead Letter Queue para análisis

        except ValueError as e:
            #  Error de validación de negocio → NO reencolar
            logger.error(f" Validación falló para mensaje {delivery_tag}: {e}")
            channel.basic_nack(delivery_tag=delivery_tag, requeue=False)
            # TODO: Persistir en BD de errores para auditoría

        except Exception as e:
            #  Error inesperado → Reencolar para retry
            logger.error(
                f" Error procesando mensaje {delivery_tag}: {e}",
                exc_info=True
            )
            channel.basic_nack(delivery_tag=delivery_tag, requeue=True)
            # TODO: Implementar exponential backoff para evitar retry loops
