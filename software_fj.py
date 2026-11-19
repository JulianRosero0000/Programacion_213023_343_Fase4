"""
Fase 4 - Componente práctico - Prácticas simuladas
Curso: Programación (213023) - UNAD
Grupo: 213023_343
Estudiante: Julian Alberto Rosero Camacho
Tutor: Juan Pablo Arango Cardona

Ejercicio 1: Sistema Integral de Gestión de Clientes, Servicios y Reservas (Software FJ).
Este archivo contiene el mismo código del cuaderno Fase4_SoftwareFJ.ipynb.
Ejecución: python software_fj.py
"""


# ==============================================================================
# 1. Importaciones y configuración del archivo de logs
# ==============================================================================
# Se configura un registrador propio que escribe cada evento y cada error en el archivo software_fj.log, con fecha, hora y nivel de severidad.

# Módulo estándar para registrar eventos y errores en un archivo
import logging
# Módulo estándar para validar textos con expresiones regulares (correo electrónico)
import re
# Herramientas para declarar clases abstractas y métodos abstractos
from abc import ABC, abstractmethod
# Decorador que permite sobrecargar un método según el tipo de dato del argumento
from functools import singledispatchmethod

# Nombre del archivo donde quedan registrados los eventos y los errores del sistema
ARCHIVO_LOG = "software_fj.log"

# Se obtiene un registrador con nombre propio para no mezclarlo con otros registradores
logger = logging.getLogger("software_fj")
# Se registran todos los niveles: DEBUG, INFO, WARNING, ERROR y CRITICAL
logger.setLevel(logging.DEBUG)
# Se eliminan manejadores anteriores para no duplicar líneas si la celda se ejecuta de nuevo
logger.handlers.clear()
# Manejador que escribe en el archivo, en modo agregar y con codificación UTF-8
manejador_archivo = logging.FileHandler(ARCHIVO_LOG, mode="a", encoding="utf-8")
# Formato de cada línea del log: fecha y hora | nivel | mensaje
formato_log = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
# Se asigna el formato al manejador del archivo
manejador_archivo.setFormatter(formato_log)
# Se conecta el manejador al registrador
logger.addHandler(manejador_archivo)
# Se evita que los mensajes se repitan en la salida estándar del cuaderno
logger.propagate = False

# Primer evento del log: marca el inicio de una nueva ejecución del sistema
logger.info("===== Inicio de ejecución del sistema Software FJ =====")
# Mensaje de confirmación en pantalla
print(f"Registro de eventos configurado. Archivo de logs: {ARCHIVO_LOG}")


# ==============================================================================
# 2. Excepciones personalizadas
# ==============================================================================
# Todas las excepciones del sistema heredan de ErrorSoftwareFJ. Esto permite capturar cualquier error propio de la aplicación con un solo bloque except, sin ocultar errores inesperados de Python.

# Excepción base: de ella heredan todas las excepciones propias del sistema
class ErrorSoftwareFJ(Exception):
    """Excepción base del sistema Software FJ."""


# Error de validación de datos de entrada (formatos, rangos, datos vacíos)
class ErrorValidacion(ErrorSoftwareFJ):
    """Se lanza cuando un dato de entrada no cumple las reglas de validación."""


# Error relacionado con la gestión de clientes (duplicados, no encontrados)
class ErrorCliente(ErrorSoftwareFJ):
    """Se lanza cuando una operación sobre clientes no se puede completar."""


# Error relacionado con la creación o configuración de servicios
class ErrorServicio(ErrorSoftwareFJ):
    """Se lanza cuando un servicio se crea o se configura de forma incorrecta."""


# Error específico: el servicio existe pero no está disponible para reservar
class ServicioNoDisponibleError(ErrorServicio):
    """Se lanza cuando se intenta usar un servicio que no está disponible."""


# Error relacionado con el ciclo de vida de una reserva
class ErrorReserva(ErrorSoftwareFJ):
    """Se lanza cuando una reserva no se puede crear, confirmar, cancelar o procesar."""


# Error en los cálculos de costos (impuestos, descuentos o totales inconsistentes)
class ErrorCalculo(ErrorSoftwareFJ):
    """Se lanza cuando un cálculo de costos produce un resultado inconsistente."""


# Mensaje de confirmación en pantalla
print("Excepciones personalizadas definidas correctamente.")


# ==============================================================================
# 3. Clase abstracta general: `Entidad`
# ==============================================================================
# Representa cualquier entidad del sistema (cliente, servicio o reserva). Asigna un identificador único y obliga a las clases hijas a implementar los métodos describir() y validar().

# Clase abstracta que representa a las entidades generales del sistema
class Entidad(ABC):
    """Entidad general del sistema: asigna un identificador único a cada objeto."""

    # Contador compartido por todas las entidades para generar identificadores consecutivos
    _contador = 0

    # Constructor común de todas las entidades
    def __init__(self):
        # Se incrementa el contador general de entidades
        Entidad._contador += 1
        # Se guarda el identificador como atributo protegido
        self._id = Entidad._contador

    # Propiedad de solo lectura para consultar el identificador
    @property
    def id(self):
        # Se retorna el identificador sin permitir su modificación
        return self._id

    # Método abstracto: cada entidad debe saber describirse en texto
    @abstractmethod
    def describir(self):
        """Retorna una descripción en texto de la entidad."""

    # Método abstracto: cada entidad debe saber validar su propio estado
    @abstractmethod
    def validar(self):
        """Verifica que el estado interno de la entidad sea consistente."""

    # Representación en texto del objeto, usada por print()
    def __str__(self):
        # Se reutiliza el método polimórfico describir() de cada clase hija
        return self.describir()


# Mensaje de confirmación en pantalla
print("Clase abstracta Entidad definida correctamente.")


# ==============================================================================
# 4. Clase `Cliente`
# ==============================================================================
# Encapsula los datos personales en atributos privados y los expone mediante propiedades. Cada asignación pasa por un validador, de modo que un cliente nunca queda con datos inválidos.

