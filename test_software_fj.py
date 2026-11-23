"""
Fase 4 - Componente práctico - Prácticas simuladas
Curso: Programación (213023) - UNAD
Grupo: 213023_343
Aporte: Leonardo Izquierdo Henao

Pruebas automatizadas del sistema Software FJ (software_fj.py).
Cada prueba ejecuta una parte del código de forma aislada y comprueba que el
manejo de excepciones se comporte como lo pide el Anexo 3: excepciones
personalizadas, try/except/else, try/except/finally, encadenamiento de
excepciones, registro en el archivo de logs y continuidad del sistema ante
errores.
Ejecución: python -m unittest -v test_software_fj.py
"""

# Módulo para redirigir la salida estándar mientras se importa el sistema
import contextlib
# Módulo para leer y escribir texto en memoria (descarta los mensajes de las simulaciones)
import io
# Módulo para manejar rutas y cambiar el directorio de trabajo
import os
# Módulo para agregar la carpeta del proyecto a la ruta de importación
import sys
# Módulo para crear una carpeta temporal donde se escribe el log de las pruebas
import tempfile
# Marco de pruebas unitarias de la biblioteca estándar de Python
import unittest

# Carpeta donde está este archivo, que es la misma de software_fj.py
CARPETA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
# Se agrega la carpeta del proyecto a la ruta para poder importar software_fj
sys.path.insert(0, CARPETA_PROYECTO)

# Variable global que guardará el módulo importado
fj = None
# Variable global que guardará la carpeta temporal de las pruebas
carpeta_temporal = None
# Variable global que guardará el directorio de trabajo original
directorio_original = None


# Función que unittest ejecuta una sola vez antes de todas las pruebas del archivo
def setUpModule():
    # Se declaran las variables globales que esta función va a modificar
    global fj, carpeta_temporal, directorio_original
    # Se guarda el directorio actual para restaurarlo al terminar
    directorio_original = os.getcwd()
    # Se crea una carpeta temporal para que el log de las pruebas no altere software_fj.log del repositorio
    carpeta_temporal = tempfile.TemporaryDirectory()
    # Se cambia el directorio de trabajo: el log del sistema se crea con ruta relativa
    os.chdir(carpeta_temporal.name)
    # Al importar el módulo se ejecutan sus 16 simulaciones; su salida en pantalla se descarta
    with contextlib.redirect_stdout(io.StringIO()):
        # Se importa el sistema Software FJ
        import software_fj as modulo
    # Se guarda el módulo importado en la variable global
    fj = modulo


# Función que unittest ejecuta una sola vez después de todas las pruebas del archivo
def tearDownModule():
    # Se cierran los manejadores del log para liberar el archivo antes de borrar la carpeta
    for manejador in list(fj.logger.handlers):
        # Se cierra el manejador del archivo
        manejador.close()
    # Se vuelve al directorio de trabajo original
    os.chdir(directorio_original)
    # Se elimina la carpeta temporal con su archivo de logs
    carpeta_temporal.cleanup()


# Función de apoyo que lee el contenido actual del archivo de logs de las pruebas
def leer_log():
    # Se vacía el búfer de cada manejador para que todo lo registrado quede en el archivo
    for manejador in fj.logger.handlers:
        # Se fuerza la escritura pendiente
        manejador.flush()
    # Se abre el archivo de logs creado en la carpeta temporal
    with open(os.path.join(carpeta_temporal.name, fj.ARCHIVO_LOG), encoding="utf-8") as archivo:
        # Se retorna todo el texto del log
        return archivo.read()


