from django.urls import reverse, resolve
from .forms import codigoDHL
from .views import validacion_dhl, validacion_codigo
from .models import Paquete
from django.test import TestCase,TransactionTestCase
from django.contrib.auth.models import User
from cuentas.models import IFCUsuario,Rol,Permiso,PermisoRol
from .models import AnalisisCotizacion,Cotizacion,AnalisisMuestra,Muestra,Analisis,OrdenInterna,Pais
from django.http import HttpResponse
from cuentas.models import Empresa
from ventas.models import Factura
from django.test.client import Client
from .views import ordenes_internas
import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName,FileType, Disposition, ContentId)
import time

# Create your tests here.
class DHLTests(TestCase):
    def test_modelo_paquete(self):
        #Model testing Paquetes
        Paquete.objects.create(
            id_paquete = 1,
            codigo_dhl = "1234567891"
        )
        self.assertTrue(Paquete.objects.filter(id_paquete=1))

#Form testing
    def test_form_dhl_valido(self):
        form_data = {'codigo_dhl': '1234567891'}
        form = codigoDHL(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_dhl_invalido(self):
        form_data = {'codigo_dhl': '123456789111'}
        form = codigoDHL(data=form_data)
        self.assertFalse(form.is_valid())

# View testing
    def test_view_dhl_error_numerico(self):
        codigo = "8426939232"
        view = validacion_dhl(codigo)
        self.assertTrue(view != 200)

    def test_view_dhl_caracteres(self):
        codigo = "shhsdheas"
        view = validacion_dhl(codigo)
        self.assertTrue(view != 200)

    def test_form_dhl_error_alfanumerico(self):
        codigo = "shh3d1e2s"
        view = validacion_dhl(codigo)
        self.assertTrue(view != 200)

    def test_form_dhl_correcto(self):
        codigo = "8426939231"
        view = validacion_dhl(codigo)
        self.assertTrue(view == 200)

    def test_url_resolved_validacion_codigo(self):
        #URL testing.
        url = reverse('validacion_codigo')
        self.assertEquals(resolve(url).func,validacion_codigo)

    def test_paquete_rastreo(self):
        #Crear un paquete y revisar su código de rastreo.
        paquete = Paquete.objects.create(
        id_paquete = 2,
        codigo_dhl = "8426939231"
        )
        codigo = paquete.codigo_dhl
        view = validacion_dhl(str(codigo))
        self.assertTrue(view == 200)


# Create your tests here.
class IngresoClienteTests(TestCase):   #Casos de prueba para la vista de ingreso_cliente
    def create_role_client(self):   #Crear rol en base de datos de tests
        permiso = Permiso()
        permiso.nombre = 'ingresar_muestra'
        permiso.save()
        role = Rol()
        role.nombre = "Cliente"
        role.save()
        permiso_rol = PermisoRol()
        permiso_rol.permiso = permiso
        permiso_rol.rol = role
        permiso_rol.save()
        return role

    def create_user_django(self):   #Crear usuario en tabla usuario de Django
        user = User.objects.create_user('hockey','hockey@lalocura.com','lalocura')
        user.save()
        return user

    def create_IFCUsuario(self):   #Crear usuario de IFC
        i_user = IFCUsuario()
        i_user.user = self.create_user_django()   #Asignar usuario de la tabla User
        i_user.rol = self.create_role_client()   #Asignar rol creado
        i_user.nombre = "Hockey"
        i_user.apellido_paterno = "Lalo"
        i_user.apellido_materno = "Cura"
        i_user.telefono = "9114364"
        i_user.estado = True
        i_user.save()   #Guardar usuario de IFC

    def login_IFC(self,mail,password):
        response = self.client.post(reverse('backend_login'),{'mail':mail,'password':password})

    def test_no_login(self):   #Prueba si el usuario no ha iniciado sesión
        self.create_role_client()   #Llamar función para crear rol
        response = self.client.get(reverse('ingreso_cliente'))   #Ir a página de ingreso de cliente
        self.assertEqual(response.status_code,302)   #La página debe de redireccionar porque no existe sesión

    def test_login(self):   #Pruena si el usuario ya inició sesión
        self.create_IFCUsuario()   #Llamar la función para crear usuario de IFC
        #self.client.login(username='hockey',password='lalocura')   #Hacer inicio de sesión
        self.login_IFC('hockey@lalocura.com','lalocura')
        response = self.client.get(reverse('ingreso_cliente'))
        self.assertEqual(response.status_code,200)   #Todo debe de salir correctamente

class IngresoMuestrasTests(TestCase):   #Casos de prueba para la vista de ingresar_muestras
    def create_role_client(self):   #Crear rol en base de datos de tests
        role = Rol()
        role.nombre = "Cliente"
        role.save()
        permiso = Permiso()
        permiso.nombre = 'ingresar_muestra'
        permiso.save()
        permiso_rol = PermisoRol()
        permiso_rol.permiso = permiso
        permiso_rol.rol = role
        permiso_rol.save()
        return role

    def create_user_django(self):   #Crear usuario en tabla usuario de Django
        user = User.objects.create_user('hockey','hockey@lalocura.com','lalocura')
        user.save()
        return user

    def create_IFCUsuario(self):   #Crear usuario de IFC
        i_user = IFCUsuario()
        i_user.user = self.create_user_django()   #Asignar usuario de la tabla User
        i_user.rol = self.create_role_client()   #Asignar rol creado
        i_user.nombre = "Hockey"
        i_user.apellido_paterno = "Lalo"
        i_user.apellido_materno = "Cura"
        i_user.telefono = "9114364"
        i_user.estado = True
        i_user.save() #Guardar usuario de IFC

    def login_IFC(self,mail,password):
        response = self.client.post(reverse('backend_login'),{'mail':mail,'password':password})

    def test_no_login(self):   #Prueba si el usuario no ha iniciado sesión
        self.create_role_client()
        response = self.client.get(reverse('ingreso_cliente'))
        self.assertEqual(response.status_code,302)

    def test_login(self):   #Prueba cuando el usuario ha iniciado sesión
        self.create_IFCUsuario()
        #self.client.login(username='hockey',password='lalocura')
        self.login_IFC('hockey@lalocura.com','lalocura')
        response = self.client.get(reverse('ingreso_cliente'))
        self.assertEqual(response.status_code,200)

    def test_post_complete(self):   #Prueba si el post es correcto
        self.create_IFCUsuario()
        #self.client.login(username='hockey',password='lalocura')
        self.login_IFC('hockey@lalocura.com', 'lalocura')
        response = self.client.post(reverse('ingreso_cliente'), {'nombre': "Impulse",   #Las variables del post están completas y con valores
                                                                   'direccion': "impulsadin",
                                                                   'pais': "Antigua y Barbuda",
                                                                   'idioma': "Inglés",
                                                                   'estado1': "Saint John's"
                                                                   })
        self.assertEqual(response.status_code,200)   #Todo correcto

class MuestraEnviarTests(TestCase):   #Casos de prueba para la vista de enviar_muestra
    def create_role_client(self):   #Crear rol en base de datos de tests
        role = Rol()
        role.nombre = "Cliente"
        role.save()
        return role

    def create_user_support(self):   #Crear rol en base de datos de tests
        role = Rol()
        role.nombre = "Soporte"
        role.save()
        user = User.objects.create_user('soporte','soporte@lalocura.com','lalocura')
        ifc_usuario = IFCUsuario.objects.create(user=user, rol=role, nombre='Juanito', apellido_paterno='Lemus', apellido_materno='Guevara', telefono="1234567890", estado=True)
        ifc_usuario.save()
        return ifc_usuario

    def create_user_django(self):   #Crear usuario en tabla usuario de Django
        user = User.objects.create_user('hockey','hockey@lalocura.com','lalocura')
        user.save()
        return user

    def create_IFCUsuario(self):   #Crear usuario de IFC
        i_user = IFCUsuario()
        i_user.user = self.create_user_django()   #Asignar usuario de la tabla User
        i_user.rol = self.create_role_client()   #Asignar rol creado
        i_user.nombre = "Hockey"
        i_user.apellido_paterno = "Lalo"
        i_user.apellido_materno = "Cura"
        i_user.telefono = "9114364"
        i_user.estado = True
        i_user.save()   #Guardar usuario de IFC

    def create_phantom(self):   #Función para crear al usuario fantasma quien creará las ordenes internas
        user = User.objects.create_user('danny_phantom', 'danny@phantom.com', 'phantom')
        user.save()   #Guardar objeto de usuario
        user_phantom = IFCUsuario()
        user_phantom.user = user
        user_phantom.rol = self.create_role_client()
        user_phantom.nombre = "Danny"
        user_phantom.apellido_paterno = "Phantom"
        user_phantom.apellido_materno = "Phantom"
        user_phantom.telefono = "9114364"
        user_phantom.estado = True
        user_phantom.save()   #Guardar usuario de IFC


    def setup(self):   #Función de setUp que crea lo necesario en la base de datos de pruebas para funcionar correctamente
        u1 = IFCUsuario.objects.all().first()
        self.create_phantom()
        u2 = IFCUsuario.objects.all().last()
        c = Cotizacion()   #Crear un objeto de Cotizacion
        c.usuario_c = u1
        c.usuario_v = u2
        c.subtotal = 10000.00
        c.envio = 100.00
        c.total = 1234235.00
        c.status = True
        c.save()   #Guardar la cotización
        pais = Pais() # Crear un pais para los analisis
        pais.nombre = "México"
        pais.save()
        a1 = Analisis()   #Crear un objeto de Analisis
        a1.codigo = "A1"
        a1.nombre = "Pest"
        a1.descripcion = "agropecuario"
        a1.precio = 213132423.12
        a1.unidad_min = "500 gr"
        a1.tiempo = "1 - 2 días"
        a1.pais = pais
        a1.save()   #Guardar el análisis
        a2 = Analisis()   #Crear un objeto de Analisis
        a2.codigo = "A2"
        a2.nombre = "icida"
        a2.descripcion = "agro"
        a2.precio = 2132423.12
        a2.unidad_min = "1 kg."
        a2.tiempo = "3 - 5 días"
        a2.pais = pais
        a2.save()   #Guardar el análisis
        ac1 = AnalisisCotizacion()   #Conectar el análisis con la cotización
        ac1.analisis = a1
        ac1.cotizacion = c
        ac1.cantidad = 10000
        ac1.restante = 10000
        ac1.fecha = datetime.datetime.now().date()
        ac1.save()   #Guardar conexión
        ac2 = AnalisisCotizacion()   #Conectar el análisis con la cotización
        ac2.analisis = a2
        ac2.cotizacion = c
        ac2.cantidad = 100
        ac2.restante = 100
        ac2.fecha = datetime.datetime.now().date()
        ac2.save()   #Guardar conexión
        otro = Analisis()   #Crear un objeto de Analisis
        otro.codigo = "Otro"
        otro.nombre = "Otro"
        otro.descripcion = "Otro"
        otro.precio = 0.00
        otro.unidad_min = "10 gr."
        otro.tiempo = "10 - 12 días"
        otro.pais = pais
        otro.save()   #Guardar el análisis

    def test_no_login(self):   #Prueba si el usuario no ha iniciado sesión
        self.create_role_client()
        response = self.client.get(reverse('registrar_ingreso_muestra'))
        self.assertEqual(response.status_code,302)

    def test_no_post(self):   #Prueba si no existe metodo post
        self.create_IFCUsuario()
        self.client.login(username='hockey',password='lalocura')
        response = self.client.get(reverse('registrar_ingreso_muestra'))
        self.assertEqual(response.status_code,404)

    def test_post_empty(self):    #Prueba si no se manda nada en el post
        self.create_IFCUsuario()
        self.client.login(username='hockey',password='lalocura')
        response = self.client.post(reverse('registrar_ingreso_muestra'),{})
        self.assertEqual(response.status_code,500)

    def test_post_incomplete(self):   #Prueba si el post no lleva todo lo que necesita en info generak
        self.create_IFCUsuario()
        self.client.login(username='hockey',password='lalocura')
        #insertar matrices de muestras, sólo la agrícola tiene una
        matrixAG = ['p', 'v', 'po', 'cm', 'p', 'ct', 'a', 'd', 'p', 'um', '11/01/2019', 'Sí', 'm', '1', '1', '-1', '-1', '-1', '-1', '-1']
        matrixPR = ['', '', '', '', '', '', '', '', '']
        matrixMB = ['', '', '', '', '', '', '', '', '', '', '']
        response = self.client.post(
            reverse('registrar_ingreso_muestra'),
            {
                'nombre': "Impulse",
                'direccion': "Impulsadin",
                'pais': "Antigua y Barbuda",
                'estado': "Saint John's",
                'matrixAG[]': matrixAG,
                'matrixPR[]': matrixPR,
                'matrixMB[]': matrixMB,
            })
        self.assertEqual(response.status_code,500)

    def test_post_incorrect(self):   #Prueba si el post no lleva todo lo que necesita en info generak
        self.create_IFCUsuario()
        self.client.login(username='hockey',password='lalocura')
        #la matriz agricola no tiene fecha
        matrixAG = ['p', 'v', 'po', 'cm', 'p', 'ct', 'a', 'd', 'p', 'um', '', 'Sí', 'm', '1', '1', '-1', '-1', '-1', '-1', '-1']
        matrixPR = ['', '', '', '', '', '', '', '', '']
        matrixMB = ['', '', '', '', '', '', '', '', '', '', '']
        response = self.client.post(
            reverse('registrar_ingreso_muestra'),
            {
                'nombre': "Impulse",
                'direccion': "Impulsadin",
                'pais': "Antigua y Barbuda",
                'estado': "Saint John's",
                'matrixAG[]': matrixAG,
                'matrixPR[]': matrixPR,
                'matrixMB[]': matrixMB,
            })
        self.assertEqual(response.status_code,500)
        #un dato en la matriz agrícola es obligatorio, pero se manda en blanco
        matrixAG = ['p', 'v', '', 'cm', 'p', 'ct', 'a', 'd', 'p', 'um', '11/01/2019', 'Sí', 'm', '1', '1', '-1', '-1', '-1', '-1', '-1']
        response = self.client.post(
            reverse('registrar_ingreso_muestra'),
            {
                'nombre': "Impulse",
                'direccion': "Impulsadin",
                'pais': "Antigua y Barbuda",
                'estado': "Saint John's",
                'matrixAG[]': matrixAG,
                'matrixPR[]': matrixPR,
                'matrixMB[]': matrixMB,
            })
        self.assertEqual(response.status_code,500)

    def test_select_single_analysis_correct(self): #probar que se ha enviado la información correcta para registrar una muestra para un solo análisis
        self.create_IFCUsuario()
        self.setup()
        self.client.login(username='hockey', password='lalocura')
        number_analysis = AnalisisCotizacion.objects.all().first().cantidad #obtener la cantidad de análisis disponibles
        analysis_id = Analisis.objects.all().first().id_analisis #obtener el id de un análisis
        #insertar matrices de muestras, sólo la agrícola tiene una
        matrixAG = ['p', 'v', 'po', 'cm', 'p', 'ct', 'a', 'd', 'p', 'um', '11/01/2019', 'Sí', 'm', 'pd', analysis_id, '-1', '-1', '-1', '-1', '-1']
        matrixPR = ['', '', '', '', '', '', '', '', '']
        matrixMB = ['', '', '', '', '', '', '', '', '', '', '']
        response = self.client.post(
            reverse('registrar_ingreso_muestra'),
            {
                'nombre': "Impulse",
                'direccion': "Impulsadin",
                'pais': "Antigua y Barbuda",
                'estado': "Saint John's",
                'idioma': "Inglés",
                'matrixAG[]': matrixAG,
                'matrixPR[]': matrixPR,
                'matrixMB[]': matrixMB,
            })
        self.assertEqual(response.status_code, 200) #El ingreso se ha hecho correctamente
        all_analysis_samples = AnalisisMuestra.objects.all()
        self.assertEqual(all_analysis_samples.count(),1) #verificar que hay un registro en la tabla análisis muestra
        self.assertEqual(all_analysis_samples.first().estado,True) #verificar que la muestra está activa
        all_internal_orders = OrdenInterna.objects.all()
        self.assertEqual(all_internal_orders.count(),1) #verificar que hay un registro en la tabla orden interna
        self.assertEqual(all_internal_orders.first().estatus,'No recibido') #verificar que el estado de la orden interna sea el correcto
        ac = AnalisisCotizacion.objects.get(analisis = Analisis.objects.get(id_analisis = analysis_id))#Obtener el analisis que se registró
        self.assertEqual(ac.restante,number_analysis-1) #verificar que se disminuyó la cantidad de análisis disponibles
        all_samples = Muestra.objects.all()
        self.assertEqual(all_samples.count(),1) #verificar que hay un registro en la tabla muestras

    def test_three_samples(self): #tres muestras ingresadas correctamente
        self.create_IFCUsuario()
        self.setup()
        self.client.login(username='hockey', password='lalocura')
        analysis_id = Analisis.objects.all().first().id_analisis #obtener el id de un análisis
        #insertar matrices de muestras, sólo la agrícola tiene una
        matrixAG = ['p', 'v', 'po', 'cm', 'p', 'ct', 'a', 'd', 'p', 'um', '11/01/2019', 'Sí', 'm', 'pd', analysis_id, analysis_id, analysis_id, '-1', '-1', '-1'] #Muestra correcta
        matrixPR = ['tm,tm', 'dm,dm', '11/30/2019,11/30/2019', str(analysis_id)+','+str(analysis_id), '-1,-1', '-1,-1', '-1,-1', '-1,-1', '-1,-1'] #Dos muestras del tipo PR
        matrixMB = ['', '', '', '', '', '', '', '', '', '', '']
        response = self.client.post(
            reverse('registrar_ingreso_muestra'),
            {
                'nombre': "Impulse",
                'direccion': "Impulsadin",
                'pais': "Antigua y Barbuda",
                'estado': "Saint John's",
                'idioma': "Inglés",
                'matrixAG[]': matrixAG,
                'matrixPR[]': matrixPR,
                'matrixMB[]': matrixMB,
            })
        self.assertEqual(response.status_code, 200) #El ingreso se ha hecho correctamente
        all_analysis_samples = AnalisisMuestra.objects.all()
        self.assertEqual(all_analysis_samples.count(),5) #verificar que hay cinco registros en la tabla análisis muestra
        self.assertEqual(all_analysis_samples.first().estado,True) #verificar que la muestra está activa
        all_internal_orders = OrdenInterna.objects.all()
        self.assertEqual(all_internal_orders.count(),1) #verificar que hay un registro en la tabla orden interna
        self.assertEqual(all_internal_orders.first().estatus,'No recibido') #verificar que el estado de la orden interna sea el correcto
        ac = AnalisisCotizacion.objects.get(analisis = Analisis.objects.get(id_analisis = analysis_id))#Obtener el analisis que se registró
        number_analysis = AnalisisCotizacion.objects.first().cantidad #Buscar la cantidad de análisis que se cotizaron originalmente
        self.assertEqual(ac.restante,number_analysis-5) #verificar que se disminuyó la cantidad de análisis disponibles
        all_samples = Muestra.objects.all()
        self.assertEqual(all_samples.count(),3) #verificar que hay tres registro en la tabla muestras

    def test_incorrect_data(self): #si hubo datos inválidos que pasaron la validación en front, el controlador debe impedir que se guarde cualquier cosa
        self.create_IFCUsuario()
        self.setup()
        self.client.login(username='hockey', password='lalocura')
        analysis_id = Analisis.objects.all().first().id_analisis #obtener el id de un análisis
        #insertar matrices de muestras, sólo la agrícola tiene una
        matrixAG = ['p', 'v', 'po', 'cm', 'p', 'ct', 'a', 'd', 'p', 'um', '11/01/2019', 'Sí', 'm', 'pd', analysis_id, '-1', '-1', '-1', '-1', '-1'] #Muestra correcta
        matrixPR = ['tm', 'dm', 'fecha_incorrecta', analysis_id, '-1', '-1', '-1', '-1', '-1'] #Muestra con datos incorrectos
        matrixMB = ['', '', '', '', '', '', '', '', '', '', '']
        response = self.client.post(
            reverse('registrar_ingreso_muestra'),
            {
                'nombre': "Impulse",
                'direccion': "Impulsadin",
                'pais': "Antigua y Barbuda",
                'estado': "Saint John's",
                'idioma': "Inglés",
                'matrixAG[]': matrixAG,
                'matrixPR[]': matrixPR,
                'matrixMB[]': matrixMB,
            })
        self.assertEqual(response.status_code, 500) #El ingreso detectó un error
        all_analysis_samples = AnalisisMuestra.objects.all()
        self.assertEqual(all_analysis_samples.count(),0) #La orden interna se borró, los objetos derivados de ella se borraron
        all_internal_orders = OrdenInterna.objects.all()
        self.assertEqual(all_internal_orders.count(),0) #La orden interna se borró, los objetos derivados de ella se borraron
        all_samples = Muestra.objects.all()
        self.assertEqual(all_samples.count(),0) #La orden interna se borró, los objetos derivados de ella se borraron

#Casos de prueba para view una orden interna
class OrdenesInternasViewTests(TestCase):
    def setup(self): #registrar la información necesaria para ejecutar los test
        permiso = Permiso()
        permiso.nombre = 'visualizar_orden_interna'
        permiso.save()
        role = Rol()
        role.nombre = "Soporte"
        role.save()
        role2 = Rol()
        role2.nombre = "Cliente"
        role2.save()
        #crear usuario de Django
        user = User.objects.create_user('hockey', 'hockey@lalocura.com', 'lalocura')
        user.save()  #guardar usuario de Django
        user2 = User.objects.create_user('padrino', 'padrino@lalocura.com', 'padrino')
        user2.save()
        #i_user : user de IFC
        i_user = IFCUsuario()  #Crear un usuario de IFC
        i_user.user = user   #Asignar usuario de la tabla User
        i_user.rol = role   #Asignar rol creado
        i_user.nombre = "Hockey"
        i_user.apellido_paterno = "Lalo"
        i_user.apellido_materno = "Cura"
        i_user.telefono = "9114364"
        i_user.estado = True
        i_user.save()   #Guardar usuario de IFC
        i_user2 = IFCUsuario()
        i_user2.user = user2   #Asignar usuario de la tabla User
        i_user2.rol = role2   #Asignar rol creado
        i_user2.nombre = "Padrino"
        i_user2.apellido_paterno = "Lalo"
        i_user2.apellido_materno = "Cura"
        i_user2.telefono = "9114454364"
        i_user2.estado = True
        i_user2.save()   #Guardar usuario de IFC
        permiso_rol = PermisoRol()
        permiso_rol.permiso = permiso
        permiso_rol.rol = role
        permiso_rol.save()

    def login_IFC(self,mail,password):
        response = self.client.post(reverse('backend_login'),{'mail':mail,'password':password})

    #probar que el usuario no pueda ingresar a la página si no ha iniciado sesión
    def test_no_login_form(self):
        self.setup()
        response = self.client.get(reverse('ordenes_internas'))
        self.assertEqual(response.status_code, 302)

    #probar que el usario no pueda ingresar a la página si no tiene el rol adecuado
    def test_no_login_different_role(self):
        self.setup()
        #ingresar como un usuario cliente
        #self.client.login(username='padrino', password='padrino')
        self.login_IFC('padrino@lalocura.com', 'padrino')
        response = self.client.get(reverse('ordenes_internas'))
        self.assertEqual(response.status_code, 404)

    #probar que el usario puede ingresar a la página si tiene el rol adecuado
    def test_login_correcto(self):
        self.setup()
        #ingresar como un usuario soporte
        #self.client.login(username='hockey', password='lalocura')
        self.login_IFC('hockey@lalocura.com','lalocura')
        response = self.client.get(reverse('ordenes_internas'))
        self.assertEqual(response.status_code, 200)

#Casos de prueba para view de consultar una orden interna
class ConsultarOrdenesInternasViewTests(TestCase):
    def setup(self):  #registrar la información necesaria para ejecutar los test
        role = Rol()
        role.nombre = "Soporte"
        role.save()
        role2 = Rol()
        role2.nombre = "Cliente"
        role2.save()
        #crear usuario de Django
        user = User.objects.create_user('hockey', 'hockey@lalocura.com', 'lalocura')
        user.save() #guardar usuario de Django
        user2 = User.objects.create_user('padrino', 'padrino@lalocura.com', 'padrino')
        user2.save()
        #i_user : user de IFC
        i_user = IFCUsuario()  #Crear un usuario de IFC
        i_user.user = user   #Asignar usuario de la tabla User
        i_user.rol = role   #Asignar rol creado
        i_user.nombre = "Hockey"
        i_user.apellido_paterno = "Lalo"
        i_user.apellido_materno = "Cura"
        i_user.telefono = "9114364"
        i_user.estado = True
        i_user.save()   #Guardar usuario de IFC
        i_user2 = IFCUsuario()
        i_user2.user = user2   #Asignar usuario de la tabla User
        i_user2.rol = role2   #Asignar rol creado
        i_user2.nombre = "Padrino"
        i_user2.apellido_paterno = "Lalo"
        i_user2.apellido_materno = "Cura"
        i_user2.telefono = "9114454364"
        i_user2.estado = True
        i_user2.save()   #Guardar usuario de IFC

    def login_IFC(self,mail,password):
        response = self.client.post(reverse('backend_login'),{'mail':mail,'password':password})

    #probar que el usuario no pueda ingresar a la página si no ha iniciado sesión
    def test_no_login_form(self):
        self.setup()
        response = self.client.get(reverse('consultar_orden'))
        self.assertEqual(response.status_code, 302)

    #probar que el usario no pueda ingresar a la página si no tiene el rol adecuado
    def test_no_login_different_role(self):
        self.setup()
        #ingresar como un usuario cliente
        self.login_IFC('padrino@lalocura.com', 'padrino')
        response = self.client.get(reverse('consultar_orden'))
        self.assertEqual(response.status_code, 404)

    #probar que el usario no puede ingresar a la página sin enviar POST
    def test_no_post(self):
        self.setup()
        #ingresar como un usuario soporte
        self.login_IFC('hockey@lalocura.com', 'lalocura')
        response = self.client.get(reverse('consultar_orden'))
        self.assertEqual(response.status_code, 404)

    def test_post_empty(self):   #Prueba si no se manda nada en el post
        self.setup()
        self.login_IFC('hockey@lalocura.com', 'lalocura')
        response = self.client.post(reverse('consultar_orden'),{})   #El post va vacío
        self.assertEqual(response.status_code, 404)   #Mostrar 404



    def create_role_client(self):   #Crear rol en base de datos de tests
        role = Rol()
        role.nombre = "Cliente"
        role.save()
        return role

    def create_role_soporte(self):   #Crear rol en base de datos de tests
        role = Rol()
        role.nombre = "Soporte"
        role.save()
        return role


    def create_user_django(self):   #Crear usuario en tabla usuario de Django
        user = User.objects.create_user('hockey','hockey@lalocura.com','lalocura')
        user.save()
        return user

    def create_IFCUsuario(self):   #Crear usuario de IFC
        #i_user : user de IFC
        i_user = IFCUsuario()
        i_user.user = self.create_user_django()   #Asignar usuario de la tabla User
        i_user.rol = self.create_role_client()   #Asignar rol creado
        i_user.nombre = "Hockey"
        i_user.apellido_paterno = "Lalo"
        i_user.apellido_materno = "Cura"
        i_user.telefono = "9114364"
        i_user.estado = True
        i_user.save()   #Guardar usuario de IFC

    #Función para crear al usuario fantasma quien creará las ordenes internas
    def create_phantom(self):
        emp = Empresa(empresa="Phantom Inc.")
        emp.save()
        user = User.objects.create_user(
            'danny_phantom',
            'danny@phantom.com',
            'phantom'
        )
        user.save()   #Guardar objeto de usuario
        #user_phantom : usuario con nombre danny_phantom
        user_phantom = IFCUsuario()
        user_phantom.user = user
        user_phantom.rol = self.create_role_client()
        user_phantom.nombre = "Danny"
        user_phantom.apellido_paterno = "Phantom"
        user_phantom.apellido_materno = "Phantom"
        user_phantom.telefono = "9114364"
        user_phantom.estado = True
        user_phantom.empresa = emp
        user_phantom.save()   #Guardar usuario de IFC

    #Función para crear al usuario fantasma quien creará las ordenes internas
    def create_soporte(self):
        user = User.objects.create_user('soporte', 'soporte@phantom.com', 'soporte')
        user.save()   #Guardar objeto de usuario
        user_soporte = IFCUsuario()
        user_soporte.user = user
        user_soporte.rol = self.create_role_soporte()
        user_soporte.nombre = "soporte"
        user_soporte.apellido_paterno = "soporte"
        user_soporte.apellido_materno = "soporte"
        user_soporte.telefono = "9114364"
        user_soporte.estado = True
        empresa = Empresa()
        empresa.empresa = "KFC"
        empresa.save()
        user_soporte.empresa = empresa
        user_soporte.save()   #Guardar usuario de IFC

    #Función setUp que crea lo necesario en la BD de pruebas para funcionar bien
    def setup2(self):
        user1 = IFCUsuario.objects.all().first()
        self.create_phantom()
        user2 = IFCUsuario.objects.all().last()
        self.create_soporte()
        empresa = Empresa()
        empresa.empresa = "IFC"
        empresa.save()
        user1.empresa = empresa
        user1.save()
        coti = Cotizacion()   #Crear un objeto de Cotizacion
        coti.usuario_c = user1
        coti.usuario_v = user2
        coti.subtotal = 10000.00
        coti.envio = 100.00
        coti.total = 1234235.00
        coti.status = True
        coti.save()   #Guardar la cotización
        pais = Pais() # Crear un pais para los analisis
        pais.nombre = "México"
        pais.save()
        analisis1 = Analisis()   #Crear un objeto de Analisis
        analisis1.codigo = "A1"
        analisis1.nombre = "Pest"
        analisis1.descripcion = "agropecuario"
        analisis1.precio = 213132423.12
        analisis1.unidad_min = "500 gr"
        analisis1.tiempo = "1 - 2 días"
        analisis1.pais = pais
        analisis1.save()   #Guardar el análisis
        analisis2 = Analisis()   #Crear un objeto de Analisis
        analisis2.codigo = "A2"
        analisis2.nombre = "icida"
        analisis2.descripcion = "agro"
        analisis2.precio = 2132423.12
        analisis2.unidad_min = "1 kg."
        analisis2.tiempo = "3 - 5 días"
        analisis2.pais = pais
        analisis2.save()   #Guardar el análisis
        ana_coti1 = AnalisisCotizacion()   #Conectar el análisis con la cotización
        ana_coti1.analisis = analisis1
        ana_coti1.cotizacion = coti
        ana_coti1.cantidad = 10000
        ana_coti1.restante = 10000
        ana_coti1.fecha = datetime.datetime.now().date()
        ana_coti1.save()   #Guardar conexión
        ana_coti2 = AnalisisCotizacion()   #Conectar el análisis con la cotización
        ana_coti2.analisis = analisis2
        ana_coti2.cotizacion = coti
        ana_coti2.cantidad = 100
        ana_coti2.restante = 100
        ana_coti2.fecha = datetime.datetime.now().date()
        ana_coti2.save()   #Guardar conexión
        otro = Analisis()   #Crear un objeto de Analisis
        otro.codigo = "Otro"
        otro.nombre = "Otro"
        otro.descripcion = "Otro"
        otro.precio = 0.00
        otro.unidad_min = "10 gr."
        otro.tiempo = "10 - 12 días"
        otro.pais = pais
        otro.save()   #Guardar el análisis
        #obtener el id del primer análisis
        analysis_id = Analisis.objects.all().get(codigo="A1").id_analisis
        #obtener el id del segundo análisis
        analysis_id2 = Analisis.objects.all().get(codigo="A2").id_analisis
        self.login_IFC('hockey@lalocura.com', 'lalocura')
        factura = Factura()
        factura.save()
        #insertar matrices de muestras, sólo la agrícola tiene una
        matrixAG = ['p', 'v', 'po', 'cm', 'p', 'ct', 'a', 'd', 'p', 'um', '11/01/2019', 'Sí', 'm', '1', '1', '-1', '-1', '-1', '-1', '-1']
        matrixPR = ['', '', '', '', '', '', '', '']
        matrixMB = ['', '', '', '', '', '', '', '', '', '', '']
        #enviar la información para guardar para la primera muestra
        response = self.client.post(
            reverse('registrar_ingreso_muestra'),
            {
                'nombre': "Impulse",
                'direccion': "Impulsadin",
                'pais': "Antigua y Barbuda",
                'estado': "Saint John's",
                'idioma': "Español",
                'matrixAG[]': matrixAG,
                'matrixPR[]': matrixPR,
                'matrixMB[]': matrixMB,
            }
        )
        #enviar la información para guardar para la segunda muestra
        response = self.client.post(
            reverse('registrar_ingreso_muestra'),
            {
                'nombre': "Impulse",
                'direccion': "Impulsadin",
                'pais': "Italia",
                'estado': "Roma",
                'idioma': "Inglés",
                'matrixAG[]': matrixAG,
                'matrixPR[]': matrixPR,
                'matrixMB[]': matrixMB,
            }
        )
        muestra = Muestra.objects.all().first()
        muestra.factura = factura
        muestra.save()
        self.client.logout()

        permiso1 = Permiso()
        permiso1.nombre = 'visualizar_orden_interna'
        permiso1.save()

        permiso_rol1 = PermisoRol()
        permiso_rol1.permiso = permiso1
        permiso_rol1.rol = Rol.objects.get(nombre="Soporte")
        permiso_rol1.save()

    def test_id_incorrecto(self):   #Prueba si no se manda nada en el post
        self.create_IFCUsuario()
        self.setup2()
        self.login_IFC('hockey@lalocura.com', 'lalocura')
        #El post va vacío
        response = self.client.post(reverse('consultar_orden'),{'id': 3456})
        self.assertEqual(response.status_code, 404)   #Mostrar 404

    #Prueba si la oi tiene 2 muestras, una con factura y otra sin factura
    def test_dos_muestras(self):
        self.create_IFCUsuario()
        self.setup2()
        self.login_IFC('soporte@phantom.com', 'soporte')
        oi_id = OrdenInterna.objects.all().first().idOI
        #El post va vacío
        response = self.client.post(reverse('consultar_orden'),{'id': oi_id})
        orden = OrdenInterna.objects.get(idOI = oi_id)
        # Sacar la oi y las muestras para comparar con el response
        import json
        muestras = response.json()['muestras']
        f = response.json()['facturas']
        muestras_json = json.loads(muestras)
        num_muestras = 0
        #Checar cada muestra y comparar que corresponden con la oi y sus facturas
        for ind in muestras_json:
            muestra = Muestra.objects.get(id_muestra = ind['pk'])
            if muestra.factura:
                self.assertEqual(f[str(ind['pk'])] , muestra.factura.idFactura)
            self.assertEqual(ind['fields']['oi'] , oi_id)
            num_muestras+=1

        #Checar que el núm de muestras del response sea igual al de la oi asociada
        self.assertEqual(num_muestras, Muestra.objects.filter(oi = orden).count())
        self.assertEqual(response.status_code, 200)   #Mostrar 200



class TestEditaOrdenesInternas(TestCase):
    #Tests de cuentas de usuarios
    def set_up_Users(self):
        permiso = Permiso()
        permiso.nombre = 'actualizar_orden_interna'
        permiso.save()

        permiso2 = Permiso()
        permiso2.nombre = 'visualizar_orden_interna'
        permiso2.save()

        #Crea usuarios Clientes
        rol_soporte = Rol.objects.create(nombre='Soporte')
        rol_cliente = Rol.objects.create(nombre='Cliente')
        usuario_clientes = User.objects.create_user('soport', 'soporttest@testuser.com', 'testpassword')
        empresa =  Empresa.objects.create(empresa='TestInc')

        clientes1 = IFCUsuario.objects.create(rol =rol_soporte,
                                                user = usuario_clientes,
                                                nombre = 'soporte',
                                                apellido_paterno = 'test',
                                                apellido_materno ='test',
                                                telefono = '5234567',
                                                estado = True,
                                                empresa=empresa,
                                              )
        clientes1.save()

        usuario_clientes = User.objects.create_user('client', 'client@testuser.com', 'testpassword')
        clientes2 = IFCUsuario.objects.create(rol =rol_cliente,
                                                user = usuario_clientes,
                                                nombre = 'otro',
                                                apellido_paterno = 'test',
                                                apellido_materno ='test',
                                                telefono = '5234567',
                                                estado = True,
                                                empresa=empresa,
                                              )
        clientes2.save()

        #Crea usuario Director
        usuario_dir = User.objects.create_user('direc', 'test@testuser.com', 'testpassword')
        rol_dir = Rol.objects.create(nombre='Director')

        dir = IFCUsuario.objects.create(rol = rol_dir,
                                            user = usuario_dir,
                                            nombre = 'dir',
                                            apellido_paterno = 'test',
                                            apellido_materno = 'test',
                                            telefono = '3234567',
                                            estado = True,
                                            empresa=empresa,
                                          )
        dir.save()


        #Crea usuario Ventas
        usuario_ventas = User.objects.create_user('vent', 'venttest@testuser.com', 'testpassword')
        rol_ventas = Rol.objects.create(nombre='Ventas')

        ventas = IFCUsuario.objects.create(rol = rol_ventas,
                                                user = usuario_ventas,
                                                nombre = 'ventas',
                                                apellido_paterno = 'test',
                                                apellido_materno = 'test',
                                                telefono = '3234567',
                                                estado = True,
                                                empresa=empresa
                                              )
        ventas.save()

        #Crea usuario Facturacion
        user_facturacion = User.objects.create_user('fact', 'facttest@testuser.com', 'testpassword')
        rol_facturacion = Rol.objects.create(nombre='Facturacion')
        facturacion = IFCUsuario.objects.create(rol = rol_facturacion,
                                                    user = user_facturacion,
                                                    nombre ='facturacion',
                                                    apellido_paterno = 'test',
                                                    apellido_materno ='test',
                                                    telefono ='4234567',
                                                    estado =True,
                                                    empresa=empresa
                                                  )
        facturacion.save()

        #Crear orden interna para cliente
        oi = OrdenInterna.objects.create(usuario = clientes1,
                                            estatus = "No recibido",
                                            localidad = "mexico",
                                        )
        oi.save()
        permiso_rol = PermisoRol()
        permiso_rol.permiso = permiso
        permiso_rol.rol = rol_soporte
        permiso_rol.save()
        permiso_rol2 = PermisoRol()
        permiso_rol2.permiso = permiso2
        permiso_rol2.rol = rol_soporte
        permiso_rol2.save()

    def login_IFC(self,mail,password):
        response = self.client.post(reverse('backend_login'),{'mail':mail,'password':password})

    #Tests
    def test_acceso_denegado(self):
        #Test de acceso a url sin Log In
        response = self.client.get('/reportes/ordenes_internas')
        self.assertRedirects(response,
                                '/cuentas/login?next=/reportes/ordenes_internas',
                                status_code=302, target_status_code=301,
                                msg_prefix='',
                                fetch_redirect_response=True
                             )

    def test_acceso_denegado_rol(self):
        #Test de acceso a url con Log In como Cliente
        self.set_up_Users() #Set up de datos
        #self.client.login(username='client',password='testpassword')
        self.login_IFC('client@testuser.com','testpassword')
        response = self.client.get('/reportes/ordenes_internas')
        self.assertEqual(response.status_code,404)

    def test_acceso_permitido_total(self):
        #Test de acceso a url con Log In como Director para que vea a todos los usuarios
        self.set_up_Users() #Set up de datos
        #self.client.login(username='soport',password='testpassword')
        self.login_IFC('soporttest@testuser.com', 'testpassword')
        response = self.client.get('/reportes/ordenes_internas')
        self.assertEqual(response.status_code,200)

    def test_template(self):
        #Test de creacion de ordenes internas para cliente
        self.set_up_Users() #Set up de datos
        #self.client.login(username='soport',password='testpassword')
        self.login_IFC('soporttest@testuser.com', 'testpassword')
        orden = OrdenInterna.objects.filter(estatus="No recibido").first()
        dir = "/reportes/ordenes_internas"
        response = self.client.post(dir)
        self.assertContains(response, "No recibido")


    def test_model(self):
        #Test del model de Ordenes Internas
        self.set_up_Users() #Set up de datos
        user = IFCUsuario.objects.get(nombre= "soporte")
        orden = OrdenInterna.objects.create(  usuario = user,
                                            localidad = "loc1",
                                            fecha_envio = "2019-03-02",
                                            link_resultados = "www.lol.com",
                                        )

        self.assertEqual(orden.localidad,"loc1")

    def test_url_resuelta(self):
        #URL testing.
        url = reverse('ordenes_internas')
        self.assertEquals(resolve(url).func,ordenes_internas)


class EnviarResultados(TestCase):
    def setup(self):
        rol_soporte = Rol.objects.create(nombre='Soporte')
        rol_cliente = Rol.objects.create(nombre='Cliente')
        usuario_clientes = User.objects.create_user('soport', 'soporttest@testuser.com', 'testpassword')
        empresa =  Empresa.objects.create(empresa='TestInc')
        clientes1 = IFCUsuario.objects.create(
                                                        rol =rol_soporte,
                                                        user = usuario_clientes,
                                                        nombre = 'soporte',
                                                        apellido_paterno = 'test',
                                                        apellido_materno ='test',
                                                        telefono = '5234567',
                                                        estado = True,
                                                        empresa=empresa,
                                                      )
        clientes1.save()
        #Crea usuario Director
        usuario_dir = User.objects.create_user('direc', 'test@testuser.com', 'testpassword')
        rol_dir = Rol.objects.create(nombre='Director')

        dir = IFCUsuario.objects.create(rol = rol_dir,
                                            user = usuario_dir,
                                            nombre = 'dir',
                                            apellido_paterno = 'test',
                                            apellido_materno = 'test',
                                            telefono = '3234567',
                                            estado = True,
                                            empresa=empresa,
                                        )
        dir.save()

    def login_IFC(self,mail,password):
        response = self.client.post(reverse('backend_login'),{'mail':mail,'password':password})

    def test_no_login(self):
        response = self.client.get(reverse('enviar_archivo'))   #Ir al url de envío de resultados
        self.assertEqual(response.status_code,302)   #La página debe de redireccionar porque no existe sesión

    #probar que el usario no pueda ingresar a la página si no tiene el rol adecuado
    def test_no_login_different_role(self):
        self.setup()
        #ingresar como un usuario cliente
        self.client.login(username='soport', password='testpassword')
        response = self.client.get(reverse('enviar_archivo'))
        self.assertEqual(response.status_code, 404)

    def test_no_post(self):   #Prueba si no existe metodo post
        self.setup()
        self.client.login(username='direc',password='testpassword')
        response = self.client.get(reverse('enviar_archivo'))
        self.assertEqual(response.status_code,404)

    def test_post_empty(self):    #Prueba si no se manda nada en el post
        self.setup()
        self.login_IFC('test@testuser.com', 'testpassword')
        response = self.client.post(reverse('enviar_archivo'),{})
        self.assertEqual(response.status_code,404)

    def test_post_incomplete(self):   #Prueba si el post no lleva todo lo que necesita
        self.setup()
        self.login_IFC('test@testuser.com', 'testpassword')
        response = self.client.post(reverse('enviar_archivo'),{'email_destino':"A01207945@itesm.mx",
                                                                  'body':"Cuerpo del correo",
                                                                  })
        self.assertEqual(response.status_code,404)

    """
    def test_mail_correcto(self):
        message = Mail(
            from_email='A01207945@itesm.mx',
            to_emails='A0127373@itesm.mx',
            subject="Asunto",
            html_content="Contenido")
        with open('./API_KEY_recover_password.txt', 'rb') as f:
            key = f.read()
        key_decoded = key.decode('ascii')
        sendgrid_client = SendGridAPIClient(key_decoded)
        response = sendgrid_client.send(message)
        self.assertEqual(response.status_code,202)
    """