# Clase que representa a un cliente de Software FJ
class Cliente(Entidad):
    """Cliente con datos personales encapsulados y validados."""

    # Expresión regular para validar el formato básico de un correo electrónico
    _PATRON_CORREO = re.compile(r"^[\w\.\-]+@[\w\-]+(\.[\w\-]+)+$")

    # Constructor: recibe los datos personales del cliente
    def __init__(self, nombre, documento, correo, telefono):
        # Cada asignación invoca al validador (setter) de la propiedad correspondiente
        self.nombre = nombre
        # Se valida y se asigna el documento de identidad
        self.documento = documento
        # Se valida y se asigna el correo electrónico
        self.correo = correo
        # Se valida y se asigna el teléfono
        self.telefono = telefono
        # Solo si todos los datos son válidos se asigna el identificador de la entidad
        super().__init__()

    # Propiedad para consultar el nombre
    @property
    def nombre(self):
        # Se retorna el atributo privado
        return self.__nombre

    # Validador del nombre
    @nombre.setter
    def nombre(self, valor):
        # El nombre debe ser un texto
        if not isinstance(valor, str):
            # Se rechaza cualquier tipo de dato distinto de texto
            raise ErrorValidacion("El nombre del cliente debe ser un texto.")
        # Se eliminan los espacios sobrantes al inicio y al final
        valor = valor.strip()
        # El nombre debe tener al menos tres caracteres
        if len(valor) < 3:
            # Se rechaza un nombre vacío o demasiado corto
            raise ErrorValidacion("El nombre del cliente debe tener al menos 3 caracteres.")
        # El nombre solo puede contener letras y espacios
        if not all(caracter.isalpha() or caracter.isspace() for caracter in valor):
            # Se rechazan números y símbolos en el nombre
            raise ErrorValidacion("El nombre del cliente solo puede contener letras y espacios.")
        # Se guarda el nombre validado en el atributo privado
        self.__nombre = valor

    # Propiedad para consultar el documento
    @property
    def documento(self):
        # Se retorna el atributo privado
        return self.__documento

    # Validador del documento de identidad
    @documento.setter
    def documento(self, valor):
        # Se intenta convertir el valor a número entero para comprobar que es numérico
        try:
            # La conversión falla si el valor tiene letras, símbolos o es None
            numero = int(valor)
        # Se capturan los dos errores posibles de la conversión
        except (ValueError, TypeError) as error:
            # Encadenamiento de excepciones: se conserva el error original como causa
            raise ErrorValidacion(f"El documento '{valor}' no es numérico.") from error
        # El documento no puede ser negativo ni cero
        if numero <= 0:
            # Se rechaza un documento no positivo
            raise ErrorValidacion("El documento debe ser un número positivo.")
        # Se convierte el número a texto para revisar su longitud
        texto = str(numero)
        # El documento debe tener entre 6 y 10 dígitos
        if not 6 <= len(texto) <= 10:
            # Se rechaza un documento con longitud fuera del rango permitido
            raise ErrorValidacion("El documento debe tener entre 6 y 10 dígitos.")
        # Se guarda el documento validado en el atributo privado
        self.__documento = texto

    # Propiedad para consultar el correo
    @property
    def correo(self):
        # Se retorna el atributo privado
        return self.__correo

    # Validador del correo electrónico
    @correo.setter
    def correo(self, valor):
        # El correo debe ser un texto que cumpla el patrón usuario@dominio.ext
        if not isinstance(valor, str) or not self._PATRON_CORREO.match(valor.strip()):
            # Se rechaza un correo con formato incorrecto
            raise ErrorValidacion(f"El correo '{valor}' no tiene un formato válido.")
        # Se guarda el correo en minúsculas y sin espacios sobrantes
        self.__correo = valor.strip().lower()

    # Propiedad para consultar el teléfono
    @property
    def telefono(self):
        # Se retorna el atributo privado
        return self.__telefono

    # Validador del teléfono
    @telefono.setter
    def telefono(self, valor):
        # Se convierte el valor a texto y se eliminan espacios sobrantes
        texto = str(valor).strip()
        # El teléfono debe tener solo dígitos y una longitud entre 7 y 10
        if not texto.isdigit() or not 7 <= len(texto) <= 10:
            # Se rechaza un teléfono con letras o con longitud incorrecta
            raise ErrorValidacion("El teléfono debe tener entre 7 y 10 dígitos numéricos.")
        # Se guarda el teléfono validado en el atributo privado
        self.__telefono = texto

    # Implementación del método abstracto validar()
    def validar(self):
        # Los validadores garantizan el estado; aquí se confirma que los datos existen
        return all([self.__nombre, self.__documento, self.__correo, self.__telefono])

    # Implementación del método abstracto describir()
    def describir(self):
        # Se arma un texto con los datos principales del cliente
        return f"Cliente #{self.id}: {self.nombre} | Documento: {self.documento} | Correo: {self.correo}"


# Mensaje de confirmación en pantalla
print("Clase Cliente definida correctamente.")


# ==============================================================================
# 5. Clase abstracta `Servicio` y servicios especializados
# ==============================================================================
# Servicio define el contrato común. Cada servicio especializado (ReservaSala, AlquilerEquipo y AsesoriaEspecializada) sobrescribe los métodos calcular_costo(), describir() y validar_parametros(), lo que evidencia el polimorfismo.
# La sobrecarga del cálculo de costos se implementa con parámetros opcionales: el mismo método admite el cálculo con el impuesto por defecto, con un impuesto distinto, o con impuesto y descuento.