# Clase base con un sistema nuevo y un catálogo mínimo para cada prueba
class PruebaConSistema(unittest.TestCase):

    # Método que unittest ejecuta antes de cada prueba
    def setUp(self):
        # Se crea un sistema vacío para que las pruebas no dependan unas de otras
        self.sistema = fj.SistemaGestion()
        # Se registra un cliente válido que usan las reservas
        self.cliente = self.sistema.registrar_cliente(
            nombre="Ana Torres", documento="52123456", correo="ana.torres@correo.com", telefono="3012223344")
        # Se crea una sala disponible de 12 personas
        self.sala = self.sistema.crear_servicio("sala", nombre="Sala Norte", tarifa_base=80000, capacidad=12)
        # Se crea un alquiler de tres equipos
        self.equipo = self.sistema.crear_servicio("equipo", nombre="Proyector HD", tarifa_base=45000, cantidad=3)
        # Se crea una asesoría de nivel senior
        self.asesoria = self.sistema.crear_servicio(
            "asesoria", nombre="Asesoría en Redes", tarifa_base=120000, area="Redes", nivel="senior")
        # Se crea una sala marcada como no disponible
        self.sala_cerrada = self.sistema.crear_servicio(
            "sala", nombre="Sala Cerrada", tarifa_base=90000, capacidad=10, disponible=False)


# Pruebas de la jerarquía de excepciones personalizadas
class TestExcepcionesPersonalizadas(unittest.TestCase):

    # Todas las excepciones del sistema deben heredar de ErrorSoftwareFJ
    def test_todas_heredan_de_la_excepcion_base(self):
        # Lista de las excepciones personalizadas definidas en software_fj.py
        excepciones = [fj.ErrorValidacion, fj.ErrorCliente, fj.ErrorServicio,
                       fj.ServicioNoDisponibleError, fj.ErrorReserva, fj.ErrorCalculo]
        # Se recorre cada excepción de la lista
        for excepcion in excepciones:
            # subTest identifica cuál excepción falla, si alguna no cumple
            with self.subTest(excepcion=excepcion.__name__):
                # Se comprueba la herencia de la excepción base del sistema
                self.assertTrue(issubclass(excepcion, fj.ErrorSoftwareFJ))

    # Un servicio no disponible es un caso particular de error de servicio
    def test_servicio_no_disponible_es_error_de_servicio(self):
        # Se comprueba la herencia de segundo nivel
        self.assertTrue(issubclass(fj.ServicioNoDisponibleError, fj.ErrorServicio))


# Pruebas de abstracción y encapsulación
class TestAbstraccionYEncapsulacion(PruebaConSistema):

    # Las clases abstractas no se pueden instanciar directamente
    def test_clases_abstractas_no_se_instancian(self):
        # Instanciar Entidad debe fallar porque tiene métodos abstractos
        with self.assertRaises(TypeError):
            # Intento de instanciar la clase abstracta Entidad
            fj.Entidad()
        # Instanciar Servicio también debe fallar por la misma razón
        with self.assertRaises(TypeError):
            # Intento de instanciar la clase abstracta Servicio
            fj.Servicio("Servicio genérico", 1000)

    # Un correo con formato inválido se rechaza con ErrorValidacion
    def test_cliente_rechaza_correo_invalido(self):
        # Se espera el error de validación del setter del correo
        with self.assertRaises(fj.ErrorValidacion):
            # Cliente con un correo sin arroba
            fj.Cliente("Pedro Díaz", "80123456", "pedro-sin-arroba", "3001112233")

    # El correo se guarda en un atributo privado y se normaliza en minúsculas
    def test_cliente_encapsula_y_normaliza_el_correo(self):
        # Se crea un cliente con el correo en mayúsculas y con espacios
        cliente = fj.Cliente("Pedro Díaz", "80123456", "  Pedro.Diaz@Correo.COM ", "3001112233")
        # La propiedad devuelve el correo limpio y en minúsculas
        self.assertEqual(cliente.correo, "pedro.diaz@correo.com")
        # El atributo privado no es accesible con su nombre directo
        self.assertFalse(hasattr(cliente, "__correo"))


