
import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RabbitMQConfig:
    """
    Aca se encuentra la configuracion centralizada de RABBIT MQ

    La idea es que use variables de entorno con valores por defecto para desarrollo
    """

    # Conexion basica
    host:str
    port:int
    username:str
    password:str
    virtual_host:str

    # Colas
    input_queue:str # La cola donde consumimos la informacion
    output_queue: str # La cola que utilizamos para consumir la informacion

    # Propiedades de configuracion
    prefetch_count:int # Cuantos msj procesar en paralelo
    heartbeat: int # Cada cuentos segundos verificar conexion
    connection_timeout: int # Timeout para establecer conexion


    @classmethod
    def from_env(cls) -> "RabbitMQConfig":

        """ Aplicamos el factory method con este metodo lo que logramos es abstrar la complejidad de la configuracion
        de las colas """
        return cls(

            host=os.getenv("RABBITMQ_HOST", "localhost"),
            port=int(os.getenv("RABBITMQ_PORT", "5672")),
            username=os.getenv("RABBITMQ_USER", "guest"),
            password=os.getenv("RABBITMQ_PASS", "guest"),
            virtual_host=os.getenv("RABBITMQ_VHOST", "/"),

            # Nombres de colas (ajusta según tu arquitectura)
            input_queue=os.getenv("RABBITMQ_INPUT_QUEUE", "transferencias.pendientes"),
            output_queue=os.getenv("RABBITMQ_OUTPUT_QUEUE", "transferencias.procesadas"),

              # Tunning
            prefetch_count=int(os.getenv("RABBITMQ_PREFETCH", "10")),
            heartbeat=int(os.getenv("RABBITMQ_HEARTBEAT", "60")),
            connection_timeout=int(os.getenv("RABBITMQ_TIMEOUT", "30"))

        )


    @property
    def connection_url(self) -> str:
        """ Generamos una conexion AMQP
        ¿ Que es ?
         Significa Protocolo de cola de mensajes avanzado """
        return (
            f"amqp://{self.username}:{self.password}"
            f"@{self.host}:{self.port}-{self.virtual_host}"
        )

    def __repr__(self)-> str:
        """ Es un overide que sirve para no exponer la contraseña en los logs """
        return(
             f"RabbitMQConfig(host={self.host}, port={self.port}, "
            f"user={self.username}, vhost={self.virtual_host}, "
            f"input_queue={self.input_queue}, output_queue={self.output_queue})"
        )