# Clase abstracta que representa cualquier servicio ofrecido por Software FJ
class Servicio(Entidad):
    """Servicio general: define el contrato que cumplen los servicios especializados."""

    # Impuesto por defecto (IVA del 19 %) aplicado cuando no se indica otro valor
    IVA_POR_DEFECTO = 0.19

    # Constructor común de todos los servicios
    def __init__(self, nombre, tarifa_base, disponible=True):
        # El nombre del servicio debe ser un texto de al menos tres caracteres
        if not isinstance(nombre, str) or len(nombre.strip()) < 3:
            # Se rechaza un nombre vacío o demasiado corto
            raise ErrorServicio("El nombre del servicio debe tener al menos 3 caracteres.")
        # La tarifa debe ser numérica (se excluye el tipo booleano, que Python trata como entero)
        if isinstance(tarifa_base, bool) or not isinstance(tarifa_base, (int, float)):
            # Se rechaza una tarifa que no sea un número
            raise ErrorServicio("La tarifa base del servicio debe ser un valor numérico.")
        # La tarifa debe ser mayor que cero
        if tarifa_base <= 0:
            # Se rechaza una tarifa negativa o igual a cero
            raise ErrorServicio(f"La tarifa base debe ser mayor que cero (valor recibido: {tarifa_base}).")
        # Se guarda el nombre como atributo protegido
        self._nombre = nombre.strip()
        # Se guarda la tarifa base como atributo protegido
        self._tarifa_base = float(tarifa_base)
        # Se guarda el estado de disponibilidad convertido a booleano
        self._disponible = bool(disponible)
        # Con los datos validados se asigna el identificador de la entidad
        super().__init__()

    # Propiedad de solo lectura para consultar el nombre
    @property
    def nombre(self):
        # Se retorna el atributo protegido
        return self._nombre

    # Propiedad de solo lectura para consultar la tarifa base
    @property
    def tarifa_base(self):
        # Se retorna el atributo protegido
        return self._tarifa_base

    # Propiedad para consultar la disponibilidad
    @property
    def disponible(self):
        # Se retorna el atributo protegido
        return self._disponible

    # Modificador de la disponibilidad
    @disponible.setter
    def disponible(self, valor):
        # Se guarda el nuevo estado convertido a booleano
        self._disponible = bool(valor)

    # Método abstracto: cada servicio calcula su costo con reglas propias
    @abstractmethod
    def calcular_costo(self, duracion, impuesto=None, descuento=0.0):
        """Calcula el costo total del servicio para la duración indicada."""

    # Método abstracto: cada servicio valida la duración con reglas propias
    @abstractmethod
    def validar_parametros(self, duracion):
        """Valida que la duración solicitada sea permitida para el servicio."""

    # Método de apoyo reutilizado por los servicios hijos para validar la duración
    def _validar_duracion(self, duracion, minimo, maximo, unidad):
        # La duración debe ser un número entero (se excluye el tipo booleano)
        if isinstance(duracion, bool) or not isinstance(duracion, int):
            # Se rechaza una duración que no sea un número entero
            raise ErrorValidacion(f"La duración debe ser un número entero de {unidad}.")
        # La duración debe estar dentro del rango permitido para el servicio
        if not minimo <= duracion <= maximo:
            # Se rechaza una duración fuera del rango permitido
            raise ErrorValidacion(
                f"La duración para '{self.nombre}' debe estar entre {minimo} y {maximo} {unidad} "
                f"(valor recibido: {duracion})."
            )
        # Si no hubo errores, la duración es válida
        return True

    # Método de apoyo que aplica el descuento y el impuesto a un subtotal
    def _aplicar_impuesto_y_descuento(self, subtotal, impuesto, descuento):
        # Si no se indica impuesto, se usa el IVA por defecto
        if impuesto is None:
            # Se toma el valor definido como constante de la clase
            impuesto = self.IVA_POR_DEFECTO
        # El impuesto debe ser una proporción entre 0 y 1
        if not 0 <= impuesto <= 1:
            # Se rechaza un impuesto fuera del rango permitido
            raise ErrorCalculo(f"El impuesto debe estar entre 0 y 1 (valor recibido: {impuesto}).")
        # El descuento debe ser una proporción entre 0 y menos de 1
        if not 0 <= descuento < 1:
            # Se rechaza un descuento negativo o igual o superior al 100 %
            raise ErrorCalculo(f"El descuento debe estar entre 0 y 0.99 (valor recibido: {descuento}).")
        # Se aplica primero el descuento y luego el impuesto sobre el valor resultante
        total = subtotal * (1 - descuento) * (1 + impuesto)
        # Un total menor o igual a cero indica un cálculo inconsistente
        if total <= 0:
            # Se rechaza el resultado inconsistente
            raise ErrorCalculo("El cálculo produjo un total inconsistente (menor o igual a cero).")
        # Se retorna el total redondeado a dos decimales
        return round(total, 2)

    # Implementación del método abstracto validar() heredado de Entidad
    def validar(self):
        # Un servicio es consistente si tiene nombre y una tarifa positiva
        return bool(self._nombre) and self._tarifa_base > 0


# Servicio especializado 1: reserva de salas, cobrada por horas
class ReservaSala(Servicio):
    """Reserva de una sala de reuniones o capacitación."""

    # Constructor: agrega la capacidad de la sala a los datos generales del servicio
    def __init__(self, nombre, tarifa_base, capacidad, disponible=True):
        # La capacidad debe ser un entero mayor que cero
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            # Se rechaza una capacidad inválida
            raise ErrorServicio("La capacidad de la sala debe ser un número entero mayor que cero.")
        # Se guarda la capacidad como atributo protegido
        self._capacidad = capacidad
        # Se delega al constructor de Servicio la validación de los datos generales
        super().__init__(nombre, tarifa_base, disponible)

    # Sobrescritura: una sala se reserva entre 1 y 8 horas
    def validar_parametros(self, duracion):
        # Se reutiliza el validador general con el rango propio de este servicio
        return self._validar_duracion(duracion, 1, 8, "horas")

    # Sobrescritura: costo = tarifa por hora x horas, con recargo para salas grandes
    def calcular_costo(self, duracion, impuesto=None, descuento=0.0):
        # Se valida la duración antes de calcular
        self.validar_parametros(duracion)
        # Subtotal: tarifa por hora multiplicada por el número de horas
        subtotal = self.tarifa_base * duracion
        # Las salas con capacidad superior a 20 personas tienen un recargo del 15 %
        if self._capacidad > 20:
            # Se aplica el recargo al subtotal
            subtotal *= 1.15
        # Se aplican el descuento y el impuesto y se retorna el total
        return self._aplicar_impuesto_y_descuento(subtotal, impuesto, descuento)

    # Sobrescritura: descripción propia de la sala
    def describir(self):
        # Se convierte el estado booleano en un texto legible
        estado = "disponible" if self.disponible else "no disponible"
        # Se arma el texto con los datos de la sala
        return (f"Servicio #{self.id}: Sala '{self.nombre}' | Capacidad: {self._capacidad} personas | "
                f"Tarifa: ${self.tarifa_base:,.0f} por hora | Estado: {estado}")


# Servicio especializado 2: alquiler de equipos, cobrado por días
class AlquilerEquipo(Servicio):
    """Alquiler de equipos tecnológicos."""

    # Constructor: agrega la cantidad de equipos a los datos generales del servicio
    def __init__(self, nombre, tarifa_base, cantidad, disponible=True):
        # La cantidad debe ser un entero mayor que cero
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            # Se rechaza una cantidad inválida
            raise ErrorServicio("La cantidad de equipos debe ser un número entero mayor que cero.")
        # Se guarda la cantidad como atributo protegido
        self._cantidad = cantidad
        # Se delega al constructor de Servicio la validación de los datos generales
        super().__init__(nombre, tarifa_base, disponible)

    # Sobrescritura: un equipo se alquila entre 1 y 30 días
    def validar_parametros(self, duracion):
        # Se reutiliza el validador general con el rango propio de este servicio
        return self._validar_duracion(duracion, 1, 30, "días")

    # Sobrescritura: costo = tarifa diaria x días x cantidad de equipos
    def calcular_costo(self, duracion, impuesto=None, descuento=0.0):
        # Se valida la duración antes de calcular
        self.validar_parametros(duracion)
        # Subtotal: tarifa diaria por número de días por cantidad de equipos
        subtotal = self.tarifa_base * duracion * self._cantidad
        # Se aplican el descuento y el impuesto y se retorna el total
        return self._aplicar_impuesto_y_descuento(subtotal, impuesto, descuento)

    # Sobrescritura: descripción propia del alquiler
    def describir(self):
        # Se convierte el estado booleano en un texto legible
        estado = "disponible" if self.disponible else "no disponible"
        # Se arma el texto con los datos del alquiler
        return (f"Servicio #{self.id}: Alquiler '{self.nombre}' | Cantidad: {self._cantidad} equipos | "
                f"Tarifa: ${self.tarifa_base:,.0f} por día y por equipo | Estado: {estado}")