# Pruebas del polimorfismo: cada servicio calcula su costo con reglas propias
class TestPolimorfismoDeServicios(PruebaConSistema):

    # La sala cobra tarifa por hora más el IVA por defecto (19 %)
    def test_costo_de_sala(self):
        # 80.000 x 3 horas x 1,19 = 285.600
        self.assertEqual(self.sala.calcular_costo(3), 285600.0)

    # Una sala de más de 20 personas tiene un recargo del 15 %
    def test_recargo_de_sala_grande(self):
        # Se crea una sala de 30 personas
        auditorio = fj.ReservaSala("Auditorio Sur", 100000, 30)
        # 100.000 x 2 horas x 1,15 x 1,19 = 273.700
        self.assertAlmostEqual(auditorio.calcular_costo(2), 273700.0, places=2)

    # El alquiler cobra por día y por equipo
    def test_costo_de_alquiler_de_equipos(self):
        # 45.000 x 5 días x 3 equipos x 1,19 = 803.250
        self.assertEqual(self.equipo.calcular_costo(5), 803250.0)

    # La asesoría aplica el factor del nivel del asesor
    def test_costo_de_asesoria_senior(self):
        # 120.000 x 2 horas x 1,5 (senior), sin impuesto = 360.000
        self.assertEqual(self.asesoria.calcular_costo(2, impuesto=0), 360000.0)

    # Cada servicio valida su propio rango de duración
    def test_rangos_de_duracion_por_servicio(self):
        # Casos fuera de rango: sala hasta 8 h, equipo hasta 30 días, asesoría hasta 4 h
        casos = [(self.sala, 9), (self.equipo, 31), (self.asesoria, 5), (self.sala, 0)]
        # Se recorre cada caso
        for servicio, duracion in casos:
            # subTest indica el servicio y la duración que fallan
            with self.subTest(servicio=servicio.nombre, duracion=duracion):
                # Una duración fuera de rango produce ErrorValidacion
                with self.assertRaises(fj.ErrorValidacion):
                    # Se calcula el costo con la duración inválida
                    servicio.calcular_costo(duracion)


# Pruebas de la sobrecarga de métodos
class TestSobrecarga(PruebaConSistema):

    # calcular_costo acepta impuesto y descuento opcionales
    def test_calcular_costo_con_impuesto_y_descuento(self):
        # 80.000 x 2 horas x 0,90 (descuento) x 1,05 (impuesto) = 151.200
        self.assertAlmostEqual(self.sala.calcular_costo(2, impuesto=0.05, descuento=0.10), 151200.0, places=2)

    # aplicar_descuento se comporta distinto según el tipo del argumento
    def test_aplicar_descuento_segun_el_tipo(self):
        # Se crea una reserva pendiente sobre la sala
        reserva = self.sistema.crear_reserva("52123456", "Sala Norte", 2)
        # Con un texto se interpreta como código promocional
        reserva.aplicar_descuento("fj20")
        # El código FJ20 equivale a un descuento del 20 %
        self.assertEqual(reserva._descuento, 0.20)
        # Con un número decimal se interpreta como proporción
        reserva.aplicar_descuento(0.15)
        # El descuento queda registrado tal cual
        self.assertEqual(reserva._descuento, 0.15)

    # Un código promocional inexistente o un tipo no admitido producen ErrorCalculo
    def test_descuentos_no_validos(self):
        # Se crea una reserva pendiente sobre la sala
        reserva = self.sistema.crear_reserva("52123456", "Sala Norte", 2)
        # Código que no existe en el diccionario de códigos promocionales
        with self.assertRaises(fj.ErrorCalculo):
            # Se aplica el código inexistente
            reserva.aplicar_descuento("NAVIDAD")
        # Una lista no tiene una variante registrada del método sobrecargado
        with self.assertRaises(fj.ErrorCalculo):
            # Se aplica un descuento de tipo no admitido
            reserva.aplicar_descuento([10])


