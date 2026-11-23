# Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ

Proyecto de la **Fase 4 - Componente práctico - Prácticas simuladas** del curso **Programación (213023)** de la Universidad Nacional Abierta y a Distancia (UNAD).

- **Grupo:** 213023_343
- **Estudiante:** Julian Alberto Rosero Camacho
- **Tutor:** Juan Pablo Arango Cardona
- **Programa:** Ingeniería de Sistemas - ECBTI

## Descripción

Sistema orientado a objetos, desarrollado en Python, que gestiona los clientes, los servicios y las reservas de la empresa Software FJ. La empresa ofrece tres tipos de servicio: reserva de salas, alquiler de equipos y asesorías especializadas.

El sistema no utiliza bases de datos. Toda la información se administra con objetos y listas en memoria, y solo se usa un archivo (`software_fj.log`) para registrar los eventos y los errores.

El objetivo de la práctica es aplicar el manejo de excepciones para que la aplicación se mantenga estable y continúe funcionando aunque se presenten errores durante su ejecución.

## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| `Fase4_SoftwareFJ.ipynb` | Cuaderno con el código fuente documentado, las simulaciones y sus resultados |
| `software_fj.log` | Archivo de logs generado por la ejecución del cuaderno |
| `software_fj.py` | Mismo código del cuaderno en un script de Python |
| `test_software_fj.py` | Pruebas automatizadas del manejo de excepciones |
| `README.md` | Documentación del proyecto |

## Estructura del sistema

| Clase | Tipo | Responsabilidad |
|---|---|---|
| `Entidad` | Abstracta | Entidad general del sistema; asigna un identificador único y exige los métodos `describir()` y `validar()` |
| `Cliente` | Concreta | Datos personales encapsulados en atributos privados, con validación de nombre, documento, correo y teléfono |
| `Servicio` | Abstracta | Contrato común de los servicios: `calcular_costo()`, `describir()` y `validar_parametros()` |
| `ReservaSala` | Concreta | Servicio por horas (1 a 8), con recargo para salas de más de 20 personas |
| `AlquilerEquipo` | Concreta | Servicio por días (1 a 30), según la cantidad de equipos |
| `AsesoriaEspecializada` | Concreta | Servicio por horas (1 a 4), con tarifa según el nivel del asesor |
| `Reserva` | Concreta | Integra cliente, servicio, duración y estado; permite confirmar, cancelar y procesar |
| `SistemaGestion` | Concreta | Administra las listas internas de clientes, servicios y reservas |

## Conceptos aplicados

- **Abstracción:** clases abstractas `Entidad` y `Servicio` definidas con el módulo `abc`.
- **Herencia:** `Cliente`, `Servicio` y `Reserva` heredan de `Entidad`; los tres servicios especializados heredan de `Servicio`.
- **Polimorfismo:** cada servicio sobrescribe `calcular_costo()`, `describir()` y `validar_parametros()`.
- **Encapsulación:** atributos privados y protegidos expuestos mediante propiedades con validadores.
- **Sobrecarga de métodos:** `calcular_costo()` admite impuesto y descuento opcionales; `aplicar_descuento()` se comporta distinto según reciba un porcentaje numérico o un código promocional en texto (`functools.singledispatchmethod`).

## Manejo de excepciones

Excepciones personalizadas, todas derivadas de `ErrorSoftwareFJ`:

| Excepción | Se lanza cuando |
|---|---|
| `ErrorValidacion` | Un dato de entrada no cumple las reglas de validación |
| `ErrorCliente` | Un cliente está duplicado, no existe o le faltan datos |
| `ErrorServicio` | Un servicio se crea o se configura de forma incorrecta |
| `ServicioNoDisponibleError` | Se intenta reservar un servicio que no está disponible |
| `ErrorReserva` | Una reserva no se puede crear, confirmar, cancelar o procesar |
| `ErrorCalculo` | Un cálculo de costos produce un resultado inconsistente |

Estructuras utilizadas:

- `try/except` en la validación del documento del cliente.
- `try/except/else` en la confirmación de reservas y en la creación de servicios.
- `try/except/else/finally` en el registro de clientes, en el procesamiento de reservas y en la ejecución de cada simulación.
- Encadenamiento de excepciones con `raise ... from ...`, que conserva el error original como causa.

Cada error se registra en `software_fj.log` con fecha, hora y nivel de severidad, y la aplicación continúa con la siguiente operación.

## Simulaciones

El cuaderno ejecuta 16 operaciones completas:

| No. | Operación | Resultado esperado |
|---|---|---|
| 1 | Registro válido de un cliente | Exitosa |
| 2 | Registro de cliente con correo inválido | Error controlado |
| 3 | Registro de cliente con documento duplicado | Error controlado |
| 4 | Registro de cliente con parámetros faltantes | Error controlado |
| 5 | Creación correcta de servicios | Exitosa |
| 6 | Creación de servicio con tarifa negativa | Error controlado |
| 7 | Creación de servicio de tipo inexistente | Error controlado |
| 8 | Creación de servicio con parámetros faltantes | Error controlado |
| 9 | Reserva exitosa de una sala | Exitosa |
| 10 | Reserva exitosa de una asesoría con código promocional | Exitosa |
| 11 | Reserva con un cliente no registrado | Error controlado |
| 12 | Reserva con duración fuera del rango permitido | Error controlado |
| 13 | Reserva sobre un servicio no disponible | Error controlado |
| 14 | Reserva con cálculo inconsistente | Error controlado |
| 15 | Cancelación de una reserva ya procesada | Error controlado |
| 16 | Cancelación válida de una reserva pendiente | Exitosa |

Resultado: 5 operaciones exitosas, 11 errores controlados y 0 errores inesperados.

## Pruebas automatizadas

Aporte de **Leonardo Izquierdo Henao**. El archivo `test_software_fj.py` comprueba con `unittest` que cada parte del manejo de excepciones funcione por separado, sin depender del orden de las simulaciones. Cada prueba crea un sistema nuevo y escribe su log en una carpeta temporal, así que no modifica `software_fj.log`.

| Grupo de pruebas | Qué verifica |
|---|---|
| `TestExcepcionesPersonalizadas` | Que todas las excepciones hereden de `ErrorSoftwareFJ` y que `ServicioNoDisponibleError` sea un `ErrorServicio` |
| `TestAbstraccionYEncapsulacion` | Que `Entidad` y `Servicio` no se puedan instanciar y que el cliente valide y encapsule su correo |
| `TestPolimorfismoDeServicios` | El costo de cada servicio con sus reglas propias (recargo de salas grandes, cantidad de equipos, nivel del asesor) y su rango de duración |
| `TestSobrecarga` | Las variantes de `calcular_costo()` y de `aplicar_descuento()` según el tipo del argumento |
| `TestEncadenamiento` | Que `raise ... from ...` conserve la causa original (`ErrorCalculo` o `TypeError`) en `__cause__` |
| `TestCicloDeReserva` | Los bloques `else` y `finally` de `procesar()`, la confirmación de servicios no disponibles y las reglas de cancelación |
| `TestLogsYEstabilidad` | Que los errores queden en el log y que `ejecutar_simulacion()` no deje escapar errores controlados ni inesperados |

Ejecución (23 pruebas):

```bash
python -m unittest -v test_software_fj.py
```

## Cómo ejecutar

Requisitos: Python 3.10 o superior y Jupyter. El proyecto usa únicamente la biblioteca estándar de Python.

1. Clonar el repositorio o descargar el archivo `Fase4_SoftwareFJ.ipynb`.
2. Abrir el cuaderno en Jupyter Notebook, JupyterLab, Visual Studio Code o Google Colab.
3. Ejecutar las celdas en orden, de la primera a la última.

Al finalizar, el archivo `software_fj.log` queda en la misma carpeta del cuaderno.

## Referencias

Cuevas Álvarez, A. (2016). *Python 3: curso práctico*. RA-MA Editorial.

Van Rossum, G., & Drake Jr, F. L. (2024). *El tutorial de Python*. Python Software Foundation. https://docs.python.org/es/3.12/tutorial/errors.html