# Servicio especializado 3: asesoría especializada, cobrada por horas según el nivel del asesor
class AsesoriaEspecializada(Servicio):
    """Asesoría prestada por un profesional de nivel junior, senior o experto."""

    # Factor que multiplica la tarifa según el nivel del asesor
    _FACTORES_NIVEL = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    # Constructor: agrega el área y el nivel del asesor a los datos generales del servicio
    def __init__(self, nombre, tarifa_base, area, nivel="junior", disponible=True):
        # El área de la asesoría debe ser un texto no vacío
        if not isinstance(area, str) or not area.strip():
            # Se rechaza un área vacía o que no sea texto
            raise ErrorServicio("El área de la asesoría es obligatoria.")
        # El nivel debe ser uno de los definidos en el diccionario de factores
        if nivel not in self._FACTORES_NIVEL:
            # Se rechaza un nivel desconocido
            raise ErrorServicio(f"Nivel de asesor no válido: '{nivel}'. Use junior, senior o experto.")
        # Se guarda el área como atributo protegido
        self._area = area.strip()
        # Se guarda el nivel como atributo protegido
        self._nivel = nivel
        # Se delega al constructor de Servicio la validación de los datos generales
        super().__init__(nombre, tarifa_base, disponible)

    # Sobrescritura: una asesoría dura entre 1 y 4 horas
    def validar_parametros(self, duracion):
        # Se reutiliza el validador general con el rango propio de este servicio
        return self._validar_duracion(duracion, 1, 4, "horas")

    # Sobrescritura: costo = tarifa por hora x horas x factor del nivel del asesor
    def calcular_costo(self, duracion, impuesto=None, descuento=0.0):
        # Se valida la duración antes de calcular
        self.validar_parametros(duracion)
        # Subtotal: tarifa por hora por número de horas por el factor del nivel
        subtotal = self.tarifa_base * duracion * self._FACTORES_NIVEL[self._nivel]
        # Se aplican el descuento y el impuesto y se retorna el total
        return self._aplicar_impuesto_y_descuento(subtotal, impuesto, descuento)

    # Sobrescritura: descripción propia de la asesoría
    def describir(self):
        # Se convierte el estado booleano en un texto legible
        estado = "disponible" if self.disponible else "no disponible"
        # Se arma el texto con los datos de la asesoría
        return (f"Servicio #{self.id}: Asesoría '{self.nombre}' | Área: {self._area} | Nivel: {self._nivel} | "
                f"Tarifa: ${self.tarifa_base:,.0f} por hora | Estado: {estado}")


# Mensaje de confirmación en pantalla
print("Clase abstracta Servicio y servicios especializados definidos correctamente.")


# ==============================================================================
# 6. Clase `Reserva`
# ==============================================================================
# Integra cliente, servicio, duración y estado. Implementa la confirmación, la cancelación y el procesamiento con manejo de excepciones:
# - confirmar() usa try/except/else.
# - procesar() usa try/except/else/finally y encadenamiento de excepciones (raise ... from ...).
# - aplicar_descuento() es un método sobrecargado según el tipo de dato: recibe un porcentaje numérico o un código promocional en texto.