# Pruebas del encadenamiento de excepciones (raise ... from ...)
class TestEncadenamiento(PruebaConSistema):

    # Un error de cálculo al procesar se encadena dentro de ErrorReserva
    def test_procesar_encadena_el_error_de_calculo(self):
        # Se crea y confirma una reserva sobre el alquiler de equipos
        reserva = self.sistema.crear_reserva("52123456", "Proyector HD", 2)
        # Se registra un descuento del 150 %, que hace inconsistente el cálculo
        reserva.aplicar_descuento(1.5)
        # Se confirma la reserva para poder procesarla
        reserva.confirmar()
        # Se espera el error de reserva
        with self.assertRaises(fj.ErrorReserva) as contexto:
            # Se intenta procesar la reserva
            reserva.procesar()
        # La causa original queda en __cause__ y es un ErrorCalculo
        self.assertIsInstance(contexto.exception.__cause__, fj.ErrorCalculo)

    # Los parámetros faltantes (TypeError de Python) se encadenan en errores propios
    def test_parametros_faltantes_se_encadenan(self):
        # Registro de cliente sin correo ni teléfono
        with self.assertRaises(fj.ErrorCliente) as contexto_cliente:
            # Se intenta registrar el cliente incompleto
            self.sistema.registrar_cliente(nombre="Luis Prada", documento="71234567")
        # La causa original es el TypeError del constructor
        self.assertIsInstance(contexto_cliente.exception.__cause__, TypeError)
        # Creación de una asesoría sin el área obligatoria
        with self.assertRaises(fj.ErrorServicio) as contexto_servicio:
            # Se intenta crear el servicio incompleto
            self.sistema.crear_servicio("asesoria", nombre="Asesoría Cloud", tarifa_base=100000)
        # La causa original también es un TypeError
        self.assertIsInstance(contexto_servicio.exception.__cause__, TypeError)


# Pruebas de los bloques else y finally en el ciclo de vida de una reserva
class TestCicloDeReserva(PruebaConSistema):

    # Si no hay errores, el bloque else de procesar() guarda el costo y cambia el estado
    def test_procesamiento_exitoso(self):
        # Se crea la reserva de la sala por 3 horas
        reserva = self.sistema.crear_reserva("52123456", "Sala Norte", 3)
        # Se confirma la reserva
        reserva.confirmar()
        # Se procesa con el IVA por defecto
        total = reserva.procesar()
        # El total retornado coincide con el costo de la sala
        self.assertEqual(total, 285600.0)
        # El estado final es PROCESADA
        self.assertEqual(reserva.estado, fj.Reserva.PROCESADA)
        # El costo queda guardado en la reserva
        self.assertEqual(reserva.costo_total, 285600.0)

    # Si procesar() falla, el estado no cambia y el bloque finally igual se ejecuta
    def test_procesamiento_fallido_conserva_el_estado(self):
        # Se crea y confirma una reserva con un descuento inválido
        reserva = self.sistema.crear_reserva("52123456", "Proyector HD", 2)
        # Descuento del 100 %, fuera del rango permitido
        reserva.aplicar_descuento(1.0)
        # Se confirma la reserva
        reserva.confirmar()
        # El procesamiento debe fallar
        with self.assertRaises(fj.ErrorReserva):
            # Se intenta procesar la reserva
            reserva.procesar()
        # El estado sigue siendo CONFIRMADA porque el bloque else no se ejecutó
        self.assertEqual(reserva.estado, fj.Reserva.CONFIRMADA)
        # El costo no se calculó
        self.assertIsNone(reserva.costo_total)
        # El bloque finally dejó su registro en el log
        self.assertIn(f"Reserva #{reserva.id}: fin del intento de procesamiento (estado: CONFIRMADA)", leer_log())

    # No se puede confirmar una reserva sobre un servicio no disponible
    def test_confirmar_servicio_no_disponible(self):
        # Se crea la reserva sobre la sala cerrada
        reserva = self.sistema.crear_reserva("52123456", "Sala Cerrada", 2)
        # Se espera el error específico de servicio no disponible
        with self.assertRaises(fj.ServicioNoDisponibleError):
            # Se intenta confirmar la reserva
            reserva.confirmar()
        # La reserva sigue pendiente
        self.assertEqual(reserva.estado, fj.Reserva.PENDIENTE)

    # Solo se pueden cancelar reservas que no estén procesadas ni canceladas
    def test_reglas_de_cancelacion(self):
        # Reserva pendiente: se puede cancelar
        pendiente = self.sistema.crear_reserva("52123456", "Sala Norte", 1)
        # Se cancela la reserva pendiente
        pendiente.cancelar()
        # Queda en estado CANCELADA
        self.assertEqual(pendiente.estado, fj.Reserva.CANCELADA)
        # Cancelarla otra vez no está permitido
        with self.assertRaises(fj.ErrorReserva):
            # Segundo intento de cancelación
            pendiente.cancelar()
        # Reserva procesada: tampoco se puede cancelar
        procesada = self.sistema.crear_reserva("52123456", "Sala Norte", 1)
        # Se confirma la reserva
        procesada.confirmar()
        # Se procesa la reserva
        procesada.procesar()
        # La cancelación de una reserva procesada produce ErrorReserva
        with self.assertRaises(fj.ErrorReserva):
            # Intento de cancelar la reserva procesada
            procesada.cancelar()

    # Una reserva con un cliente inexistente no se crea y no queda en la lista
    def test_reserva_con_cliente_inexistente(self):
        # Se espera el error de cliente
        with self.assertRaises(fj.ErrorCliente):
            # Documento que no está registrado
            self.sistema.crear_reserva("00000000", "Sala Norte", 2)
        # La lista de reservas sigue vacía
        self.assertEqual(self.sistema.listar_reservas(), [])