# Clase que representa una reserva de un servicio hecha por un cliente
class Reserva(Entidad):
    """Reserva que integra cliente, servicio, duración y estado."""

    # Estados posibles de una reserva
    PENDIENTE = "PENDIENTE"
    # Estado de una reserva confirmada y lista para procesar
    CONFIRMADA = "CONFIRMADA"
    # Estado de una reserva cancelada
    CANCELADA = "CANCELADA"
    # Estado de una reserva procesada y cobrada
    PROCESADA = "PROCESADA"

    # Códigos promocionales vigentes y el descuento que otorga cada uno
    _CODIGOS_PROMOCIONALES = {"FJ10": 0.10, "FJ20": 0.20}

    # Constructor: recibe el cliente, el servicio y la duración solicitada
    def __init__(self, cliente, servicio, duracion):
        # El primer argumento debe ser un objeto de la clase Cliente
        if not isinstance(cliente, Cliente):
            # Se rechaza una reserva sin un cliente válido
            raise ErrorReserva("La reserva requiere un cliente válido.")
        # El segundo argumento debe ser un objeto de alguna clase derivada de Servicio
        if not isinstance(servicio, Servicio):
            # Se rechaza una reserva sin un servicio válido
            raise ErrorReserva("La reserva requiere un servicio válido.")
        # Se valida la duración con las reglas propias del servicio (polimorfismo)
        servicio.validar_parametros(duracion)
        # Se guarda el cliente como atributo protegido
        self._cliente = cliente
        # Se guarda el servicio como atributo protegido
        self._servicio = servicio
        # Se guarda la duración como atributo protegido
        self._duracion = duracion
        # Toda reserva inicia en estado pendiente
        self._estado = Reserva.PENDIENTE
        # El descuento inicia en cero hasta que se aplique alguno
        self._descuento = 0.0
        # El costo total se conoce solo después de procesar la reserva
        self._costo_total = None
        # Con los datos validados se asigna el identificador de la entidad
        super().__init__()

    # Propiedad de solo lectura para consultar el estado
    @property
    def estado(self):
        # Se retorna el atributo protegido
        return self._estado

    # Propiedad de solo lectura para consultar el costo total
    @property
    def costo_total(self):
        # Se retorna el atributo protegido
        return self._costo_total

    # Método sobrecargado: versión base para tipos de dato no admitidos
    @singledispatchmethod
    def aplicar_descuento(self, valor):
        # Cualquier tipo distinto de número o texto se rechaza
        raise ErrorCalculo(f"Tipo de descuento no admitido: {type(valor).__name__}.")

    # Sobrecarga para porcentajes expresados como número decimal (por ejemplo 0.15)
    @aplicar_descuento.register
    def _(self, valor: float):
        # Se guarda el porcentaje; su rango se valida en el momento del cálculo
        self._descuento = valor
        # Se registra el evento en el archivo de logs
        logger.info("Reserva #%s: descuento por porcentaje registrado (%s).", self.id, valor)

    # Sobrecarga para porcentajes expresados como número entero (por ejemplo 0)
    @aplicar_descuento.register
    def _(self, valor: int):
        # Se guarda el porcentaje convertido a decimal
        self._descuento = float(valor)
        # Se registra el evento en el archivo de logs
        logger.info("Reserva #%s: descuento por porcentaje registrado (%s).", self.id, valor)

    # Sobrecarga para códigos promocionales expresados como texto (por ejemplo "FJ10")
    @aplicar_descuento.register
    def _(self, valor: str):
        # Se normaliza el código: sin espacios sobrantes y en mayúsculas
        codigo = valor.strip().upper()
        # El código debe existir en el diccionario de códigos vigentes
        if codigo not in self._CODIGOS_PROMOCIONALES:
            # Se rechaza un código promocional inexistente
            raise ErrorCalculo(f"El código promocional '{valor}' no existe.")
        # Se guarda el descuento asociado al código
        self._descuento = self._CODIGOS_PROMOCIONALES[codigo]
        # Se registra el evento en el archivo de logs
        logger.info("Reserva #%s: código promocional %s aplicado.", self.id, codigo)

    # Confirma la reserva: uso de try/except/else
    def confirmar(self):
        # Se intentan las verificaciones previas a la confirmación
        try:
            # Solo se puede confirmar una reserva que esté pendiente
            if self._estado != Reserva.PENDIENTE:
                # Se rechaza la confirmación de una reserva en otro estado
                raise ErrorReserva(f"No se puede confirmar una reserva en estado {self._estado}.")
            # El servicio debe estar disponible en el momento de confirmar
            if not self._servicio.disponible:
                # Se rechaza la confirmación sobre un servicio no disponible
                raise ServicioNoDisponibleError(f"El servicio '{self._servicio.nombre}' no está disponible.")
        # Si alguna verificación falla, se registra y se propaga el error
        except ErrorSoftwareFJ as error:
            # Se registra el error en el archivo de logs
            logger.error("Reserva #%s: no se pudo confirmar. %s", self.id, error)
            # Se propaga el mismo error para que lo maneje quien llamó al método
            raise
        # El bloque else se ejecuta solo si no hubo ninguna excepción
        else:
            # Se cambia el estado de la reserva a confirmada
            self._estado = Reserva.CONFIRMADA
            # Se registra el evento en el archivo de logs
            logger.info("Reserva #%s confirmada.", self.id)

    # Cancela la reserva
    def cancelar(self):
        # No se puede cancelar una reserva ya procesada ni una ya cancelada
        if self._estado in (Reserva.PROCESADA, Reserva.CANCELADA):
            # Se registra el intento de operación no permitida
            logger.error("Reserva #%s: cancelación no permitida en estado %s.", self.id, self._estado)
            # Se rechaza la operación no permitida
            raise ErrorReserva(f"No se puede cancelar una reserva en estado {self._estado}.")
        # Se cambia el estado de la reserva a cancelada
        self._estado = Reserva.CANCELADA
        # Se registra el evento en el archivo de logs
        logger.info("Reserva #%s cancelada.", self.id)

    # Procesa la reserva y calcula el costo: uso de try/except/else/finally
    def procesar(self, impuesto=None):
        # Solo se puede procesar una reserva confirmada
        if self._estado != Reserva.CONFIRMADA:
            # Se registra el intento de operación no permitida
            logger.error("Reserva #%s: no se puede procesar en estado %s.", self.id, self._estado)
            # Se rechaza la operación no permitida
            raise ErrorReserva(f"Solo se pueden procesar reservas confirmadas (estado actual: {self._estado}).")
        # Se intenta el cálculo del costo
        try:
            # Polimorfismo: cada servicio calcula el costo con sus propias reglas
            total = self._servicio.calcular_costo(self._duracion, impuesto, self._descuento)
        # Se capturan los errores de cálculo y los errores de tipo de dato
        except (ErrorCalculo, TypeError) as error:
            # Encadenamiento de excepciones: el error de cálculo queda como causa del error de reserva
            raise ErrorReserva(f"La reserva #{self.id} no se pudo procesar por un error de cálculo.") from error
        # El bloque else se ejecuta solo si el cálculo terminó sin excepciones
        else:
            # Se guarda el costo total calculado
            self._costo_total = total
            # Se cambia el estado de la reserva a procesada
            self._estado = Reserva.PROCESADA
            # Se registra el evento en el archivo de logs
            logger.info("Reserva #%s procesada. Costo total: %.2f", self.id, total)
            # Se retorna el costo total
            return total
        # El bloque finally se ejecuta siempre, haya o no excepción
        finally:
            # Se deja constancia del intento y del estado final de la reserva
            logger.debug("Reserva #%s: fin del intento de procesamiento (estado: %s).", self.id, self._estado)

    # Implementación del método abstracto validar()
    def validar(self):
        # Una reserva es consistente si su duración sigue siendo válida para el servicio
        return self._servicio.validar_parametros(self._duracion)

    # Implementación del método abstracto describir()
    def describir(self):
        # El costo se muestra solo si la reserva ya fue procesada
        costo = f"${self._costo_total:,.2f}" if self._costo_total is not None else "sin calcular"
        # Se arma el texto con los datos de la reserva
        return (f"Reserva #{self.id}: {self._cliente.nombre} -> {self._servicio.nombre} | "
                f"Duración: {self._duracion} | Estado: {self._estado} | Costo: {costo}")


# Mensaje de confirmación en pantalla
print("Clase Reserva definida correctamente.")


# ==============================================================================
# 7. Clase `SistemaGestion`
# ==============================================================================
# Administra las listas internas de clientes, servicios y reservas. No usa ninguna base de datos. Cada operación registra en el log tanto los eventos correctos como los errores.

# Clase que administra las listas internas del sistema
class SistemaGestion:
    """Gestiona clientes, servicios y reservas usando listas en memoria."""

    # Diccionario que relaciona el nombre de cada tipo de servicio con su clase
    _TIPOS_SERVICIO = {"sala": ReservaSala, "equipo": AlquilerEquipo, "asesoria": AsesoriaEspecializada}

    # Constructor: crea las listas vacías
    def __init__(self):
        # Lista interna de clientes registrados
        self._clientes = []
        # Lista interna de servicios creados
        self._servicios = []
        # Lista interna de reservas creadas
        self._reservas = []

    # Registra un cliente: uso de try/except/else/finally
    def registrar_cliente(self, **datos):
        # Se intenta la creación del cliente con los datos recibidos
        try:
            # Si faltan parámetros, Python lanza TypeError; si son inválidos, ErrorValidacion
            cliente = Cliente(**datos)
            # Se revisa que no exista otro cliente con el mismo documento
            if any(existente.documento == cliente.documento for existente in self._clientes):
                # Se rechaza el registro duplicado
                raise ErrorCliente(f"Ya existe un cliente con el documento {cliente.documento}.")
        # Se captura la falta de parámetros obligatorios o los parámetros desconocidos
        except TypeError as error:
            # Se registra el error en el archivo de logs
            logger.error("Registro de cliente fallido por parámetros faltantes: %s", error)
            # Encadenamiento de excepciones: el TypeError queda como causa del error de cliente
            raise ErrorCliente("Faltan datos obligatorios para registrar el cliente.") from error
        # Se capturan los errores propios del sistema (validación o duplicados)
        except ErrorSoftwareFJ as error:
            # Se registra el error en el archivo de logs
            logger.error("Registro de cliente fallido: %s", error)
            # Se propaga el mismo error para que lo maneje quien llamó al método
            raise
        # El bloque else se ejecuta solo si no hubo ninguna excepción
        else:
            # Se agrega el cliente a la lista interna
            self._clientes.append(cliente)
            # Se registra el evento en el archivo de logs
            logger.info("Cliente registrado: %s", cliente.describir())
            # Se retorna el cliente creado
            return cliente
        # El bloque finally se ejecuta siempre, haya o no excepción
        finally:
            # Se deja constancia del total de clientes después del intento
            logger.debug("Intento de registro de cliente finalizado. Total de clientes: %d", len(self._clientes))

    # Crea un servicio del tipo indicado: uso de try/except/else
    def crear_servicio(self, tipo, **parametros):
        # Se busca la clase que corresponde al tipo solicitado
        clase_servicio = self._TIPOS_SERVICIO.get(tipo)
        # Si el tipo no existe en el diccionario, no hay clase asociada
        if clase_servicio is None:
            # Se registra el error en el archivo de logs
            logger.error("Creación de servicio fallida: tipo desconocido '%s'.", tipo)
            # Se rechaza el tipo de servicio desconocido
            raise ErrorServicio(f"Tipo de servicio desconocido: '{tipo}'.")
        # Se intenta la creación del servicio con los parámetros recibidos
        try:
            # Si faltan parámetros, Python lanza TypeError; si son inválidos, ErrorServicio
            servicio = clase_servicio(**parametros)
        # Se captura la falta de parámetros obligatorios o los parámetros desconocidos
        except TypeError as error:
            # Se registra el error en el archivo de logs
            logger.error("Creación de servicio fallida por parámetros faltantes: %s", error)
            # Encadenamiento de excepciones: el TypeError queda como causa del error de servicio
            raise ErrorServicio(f"Faltan parámetros para crear el servicio de tipo '{tipo}'.") from error
        # Se capturan los errores propios del sistema
        except ErrorSoftwareFJ as error:
            # Se registra el error en el archivo de logs
            logger.error("Creación de servicio fallida: %s", error)
            # Se propaga el mismo error para que lo maneje quien llamó al método
            raise
        # El bloque else se ejecuta solo si no hubo ninguna excepción
        else:
            # Se agrega el servicio a la lista interna
            self._servicios.append(servicio)
            # Se registra el evento en el archivo de logs
            logger.info("Servicio creado: %s", servicio.describir())
            # Se retorna el servicio creado
            return servicio

    # Busca un cliente por su documento
    def buscar_cliente(self, documento):
        # Se recorre la lista interna de clientes
        for cliente in self._clientes:
            # Se compara el documento como texto para aceptar números o textos
            if cliente.documento == str(documento):
                # Se retorna el cliente encontrado
                return cliente
        # Si el ciclo termina sin coincidencias, el cliente no está registrado
        raise ErrorCliente(f"No existe un cliente registrado con el documento {documento}.")

    # Busca un servicio por su nombre
    def buscar_servicio(self, nombre):
        # Se recorre la lista interna de servicios
        for servicio in self._servicios:
            # Se compara el nombre sin distinguir mayúsculas de minúsculas
            if servicio.nombre.lower() == str(nombre).strip().lower():
                # Se retorna el servicio encontrado
                return servicio
        # Si el ciclo termina sin coincidencias, el servicio no existe
        raise ErrorServicio(f"No existe un servicio con el nombre '{nombre}'.")

    # Crea una reserva a partir del documento del cliente y el nombre del servicio
    def crear_reserva(self, documento, nombre_servicio, duracion):
        # Se intenta la creación de la reserva
        try:
            # Se busca el cliente; lanza ErrorCliente si no existe
            cliente = self.buscar_cliente(documento)
            # Se busca el servicio; lanza ErrorServicio si no existe
            servicio = self.buscar_servicio(nombre_servicio)
            # Se crea la reserva; lanza ErrorValidacion si la duración no es válida
            reserva = Reserva(cliente, servicio, duracion)
        # Se capturan los errores propios del sistema
        except ErrorSoftwareFJ as error:
            # Se registra el error en el archivo de logs
            logger.error("Creación de reserva fallida: %s", error)
            # Se propaga el mismo error para que lo maneje quien llamó al método
            raise
        # El bloque else se ejecuta solo si no hubo ninguna excepción
        else:
            # Se agrega la reserva a la lista interna
            self._reservas.append(reserva)
            # Se registra el evento en el archivo de logs
            logger.info("Reserva creada: %s", reserva.describir())
            # Se retorna la reserva creada
            return reserva

    # Retorna una copia de la lista de clientes para proteger la lista interna
    def listar_clientes(self):
        # Se retorna una copia y no la lista original
        return list(self._clientes)

    # Retorna una copia de la lista de servicios para proteger la lista interna
    def listar_servicios(self):
        # Se retorna una copia y no la lista original
        return list(self._servicios)

    # Retorna una copia de la lista de reservas para proteger la lista interna
    def listar_reservas(self):
        # Se retorna una copia y no la lista original
        return list(self._reservas)


# Mensaje de confirmación en pantalla
print("Clase SistemaGestion definida correctamente.")


# ==============================================================================
# 8. Simulación de operaciones
# ==============================================================================
# La función ejecutar_simulacion() envuelve cada operación en un bloque try/except/else/finally. Si la operación falla, el error se muestra de forma controlada, se registra en el log y el sistema continúa con la siguiente operación sin detenerse.
# Se ejecutan 16 operaciones: registros válidos e inválidos de clientes, creación correcta e incorrecta de servicios, y reservas exitosas y fallidas.