# Pruebas del archivo de logs y de la estabilidad del sistema
class TestLogsYEstabilidad(PruebaConSistema):

    # Los errores de negocio quedan registrados en el archivo de logs
    def test_errores_se_registran_en_el_log(self):
        # Se provoca un error al buscar un servicio inexistente
        with self.assertRaises(fj.ErrorServicio):
            # Servicio que no existe en el catálogo
            self.sistema.crear_reserva("52123456", "Sala Inexistente", 2)
        # El mensaje de error aparece en el log con nivel ERROR
        self.assertRegex(leer_log(), r"ERROR\s+\| Creación de reserva fallida: No existe un servicio con el nombre 'Sala Inexistente'")

    # ejecutar_simulacion() nunca deja escapar un error: el sistema sigue funcionando
    def test_ejecutar_simulacion_no_detiene_el_sistema(self):
        # Se guardan los contadores antes de las simulaciones de prueba
        antes = dict(fj.resultados)
        # Función que lanza un error propio del sistema
        def error_controlado():
            # Error de validación simulado
            raise fj.ErrorValidacion("dato inválido de prueba")
        # Función que lanza un error inesperado de Python
        def error_inesperado():
            # División por cero simulada
            return 1 / 0
        # La salida en pantalla de las simulaciones se descarta
        with contextlib.redirect_stdout(io.StringIO()):
            # Ninguna de estas llamadas debe lanzar una excepción
            fj.ejecutar_simulacion(901, "Prueba de error controlado", error_controlado)
            # El error inesperado también se captura
            fj.ejecutar_simulacion(902, "Prueba de error inesperado", error_inesperado)
            # Una operación exitosa después de los errores demuestra que el sistema sigue activo
            fj.ejecutar_simulacion(903, "Prueba de operación exitosa", lambda: "ok")
        # Se contó un error controlado
        self.assertEqual(fj.resultados["controladas"], antes["controladas"] + 1)
        # Se contó un error inesperado
        self.assertEqual(fj.resultados["inesperadas"], antes["inesperadas"] + 1)
        # Se contó una operación exitosa
        self.assertEqual(fj.resultados["exitosas"], antes["exitosas"] + 1)
        # El error inesperado quedó en el log con su traza completa (logger.exception)
        self.assertIn("ZeroDivisionError", leer_log())

    # Las 16 simulaciones del módulo terminan sin errores inesperados
    def test_simulaciones_del_modulo(self):
        # Se lee el log generado al importar el módulo
        log = leer_log()
        # La línea de cierre de la ejecución reporta 0 errores inesperados
        self.assertIn("5 exitosas, 11 errores controlados, 0 inesperados", log)


# Permite ejecutar el archivo directamente con: python test_software_fj.py
if __name__ == "__main__":
    # Se ejecutan todas las pruebas mostrando el nombre de cada una
    unittest.main(verbosity=2)