# Se crea la instancia única del sistema que usan todas las simulaciones
sistema = SistemaGestion()

# Diccionario que acumula el resultado de las simulaciones
resultados = {"exitosas": 0, "controladas": 0, "inesperadas": 0}


# Función que ejecuta una simulación sin permitir que un error detenga el programa
def ejecutar_simulacion(numero, descripcion, operacion):
    # Se muestra el encabezado de la simulación en pantalla
    print(f"--- Simulación {numero}: {descripcion}")
    # Se registra el inicio de la simulación en el archivo de logs
    logger.info("Simulación %s iniciada: %s", numero, descripcion)
    # Se intenta la ejecución de la operación recibida como función
    try:
        # Se invoca la operación y se guarda lo que retorne
        resultado = operacion()
    # Se capturan los errores propios del sistema: son errores previstos y controlados
    except ErrorSoftwareFJ as error:
        # Se suma una simulación con error controlado
        resultados["controladas"] += 1
        # Se muestra el tipo y el mensaje del error en pantalla
        print(f"    ERROR CONTROLADO [{type(error).__name__}]: {error}")
        # Si la excepción tiene una causa, se trata de un encadenamiento de excepciones
        if error.__cause__ is not None:
            # Se muestra el error original que provocó la excepción
            print(f"    Causa original [{type(error.__cause__).__name__}]: {error.__cause__}")
        # Se registra el error en el archivo de logs
        logger.error("Simulación %s: error controlado [%s] %s", numero, type(error).__name__, error)
    # Se captura cualquier otro error no previsto para que la aplicación no se detenga
    except Exception as error:
        # Se suma una simulación con error inesperado
        resultados["inesperadas"] += 1
        # Se muestra el error inesperado en pantalla
        print(f"    ERROR INESPERADO [{type(error).__name__}]: {error}")
        # Se registra el error con la traza completa en el archivo de logs
        logger.exception("Simulación %s: error inesperado.", numero)
    # El bloque else se ejecuta solo si la operación terminó sin excepciones
    else:
        # Se suma una simulación exitosa
        resultados["exitosas"] += 1
        # Se muestra el resultado de la operación en pantalla
        print(f"    OPERACIÓN EXITOSA: {resultado}")
        # Se registra el resultado en el archivo de logs
        logger.info("Simulación %s: operación exitosa.", numero)
    # El bloque finally se ejecuta siempre, haya o no excepción
    finally:
        # Se confirma en pantalla que el sistema sigue en funcionamiento
        print("    El sistema continúa en funcionamiento.\n")


# Mensaje de confirmación en pantalla
print("Sistema inicializado y función de simulación lista.")


# ==============================================================================
# Simulaciones 1 a 4: registro de clientes
# ==============================================================================

# Simulación 1: registro válido de un cliente
ejecutar_simulacion(1, "Registro válido de un cliente", lambda: sistema.registrar_cliente(
    nombre="Laura Gómez", documento="1144055321", correo="laura.gomez@correo.com", telefono="3105557788"))

# Simulación 2: registro inválido por correo electrónico con formato incorrecto
ejecutar_simulacion(2, "Registro de cliente con correo inválido", lambda: sistema.registrar_cliente(
    nombre="Carlos Ruiz", documento="94567123", correo="carlos.ruiz-sin-arroba", telefono="3004441122"))

# Simulación 3: registro inválido por documento duplicado (ya usado en la simulación 1)
ejecutar_simulacion(3, "Registro de cliente con documento duplicado", lambda: sistema.registrar_cliente(
    nombre="Laura Patricia Gómez", documento="1144055321", correo="lpgomez@correo.com", telefono="3105550000"))

# Simulación 4: registro inválido por parámetros faltantes (no se envían correo ni teléfono)
ejecutar_simulacion(4, "Registro de cliente con parámetros faltantes", lambda: sistema.registrar_cliente(
    nombre="Andrés Mejía", documento="16789456"))


# ==============================================================================
# Simulaciones 5 a 8: creación de servicios
# ==============================================================================

# Función de apoyo que crea los servicios válidos del catálogo de Software FJ
def crear_catalogo():
    # Sala disponible con capacidad para 12 personas
    sistema.crear_servicio("sala", nombre="Sala Ejecutiva", tarifa_base=80000, capacidad=12)
    # Alquiler de tres computadores portátiles
    sistema.crear_servicio("equipo", nombre="Portátil Corporativo", tarifa_base=45000, cantidad=3)
    # Asesoría de nivel senior en ciberseguridad
    sistema.crear_servicio("asesoria", nombre="Asesoría en Ciberseguridad", tarifa_base=120000,
                           area="Seguridad informática", nivel="senior")
    # Sala creada como no disponible para probar reservas fallidas más adelante
    sistema.crear_servicio("sala", nombre="Auditorio Principal", tarifa_base=200000, capacidad=60,
                           disponible=False)
    # Se retorna el número de servicios creados como resultado de la operación
    return f"{len(sistema.listar_servicios())} servicios creados en el catálogo"


# Simulación 5: creación correcta de los servicios del catálogo
ejecutar_simulacion(5, "Creación correcta de servicios", crear_catalogo)

# Simulación 6: creación incorrecta por tarifa negativa
ejecutar_simulacion(6, "Creación de servicio con tarifa negativa", lambda: sistema.crear_servicio(
    "sala", nombre="Sala Económica", tarifa_base=-50000, capacidad=8))

# Simulación 7: creación incorrecta por tipo de servicio inexistente
ejecutar_simulacion(7, "Creación de servicio de tipo inexistente", lambda: sistema.crear_servicio(
    "transporte", nombre="Transporte Ejecutivo", tarifa_base=90000))

# Simulación 8: creación incorrecta por parámetros faltantes (no se envía el área de la asesoría)
ejecutar_simulacion(8, "Creación de servicio con parámetros faltantes", lambda: sistema.crear_servicio(
    "asesoria", nombre="Asesoría en Redes", tarifa_base=100000))


# ==============================================================================
# Simulaciones 9 a 16: reservas
# ==============================================================================

# Función de apoyo: reserva completa de una sala con el impuesto por defecto
def reserva_sala_exitosa():
    # Se crea la reserva de la sala por 3 horas
    reserva = sistema.crear_reserva("1144055321", "Sala Ejecutiva", 3)
    # Se confirma la reserva
    reserva.confirmar()
    # Se procesa con la primera variante del cálculo: IVA por defecto y sin descuento
    reserva.procesar()
    # Se retorna la descripción de la reserva como resultado de la operación
    return reserva.describir()


# Función de apoyo: reserva completa de una asesoría con código promocional e impuesto distinto
def reserva_asesoria_con_descuento():
    # Se crea la reserva de la asesoría por 2 horas
    reserva = sistema.crear_reserva("1144055321", "Asesoría en Ciberseguridad", 2)
    # Método sobrecargado: en este caso recibe un texto (código promocional)
    reserva.aplicar_descuento("FJ10")
    # Se confirma la reserva
    reserva.confirmar()
    # Se procesa con otra variante del cálculo: impuesto del 5 % en lugar del IVA por defecto
    reserva.procesar(impuesto=0.05)
    # Se retorna la descripción de la reserva como resultado de la operación
    return reserva.describir()


# Función de apoyo: intento de confirmar una reserva sobre un servicio no disponible
def reserva_servicio_no_disponible():
    # La reserva se puede crear porque los datos son válidos
    reserva = sistema.crear_reserva("1144055321", "Auditorio Principal", 4)
    # La confirmación falla porque el auditorio está marcado como no disponible
    reserva.confirmar()
    # Esta línea no se alcanza porque la confirmación lanza una excepción
    return reserva.describir()


# Función de apoyo: intento de procesar una reserva con un descuento inconsistente
def reserva_calculo_inconsistente():
    # Se crea la reserva del alquiler de equipos por 5 días
    reserva = sistema.crear_reserva("1144055321", "Portátil Corporativo", 5)
    # Método sobrecargado: en este caso recibe un número (descuento del 150 %, inconsistente)
    reserva.aplicar_descuento(1.5)
    # Se confirma la reserva
    reserva.confirmar()
    # El procesamiento falla: ErrorCalculo se encadena como causa de ErrorReserva
    reserva.procesar()
    # Esta línea no se alcanza porque el procesamiento lanza una excepción
    return reserva.describir()


# Función de apoyo: intento de cancelar una reserva que ya fue procesada
def cancelar_reserva_procesada():
    # Se toma la primera reserva del sistema, procesada en la simulación 9
    reserva = sistema.listar_reservas()[0]
    # La cancelación falla porque una reserva procesada no se puede cancelar
    reserva.cancelar()
    # Esta línea no se alcanza porque la cancelación lanza una excepción
    return reserva.describir()


# Función de apoyo: cancelación válida de una reserva pendiente
def cancelar_reserva_pendiente():
    # Se crea una reserva nueva de equipos por 2 días, que queda en estado pendiente
    reserva = sistema.crear_reserva("1144055321", "Portátil Corporativo", 2)
    # Se cancela la reserva pendiente, operación permitida
    reserva.cancelar()
    # Se retorna la descripción de la reserva como resultado de la operación
    return reserva.describir()


# Simulación 9: reserva exitosa de una sala
ejecutar_simulacion(9, "Reserva exitosa de una sala (IVA por defecto)", reserva_sala_exitosa)

# Simulación 10: reserva exitosa de una asesoría con descuento
ejecutar_simulacion(10, "Reserva exitosa de una asesoría con código promocional", reserva_asesoria_con_descuento)

# Simulación 11: reserva fallida porque el cliente no está registrado
ejecutar_simulacion(11, "Reserva con un cliente no registrado",
                    lambda: sistema.crear_reserva("99999999", "Sala Ejecutiva", 2))

# Simulación 12: reserva fallida porque la duración supera el máximo permitido para una sala
ejecutar_simulacion(12, "Reserva con duración fuera del rango permitido",
                    lambda: sistema.crear_reserva("1144055321", "Sala Ejecutiva", 15))

# Simulación 13: reserva fallida porque el servicio no está disponible
ejecutar_simulacion(13, "Reserva sobre un servicio no disponible", reserva_servicio_no_disponible)

# Simulación 14: reserva fallida por un cálculo inconsistente (encadenamiento de excepciones)
ejecutar_simulacion(14, "Reserva con cálculo inconsistente (descuento del 150 %)", reserva_calculo_inconsistente)

# Simulación 15: operación no permitida al cancelar una reserva ya procesada
ejecutar_simulacion(15, "Cancelación de una reserva ya procesada", cancelar_reserva_procesada)

# Simulación 16: cancelación válida de una reserva pendiente
ejecutar_simulacion(16, "Cancelación válida de una reserva pendiente", cancelar_reserva_pendiente)


# ==============================================================================
# 9. Resumen final y contenido del archivo de logs
# ==============================================================================
# Se muestra el estado final de las listas internas del sistema, que demuestra que la aplicación terminó todas las operaciones sin detenerse, y luego las líneas registradas en software_fj.log.

# Encabezado del resumen de simulaciones
print("RESUMEN DE SIMULACIONES")
# Total de simulaciones ejecutadas: suma de los tres contadores
print(f"Total ejecutadas     : {sum(resultados.values())}")
# Simulaciones que terminaron sin errores
print(f"Operaciones exitosas : {resultados['exitosas']}")
# Simulaciones con errores previstos y controlados por el sistema
print(f"Errores controlados  : {resultados['controladas']}")
# Simulaciones con errores no previstos (se espera cero)
print(f"Errores inesperados  : {resultados['inesperadas']}")

# Encabezado de la lista de clientes
print("\nCLIENTES REGISTRADOS")
# Se recorre la lista de clientes
for cliente in sistema.listar_clientes():
    # Se imprime la descripción de cada cliente
    print(" ", cliente)

# Encabezado de la lista de servicios
print("\nSERVICIOS CREADOS")
# Se recorre la lista de servicios
for servicio in sistema.listar_servicios():
    # Polimorfismo: cada servicio se describe con su propia implementación
    print(" ", servicio)

# Encabezado de la lista de reservas
print("\nRESERVAS")
# Se recorre la lista de reservas
for reserva in sistema.listar_reservas():
    # Se imprime la descripción de cada reserva
    print(" ", reserva)

# Se registra el cierre de la ejecución en el archivo de logs
logger.info("===== Fin de ejecución: %d exitosas, %d errores controlados, %d inesperados =====",
            resultados["exitosas"], resultados["controladas"], resultados["inesperadas"])

# Se fuerza la escritura en disco de las líneas pendientes del log
manejador_archivo.flush()

# Se abre el archivo de logs en modo lectura; el bloque with garantiza su cierre
with open(ARCHIVO_LOG, "r", encoding="utf-8") as archivo:
    # Se leen todas las líneas del archivo
    lineas = archivo.readlines()

# Se muestra el total de líneas registradas
print(f"Archivo {ARCHIVO_LOG}: {len(lineas)} líneas registradas.\n")
# Se recorren las líneas del archivo
for linea in lineas:
    # Se imprime cada línea sin el salto de línea final
    print(linea.rstrip())
