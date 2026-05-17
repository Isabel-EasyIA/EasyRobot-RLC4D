# -*- coding: utf-8 -*-
import c4d
import time
import random
import socket
import struct
import math
from c4d import gui

# ID Único de Desarrollo para el plugin
PLUGIN_ID = 1054321 

# IDs de Elementos Estáticos de la Interfaz
GRP_CONFIG_CANTIDAD = 5000
NUM_CANT_SERVOS = 5001
NUM_CANT_SENSORES = 5002
NUM_CANT_DIST_SENSORS = 5005 
BTN_RELOAD_UI = 5003
BTN_AYUDA_VEL = 5004
GRP_MASTER_SCROLL = 6000
GRP_DYNAMIC_MAIN = 1000
GRP_SERVOS = 2000
GRP_SENSORES = 3000
GRP_DIST_SENSORS = 3500 

# IDs para el Entrenamiento Paralelo Estructurado
GRP_TRAINING = 7000
GRP_FILA_MAESTRO = 7001
LNK_ROBOT_MAESTRO = 7002
GRP_FILA_INSTANCIAS = 7003
NUM_INSTANCIAS = 7004
NUM_DISTANCIA_CM = 7005
GRP_STEPS_TIME = 7006
NUM_TRAINING_STEPS = 7007
NUM_CICLO_MS = 7008
GRP_OPCIONES_TRAIN = 7009
CHK_MODO_ESPECTADOR = 7010
CHK_MOSTRAR_CLONES = 7011

# IDs para la Red de Telemetría UDP
GRP_UDP_CONFIG = 9000
TXT_UDP_IP = 9001
NUM_UDP_PORT = 9002

# IDs para la Botonera Inferior
GRP_BOTONES_BASE = 8000
BTN_CONECTAR = 4000
BTN_START_TRAINING = 4001

# Sub-IDs para persistencia en el BaseContainer del Documento
ID_CANT_SERVOS_BC = 10
ID_CANT_SENSORES_BC = 11
ID_INSTANCIAS_BC = 12
ID_MODO_ESPECTADOR_BC = 13
ID_CICLO_MS_BC = 14
ID_DISTANCIA_CM_BC = 15
ID_MOSTRAR_CLONES_BC = 16
ID_UDP_IP_BC = 17
ID_UDP_PORT_BC = 18
ID_CANT_DIST_BC = 19 

# Offsets de Memoria indexados
OFFSET_SERVO_LINK = 10000
OFFSET_SERVO_VEL = 20000
OFFSET_SENSOR_LINK = 40000
OFFSET_ROBOT_MAESTRO_LINK = 50000
OFFSET_SERVO_MIN = 60000
OFFSET_SERVO_MAX = 70000
OFFSET_SENSOR_RUIDO_ACEL = 80000
OFFSET_SENSOR_RANGO_MAX_ACEL = 90000
OFFSET_DIST_LINK = 110000
OFFSET_DIST_MAX = 120000 
OFFSET_DIST_TARGET = 130000 

NOMBRE_CONTENEDOR_CLONES = "=== ENVT_CLONES_TEMPORALES ==="

class EasyRobotRLDlg(gui.GeDialog):
    def __init__(self):
        self.cant_servos = 10
        self.cant_sensores = 5
        self.cant_dist_sensores = 3 
        self.instancias = 4
        self.distancia_cm = 2000
        self.modo_espectador = False
        self.mostrar_clones = False
        self.ciclo_ms = 0
        self.udp_ip = "127.0.0.1"
        self.udp_port = 2026

    def CreateLayout(self):
        self.SetTitle("Easy Robot RL - Configuración Binaria Unificada")
        
        self.GroupBegin(GRP_CONFIG_CANTIDAD, c4d.BFH_SCALEFIT, cols=8) 
        self.GroupBorder(c4d.BORDER_THIN_IN)
        self.GroupBorderSpace(10, 10, 10, 5)
        
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Nº Servos Motores:", c4d.BORDER_NONE)
        self.AddEditNumberArrows(NUM_CANT_SERVOS, c4d.BFH_LEFT, 40, 0)
        
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Nº Sensores IMU:", c4d.BORDER_NONE)
        self.AddEditNumberArrows(NUM_CANT_SENSORES, c4d.BFH_LEFT, 40, 0)
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Nº Sensores de Distancias:", c4d.BORDER_NONE)
        self.AddEditNumberArrows(NUM_CANT_DIST_SENSORS, c4d.BFH_LEFT, 40, 0)
        
        self.AddButton(BTN_RELOAD_UI, c4d.BFH_RIGHT, 0, 0, "Actualizar Panel")
        self.AddButton(BTN_AYUDA_VEL, c4d.BFH_RIGHT, 50, 0, "Ayuda")
        self.GroupEnd()
        
        if self.ScrollGroupBegin(GRP_MASTER_SCROLL, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, scrollflags=c4d.SCROLLGROUP_VERT):
            self.GroupBegin(GRP_DYNAMIC_MAIN, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=1)
            self.DibujarListasDinamicas()
            self.GroupEnd()
            self.GroupEnd()
        
        self.GroupBegin(GRP_TRAINING, c4d.BFH_SCALEFIT, cols=1)
        self.GroupBorder(c4d.BORDER_THIN_IN)
        self.GroupBorderSpace(10, 10, 10, 10)
        
        self.GroupBegin(GRP_FILA_MAESTRO, c4d.BFH_SCALEFIT, cols=2)
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Proyecto Robot Maestro (Nulo):", c4d.BORDER_NONE)
        self.AddCustomGui(LNK_ROBOT_MAESTRO, c4d.CUSTOMGUI_LINKBOX, "", c4d.BFH_SCALEFIT, 150, 0)
        self.GroupEnd()
        
        self.GroupBegin(GRP_FILA_INSTANCIAS, c4d.BFH_SCALEFIT, cols=4)
        self.GroupSpace(5, 0)
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Instancias Simultáneas (Clones):", c4d.BORDER_NONE)
        self.AddEditNumberArrows(NUM_INSTANCIAS, c4d.BFH_LEFT, 60, 0)
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Distancia (cm):", c4d.BORDER_NONE)
        self.AddEditNumberArrows(NUM_DISTANCIA_CM, c4d.BFH_LEFT, 60, 0)
        self.GroupEnd()
        
        self.GroupBegin(GRP_STEPS_TIME, c4d.BFH_SCALEFIT, cols=4)
        self.GroupSpace(5, 0)
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Pasos de Simulación:", c4d.BORDER_NONE)
        self.AddEditNumberArrows(NUM_TRAINING_STEPS, c4d.BFH_LEFT, 60, 0)
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Ciclo (ms):", c4d.BORDER_NONE)
        self.AddEditNumberArrows(NUM_CICLO_MS, c4d.BFH_LEFT, 60, 0)
        self.GroupEnd() 
        
        self.GroupBegin(GRP_OPCIONES_TRAIN, c4d.BFH_SCALEFIT, cols=2)
        self.GroupSpace(10, 0)
        self.AddCheckbox(CHK_MODO_ESPECTADOR, c4d.BFH_LEFT, 0, 0, "Modo Espectador (Ver Simulación)")
        self.AddCheckbox(CHK_MOSTRAR_CLONES, c4d.BFH_LEFT, 0, 0, "Mostrar Clones en Escena")
        self.GroupEnd()
        self.GroupEnd()
        
        self.GroupBegin(GRP_UDP_CONFIG, c4d.BFH_SCALEFIT, cols=4)
        self.GroupBorder(c4d.BORDER_THIN_IN)
        self.GroupBorderSpace(10, 10, 10, 10)
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Dirección IP (Host):", c4d.BORDER_NONE)
        self.AddEditText(TXT_UDP_IP, c4d.BFH_SCALEFIT, 120, 0)
        
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Puerto (Port):", c4d.BORDER_NONE)
        self.AddEditNumberArrows(NUM_UDP_PORT, c4d.BFH_LEFT, 70, 0)
        self.GroupEnd()

        self.GroupBegin(GRP_BOTONES_BASE, c4d.BFH_SCALEFIT, cols=2)
        self.AddButton(BTN_CONECTAR, c4d.BFH_SCALEFIT, 0, 35, "Validar Telemetría (Local)")
        self.AddButton(BTN_START_TRAINING, c4d.BFH_SCALEFIT, 0, 35, "Iniciar Simulación Paralela")
        self.GroupEnd()
        
        return True

    def InitValues(self):
        doc = c4d.documents.GetActiveDocument()
        if not doc: return True
        
        bc = doc.GetDataInstance().GetContainerInstance(PLUGIN_ID)
        if bc:
            self.cant_servos = bc.GetInt32(ID_CANT_SERVOS_BC, 10)
            self.cant_sensores = bc.GetInt32(ID_CANT_SENSORES_BC, 5)
            self.cant_dist_sensores = bc.GetInt32(ID_CANT_DIST_BC, 3) 
            self.instancias = bc.GetInt32(ID_INSTANCIAS_BC, 4)
            self.distancia_cm = bc.GetInt32(ID_DISTANCIA_CM_BC, 2000)
            self.modo_espectador = bc.GetBool(ID_MODO_ESPECTADOR_BC, False)
            self.mostrar_clones = bc.GetBool(ID_MOSTRAR_CLONES_BC, False)
            self.ciclo_ms = bc.GetInt32(ID_CICLO_MS_BC, 0)
            self.udp_ip = bc.GetString(ID_UDP_IP_BC, "127.0.0.1")
            self.udp_port = bc.GetInt32(ID_UDP_PORT_BC, 2026)
            
            obj_maestro = bc.GetLink(OFFSET_ROBOT_MAESTRO_LINK, doc)
            if obj_maestro:
                lk = self.FindCustomGui(LNK_ROBOT_MAESTRO, c4d.CUSTOMGUI_LINKBOX)
                if lk: lk.SetLink(obj_maestro)
        else:
            self.cant_servos = 10
            self.cant_sensores = 5
            self.cant_dist_sensores = 3
            self.instancias = 4
            self.distancia_cm = 2000
            self.modo_espectador = False
            self.mostrar_clones = False
            self.ciclo_ms = 0
            self.udp_ip = "127.0.0.1"
            self.udp_port = 2026
        
        self.SetInt32(NUM_CANT_SERVOS, self.cant_servos, min=1, max=50)
        self.SetInt32(NUM_CANT_SENSORES, self.cant_sensores, min=1, max=25)
        self.SetInt32(NUM_CANT_DIST_SENSORS, self.cant_dist_sensores, min=1, max=32) 
        self.SetInt32(NUM_INSTANCIAS, self.instancias, min=1, max=32)
        self.SetInt32(NUM_DISTANCIA_CM, self.distancia_cm, min=10, max=100000)
        self.SetInt32(NUM_TRAINING_STEPS, 100, min=1, max=10000)
        self.SetInt32(NUM_CICLO_MS, self.ciclo_ms, min=0, max=5000)
        self.SetBool(CHK_MODO_ESPECTADOR, self.modo_espectador)
        self.SetBool(CHK_MOSTRAR_CLONES, self.mostrar_clones)
        
        self.SetString(TXT_UDP_IP, self.udp_ip)
        self.SetInt32(NUM_UDP_PORT, self.udp_port, min=1024, max=65535)
        
        self.LayoutFlushGroup(GRP_DYNAMIC_MAIN)
        self.DibujarListasDinamicas()
        self.LayoutChanged(GRP_MASTER_SCROLL)
        return True

    def DibujarListasDinamicas(self):
        doc = c4d.documents.GetActiveDocument()
        if not doc: return
        bc = doc.GetDataInstance().GetContainerInstance(PLUGIN_ID)
        
        # --- 1. CONFIGURACIÓN DE SERVOS ---
        # cols=5 para albergar de forma lineal: ID | Link | Mínimo | Máximo | Velocidad
        self.GroupBegin(GRP_SERVOS, c4d.BFH_SCALEFIT, cols=5, title="Configuración de Servos (Relación Directa 1:1)")
        self.GroupBorder(c4d.BORDER_THIN_IN)
        self.GroupBorderSpace(10, 10, 10, 10)
        
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Servo ID", c4d.BORDER_NONE)
        self.AddStaticText(0, c4d.BFH_SCALEFIT, 0, 0, "Objeto C4D (Link)", c4d.BORDER_NONE)
        self.AddStaticText(0, c4d.BFH_CENTER, 0, 0, "Límite Mín (°)", c4d.BORDER_NONE)
        self.AddStaticText(0, c4d.BFH_CENTER, 0, 0, "Límite Máx (°)", c4d.BORDER_NONE)
        self.AddStaticText(0, c4d.BFH_CENTER, 0, 0, "Velocidad (°/s)", c4d.BORDER_NONE)
        
        for i in range(1, self.cant_servos + 1):
            self.AddStaticText(2100 + i, c4d.BFH_LEFT, 0, 0, "Servo {}".format(i), c4d.BORDER_NONE)
            self.AddCustomGui(2200 + i, c4d.CUSTOMGUI_LINKBOX, "", c4d.BFH_SCALEFIT, 150, 0)
            if bc:
                obj_vinculado = bc.GetLink(OFFSET_SERVO_LINK + i, doc)
                if obj_vinculado:
                    lk = self.FindCustomGui(2200 + i, c4d.CUSTOMGUI_LINKBOX)
                    if lk: lk.SetLink(obj_vinculado)
            
            # Límite Mínimo Geométrico (Por defecto 0.0)
            self.AddEditNumber(2500 + i, c4d.BFH_CENTER, 50, 0)
            val_min = bc.GetFloat(OFFSET_SERVO_MIN + i, 0.0) if bc else 0.0
            self.SetFloat(2500 + i, val_min)
            
            # Límite Máximo Geométrico (Por defecto 180.0)
            self.AddEditNumber(2600 + i, c4d.BFH_CENTER, 50, 0)
            val_max = bc.GetFloat(OFFSET_SERVO_MAX + i, 180.0) if bc else 180.0
            self.SetFloat(2600 + i, val_max)
            
            # Velocidad en Grados por Segundo (°/s)
            self.AddEditNumber(2300 + i, c4d.BFH_CENTER, 50, 0)
            val_vel = bc.GetFloat(OFFSET_SERVO_VEL + i, 360.0) if bc else 360.0
            self.SetFloat(2300 + i, val_vel)
            
        self.GroupEnd()

        
        self.GroupBegin(0, c4d.BFH_SCALEFIT, cols=1)
        self.AddStaticText(0, c4d.BFH_SCALEFIT, 0, 10, "", c4d.BORDER_NONE)
        self.GroupEnd()
        
        # --- 2. CONFIGURACIÓN DE SENSORES IMU (BNO055) ---
        self.GroupBegin(GRP_SENSORES, c4d.BFH_SCALEFIT, cols=4, title="Configuración de Sensores IMU (BNO055)")
        self.GroupBorder(c4d.BORDER_THIN_IN)
        self.GroupBorderSpace(10, 10, 10, 10)
        
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Sensor ID", c4d.BORDER_NONE)
        self.AddStaticText(0, c4d.BFH_SCALEFIT, 0, 0, "Objeto Referencia C4D", c4d.BORDER_NONE)
        self.AddStaticText(0, c4d.BFH_CENTER, 0, 0, "Ruido: Acel. (" + "σ".decode('utf-8') + "_A)", c4d.BORDER_NONE)
        # Cambio de texto de la columna
        self.AddStaticText(0, c4d.BFH_CENTER, 0, 0, "Rango Máx Acel (m/s²)", c4d.BORDER_NONE)
        
        for i in range(1, self.cant_sensores + 1):
            self.AddStaticText(3100 + i, c4d.BFH_LEFT, 0, 0, "Sensor IMU {}".format(i), c4d.BORDER_NONE)
            self.AddCustomGui(3200 + i, c4d.CUSTOMGUI_LINKBOX, "", c4d.BFH_SCALEFIT, 150, 0)
            if bc:
                obj_vinculado = bc.GetLink(OFFSET_SENSOR_LINK + i, doc)
                if obj_vinculado:
                    lk = self.FindCustomGui(3200 + i, c4d.CUSTOMGUI_LINKBOX)
                    if lk: lk.SetLink(obj_vinculado)
            
            self.AddEditNumber(3300 + i, c4d.BFH_CENTER, 50, 0)
            val_ruido_acel = bc.GetFloat(OFFSET_SENSOR_RUIDO_ACEL + i, 0.05) if bc else 0.05
            self.SetFloat(3300 + i, val_ruido_acel)
            
            # Cambiado: Ahora lee y setea la casilla usando el nuevo offset semántico
            self.AddEditNumber(3400 + i, c4d.BFH_CENTER, 50, 0)
            val_max_acel = bc.GetFloat(OFFSET_SENSOR_RANGO_MAX_ACEL + i, 20.0) if bc else 20.0
            self.SetFloat(3400 + i, val_max_acel)
        self.GroupEnd()

        
        self.GroupBegin(0, c4d.BFH_SCALEFIT, cols=1)
        self.AddStaticText(0, c4d.BFH_SCALEFIT, 0, 10, "", c4d.BORDER_NONE)
        self.GroupEnd()
        
        # --- 3. CONFIGURACIÓN OPTIMIZADA DE SENSORES DE DISTANCIA ---
        self.GroupBegin(GRP_DIST_SENSORS, c4d.BFH_SCALEFIT, cols=4, title="Configuración de Sensores de Distancia (Raycast)")
        self.GroupBorder(c4d.BORDER_THIN_IN)
        self.GroupBorderSpace(10, 10, 10, 10)
        
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Sensor ID", c4d.BORDER_NONE)
        self.AddStaticText(0, c4d.BFH_SCALEFIT, 0, 0, "Objeto Emisor C4D (Eje Z)", c4d.BORDER_NONE)
        self.AddStaticText(0, c4d.BFH_SCALEFIT, 0, 0, "Objeto Objetivo (Malla / Conectar)", c4d.BORDER_NONE)
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Rango Máx (cm)", c4d.BORDER_NONE)
        
        for i in range(1, self.cant_dist_sensores + 1):
            self.AddStaticText(3600 + i, c4d.BFH_LEFT, 0, 0, "Distancia {}".format(i), c4d.BORDER_NONE)
            
            self.AddCustomGui(3700 + i, c4d.CUSTOMGUI_LINKBOX, "", c4d.BFH_SCALEFIT, 120, 0)
            if bc:
                obj_vinculado = bc.GetLink(OFFSET_DIST_LINK + i, doc)
                if obj_vinculado:
                    lk = self.FindCustomGui(3700 + i, c4d.CUSTOMGUI_LINKBOX)
                    if lk: lk.SetLink(obj_vinculado)
            
            self.AddCustomGui(3900 + i, c4d.CUSTOMGUI_LINKBOX, "", c4d.BFH_SCALEFIT, 120, 0)
            if bc:
                obj_target = bc.GetLink(OFFSET_DIST_TARGET + i, doc)
                if obj_target:
                    lk_t = self.FindCustomGui(3900 + i, c4d.CUSTOMGUI_LINKBOX)
                    if lk_t: lk_t.SetLink(obj_target)
            
            self.AddEditNumber(3800 + i, c4d.BFH_LEFT, 60, 0)
            val_max = bc.GetFloat(OFFSET_DIST_MAX + i, 300.0) if bc else 300.0
            self.SetFloat(3800 + i, val_max)
        self.GroupEnd()
        
        self.GroupBegin(0, c4d.BFH_SCALEFIT, cols=1)
        self.AddStaticText(0, c4d.BFH_SCALEFIT, 0, 10, "", c4d.BORDER_NONE)
        self.GroupEnd()

    def GuardarDatosEnDocumento(self):
        doc = c4d.documents.GetActiveDocument()
        if not doc: return
        root_bc = doc.GetDataInstance()
        bc = root_bc.GetContainerInstance(PLUGIN_ID)
        if not bc:
            root_bc.SetContainer(PLUGIN_ID, c4d.BaseContainer())
            bc = root_bc.GetContainerInstance(PLUGIN_ID)
        
        bc.SetInt32(ID_CANT_SERVOS_BC, self.cant_servos)
        bc.SetInt32(ID_CANT_SENSORES_BC, self.cant_sensores)
        bc.SetInt32(ID_CANT_DIST_BC, self.cant_dist_sensores) 
        bc.SetInt32(ID_INSTANCIAS_BC, self.instancias)
        bc.SetInt32(ID_DISTANCIA_CM_BC, self.distancia_cm)
        bc.SetBool(ID_MODO_ESPECTADOR_BC, self.modo_espectador)
        bc.SetBool(ID_MOSTRAR_CLONES_BC, self.mostrar_clones)
        bc.SetInt32(ID_CICLO_MS_BC, self.ciclo_ms)
        bc.SetString(ID_UDP_IP_BC, self.udp_ip)
        bc.SetInt32(ID_UDP_PORT_BC, self.udp_port)
        
        lk_maestro = self.FindCustomGui(LNK_ROBOT_MAESTRO, c4d.CUSTOMGUI_LINKBOX)
        if lk_maestro:
            obj_m = lk_maestro.GetLink(doc)
            if obj_m is not None: bc.SetLink(OFFSET_ROBOT_MAESTRO_LINK, obj_m)
            else: bc.RemoveData(OFFSET_ROBOT_MAESTRO_LINK)
        
        for i in range(1, self.cant_servos + 1):
            lk = self.FindCustomGui(2200 + i, c4d.CUSTOMGUI_LINKBOX)
            if lk:
                obj = lk.GetLink(doc)
                if obj is not None: bc.SetLink(OFFSET_SERVO_LINK + i, obj)
                else: bc.RemoveData(OFFSET_SERVO_LINK + i)
            bc.SetFloat(OFFSET_SERVO_MIN + i, self.GetFloat(2500 + i))
            bc.SetFloat(OFFSET_SERVO_MAX + i, self.GetFloat(2600 + i))
            bc.SetFloat(OFFSET_SERVO_VEL + i, self.GetFloat(2300 + i))
        
        # Volcado dinámico de IMUs
        for i in range(1, self.cant_sensores + 1):
            lk = self.FindCustomGui(3200 + i, c4d.CUSTOMGUI_LINKBOX)
            if lk:
                obj = lk.GetLink(doc)
                if obj is not None: bc.SetLink(OFFSET_SENSOR_LINK + i, obj)
                else: bc.RemoveData(OFFSET_SENSOR_LINK + i)
            bc.SetFloat(OFFSET_SENSOR_RUIDO_ACEL + i, self.GetFloat(3300 + i))
            # Cambiado: Guarda el valor en el nuevo offset correcto
            bc.SetFloat(OFFSET_SENSOR_RANGO_MAX_ACEL + i, self.GetFloat(3400 + i))

        
        for i in range(1, self.cant_dist_sensores + 1):
            lk_e = self.FindCustomGui(3700 + i, c4d.CUSTOMGUI_LINKBOX)
            if lk_e:
                obj_e = lk_e.GetLink(doc)
                if obj_e is not None: bc.SetLink(OFFSET_DIST_LINK + i, obj_e)
                else: bc.RemoveData(OFFSET_DIST_LINK + i)
            
            lk_t = self.FindCustomGui(3900 + i, c4d.CUSTOMGUI_LINKBOX)
            if lk_t:
                obj_t = lk_t.GetLink(doc)
                if obj_t is not None: bc.SetLink(OFFSET_DIST_TARGET + i, obj_t)
                else: bc.RemoveData(OFFSET_DIST_TARGET + i)
            
            bc.SetFloat(OFFSET_DIST_MAX + i, self.GetFloat(3800 + i))
        
        doc.SetChanged()

    def BuscarObjetoPorNombre(self, root, nombre):
        if not root: return None
        if root.GetName() == nombre: return root
        
        hijo = root.GetDown()
        while hijo:
            resultado = self.BuscarObjetoPorNombre(hijo, nombre)
            if resultado: return resultado
            hijo = hijo.GetNext()
        return None

    def LimpiarClonesExistentes(self, doc):
        antiguo_contenedor = doc.SearchObject(NOMBRE_CONTENEDOR_CLONES)
        if antiguo_contenedor:
            antiguo_contenedor.Remove()
        c4d.EventAdd()

    def ActualizarClonacionEnTiempoReal(self):
        doc = c4d.documents.GetActiveDocument()
        if not doc: return
        
        self.LimpiarClonesExistentes(doc)
        if not self.mostrar_clones: return
        
        lk_maestro = self.FindCustomGui(LNK_ROBOT_MAESTRO, c4d.CUSTOMGUI_LINKBOX)
        obj_maestro = lk_maestro.GetLink(doc) if lk_maestro else None
        if not obj_maestro: return
        
        contenedor = c4d.BaseObject(c4d.Onull)
        contenedor.SetName(NOMBRE_CONTENEDOR_CLONES)
        doc.InsertObject(contenedor)
        
        columnas_max = int(self.instancias ** 0.5)
        if columnas_max < 1: columnas_max = 1
        
        for k in range(self.instancias):
            fila = k // columnas_max
            columna = k % columnas_max
            
            pos_x = columna * self.distancia_cm
            pos_z = fila * self.distancia_cm
            
            clon = obj_maestro.GetClone(c4d.COPYFLAGS_0)
            if clon:
                clon.SetName("Robot_Clon_{}".format(k + 1))
                clon.SetMl(c4d.Matrix(c4d.Vector(pos_x, 0, pos_z)))
                clon.InsertUnder(contenedor)
        
        c4d.EventAdd()

    def MuestrearAyudaVelocidad(self):
        mensaje = (
            "=== GUÍA DE CALIBRACIÓN DE VELOCIDAD ===\n\n"
            "Los fabricantes expresan la velocidad en segundos por cada 60 grados (ej. 0.200s/60°).\n"
            "El simulador exige el valor convertido a Grados por Segundo (°/s).\n\n"
            "FÓRMULA DE CONVERSIÓN:\n"
            "Velocidad (°/s) = 60 / Tiempo del Catálogo"
        )
        gui.MessageDialog(mensaje)

    def IniciarSimulacion(self):
        doc = c4d.documents.GetActiveDocument()
        if not doc: return True
        
        print("=" * 80)
        
        # --- SECCIÓN 1: ACTUADORES (SERVOS) ---
        # Contamos primero cuántos servos válidos hay online para pintar el título exacto
        servos_online = []
        for i in range(1, self.cant_servos + 1):
            linkbox = self.FindCustomGui(2200 + i, c4d.CUSTOMGUI_LINKBOX)
            obj = linkbox.GetLink(doc) if linkbox else None
            if obj:
                servos_online.append((i, obj))
                
        if len(servos_online) > 0:
            print("    " + "─" * 15 + " ACTUADORES SERVOS ({}) ".format(len(servos_online)) + "─" * 15)
            for i, obj in servos_online:
                angulo_final = c4d.utils.RadToDeg(obj.GetAbsRot().y)
                print("    [SERVO_CH_{0:02d}] ──> Ángulo Eje: {1:+7.2f}°".format(i, angulo_final))
        
        # --- SECCIÓN 2: SENSORES INERCIALES (IMUS) ---
        imus_online = []
        for i in range(1, self.cant_sensores + 1):
            linkbox = self.FindCustomGui(3200 + i, c4d.CUSTOMGUI_LINKBOX)
            obj = linkbox.GetLink(doc) if linkbox else None
            if obj:
                imus_online.append((i, obj))
                
        if len(imus_online) > 0:
            print("    " + "─" * 15 + " MATRIZ INERCIAL IMUS ({}) ".format(len(imus_online)) + "─" * 15)
            # Recuperamos el cálculo de delta tiempo (dt) necesario para calcular la aceleración inercial
            fps = doc.GetFps() if doc.GetFps() > 0 else 60.0
            dt = 1.0 / fps
            if not hasattr(self, 'historico_imus'):
                self.historico_imus = {}
                
            for i, obj in imus_online:
                mg = obj.GetMg()
                pos_actual = mg.off
                
                # Orientación nativa en flotante sin snap rígido a entero
                rot_flotante = c4d.utils.MatrixToHPB(mg)
                pitch_flotante = c4d.utils.RadToDeg(rot_flotante.y)
                roll_flotante = c4d.utils.RadToDeg(rot_flotante.z)
                
                # Cálculo de la aceleración lineal dinámica (idéntico a tu pipeline de simulación)
                id_hist = "diagnostico_{}".format(i)
                if id_hist not in self.historico_imus:
                    self.historico_imus[id_hist] = {"pos": pos_actual, "vel": c4d.Vector(0)}
                
                hist = self.historico_imus[id_hist]
                vel_actual = (pos_actual - hist["pos"]) * (1.0 / dt)
                vel_actual_m = vel_actual * 0.01
                vel_anterior_m = hist["vel"] * 0.01
                acel_m = (vel_actual_m - vel_anterior_m) * (1.0 / dt)
                
                # Guardamos histórico local para mantener la coherencia del refresco visual
                self.historico_imus[id_hist]["pos"] = pos_actual
                self.historico_imus[id_hist]["vel"] = vel_actual
                
                print("    [IMU_CH_{0:02d}]".format(i))
                print("          Orientación Absoluta: Pitch: {0:+7.2f}° | Roll: {1:+7.2f}°".format(pitch_flotante, roll_flotante))
                print("          Aceleración Dinámica: Eje X: {0:+7.2f} | Eje Y: {1:+7.2f} | Eje Z: {2:+7.2f} m/s²".format(acel_m.x, acel_m.y, acel_m.z))
        
        # --- SECCIÓN 3: SENSORES ÓPTICOS (LÁSER DISTANCIA) ---
        dist_online = []
        for i in range(1, self.cant_dist_sensores + 1):
            lk_e = self.FindCustomGui(3700 + i, c4d.CUSTOMGUI_LINKBOX)
            lk_t = self.FindCustomGui(3900 + i, c4d.CUSTOMGUI_LINKBOX)
            obj_emisor = lk_e.GetLink(doc) if lk_e else None
            obj_target = lk_t.GetLink(doc) if lk_t else None
            if obj_emisor and obj_target:
                dist_online.append((i, obj_emisor, obj_target))
                
        if len(dist_online) > 0:
            print("    " + "─" * 15 + " TELEMETRÍA RAYCAST DISTANCIAS ({}) ".format(len(dist_online)) + "─" * 15)
            for i, obj_emisor, obj_target in dist_online:
                root_bc = doc.GetDataInstance()
                bc = root_bc.GetContainerInstance(PLUGIN_ID) if root_bc else None
                val_max = bc.GetFloat(OFFSET_DIST_MAX + i, 300.0) if bc else 300.0
                distancia_real = val_max
                
                poly_target = obj_target
                if obj_target.GetType() != c4d.Opolygon:
                    cache = obj_target.GetDeformCache() or obj_target.GetCache()
                    if cache and cache.GetType() == c4d.Opolygon:
                        poly_target = cache
                
                if poly_target and poly_target.GetType() == c4d.Opolygon:
                    temp_poly = poly_target.GetClone(c4d.COPYFLAGS_0)
                    mg_target = obj_target.GetMg()
                    puntos_globales = [mg_target * p for p in temp_poly.GetAllPoints()]
                    temp_poly.SetAllPoints(puntos_globales)
                    temp_poly.Message(c4d.MSG_UPDATE)
                    
                    mg_emisor = obj_emisor.GetMg()
                    origen_global = mg_emisor.off
                    direccion_global = mg_emisor.v3.GetNormalized()
                    
                    rc_test = c4d.utils.GeRayCollider()
                    rc_test.Init(temp_poly, force=True)
                    
                    if rc_test.Intersect(origen_global, direccion_global, val_max):
                        primer_impacto = rc_test.GetNearestIntersection()
                        if primer_impacto:
                            distancia_real = primer_impacto['distance']
                
                print("    [DIST_CH_{0:02d}] ──> Distancia Detectada: {1:7.2f} cm".format(i, distancia_real))
        
        print("=" * 80)
        
        # --- SECCIÓN 4: RED COLA DE DIAGNÓSTICO (PING) ---
        ip_destino = self.GetString(TXT_UDP_IP)
        puerto_destino = self.GetInt32(NUM_UDP_PORT)
        
        sock_check = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_check.settimeout(0.05) 
        
        server_escuchando = False
        try:
            sock_check.sendto(b"PING_CHECK", (ip_destino, puerto_destino))
            respuesta, _ = sock_check.recvfrom(1024)
            if respuesta == b"PONG_ALIVE":
                server_escuchando = True
        except Exception:
            server_escuchando = False
        finally:
            sock_check.close()
        
        if server_escuchando:
            print(">>> ÉXITO: PIPELINE DE COMUNICACIONES VERIFICADO // DESTINO: UDP://{}:{}".format(ip_destino, puerto_destino))
        else:
            print(">>> ERROR: EL SERVIDOR NO RESPONDE EN UDP://{}:{} // VERIFIQUE EL SOCKET.".format(ip_destino, puerto_destino))
        
        return True



    def EjecutarSimulacionParalela(self):
        doc = c4d.documents.GetActiveDocument()
        if not doc: return
        
        lk_maestro = self.FindCustomGui(LNK_ROBOT_MAESTRO, c4d.CUSTOMGUI_LINKBOX)
        obj_maestro = lk_maestro.GetLink(doc) if lk_maestro else None
        if not obj_maestro:
            gui.MessageDialog("Error: Por favor, vincula el objeto Nulo del 'Robot Maestro' antes de entrenar.")
            return
        
        def EsHijoDe(obj_nodo, obj_ancestro):
            if not obj_nodo or not obj_ancestro:
                return False
            actual = obj_nodo.GetUp()
            while actual:
                if actual == obj_ancestro:
                    return True
                actual = actual.GetUp()
            return False
        
        pasos = self.GetInt32(NUM_TRAINING_STEPS)
        espectador = self.GetBool(CHK_MODO_ESPECTADOR)
        retardo = self.GetInt32(NUM_CICLO_MS)
        
        ip_destino = self.GetString(TXT_UDP_IP)
        puerto_destino = self.GetInt32(NUM_UDP_PORT)
        fps = doc.GetFps() if doc.GetFps() > 0 else 60.0
        dt = 1.0 / fps
        
        contenedor_clones = doc.SearchObject(NOMBRE_CONTENEDOR_CLONES)
        clones_activos = True if (contenedor_clones and self.mostrar_clones) else False
        entornos_reales = self.instancias if clones_activos else 1
        
        if not hasattr(self, 'historico_imus'):
            self.historico_imus = {}
        
        print("\n=== INICIANDO ENVÍO FILTRADO ADAPTATIVO OPTIMIZADO (16-BIT INT) ===")
        
        root_bc = doc.GetDataInstance()
        bc = root_bc.GetContainerInstance(PLUGIN_ID)
        
        # --- FILTRAR SERVOS ACTUADORES ---
        servos_maestros = []
        for i in range(1, self.cant_servos + 1):
            lk = self.FindCustomGui(2200 + i, c4d.CUSTOMGUI_LINKBOX)
            obj = lk.GetLink(doc) if lk else None
            if obj:
                if not EsHijoDe(obj, obj_maestro) and obj != obj_maestro:
                    continue
                val_min = bc.GetFloat(OFFSET_SERVO_MIN + i, 0.0) if bc else 0.0
                val_max = bc.GetFloat(OFFSET_SERVO_MAX + i, 180.0) if bc else 180.0
                val_vel = bc.GetFloat(OFFSET_SERVO_VEL + i, 360.0) if bc else 360.0
                servos_maestros.append((i, obj, val_min, val_max, val_vel))
        
        # --- FILTRAR IMUS ---
        imus_maestras = []
        for i in range(1, self.cant_sensores + 1):
            lk = self.FindCustomGui(3200 + i, c4d.CUSTOMGUI_LINKBOX)
            obj = lk.GetLink(doc) if lk else None
            if obj:
                if not EsHijoDe(obj, obj_maestro) and obj != obj_maestro:
                    continue
                val_ruido_acel = bc.GetFloat(OFFSET_SENSOR_RUIDO_ACEL + i, 0.05) if bc else 0.05
                rango_max_acel = bc.GetFloat(OFFSET_SENSOR_RANGO_MAX_ACEL + i, 20.0) if bc else 20.0
                if rango_max_acel <= 0.001: rango_max_acel = 20.0
                imus_maestras.append((i, obj, val_ruido_acel, rango_max_acel))
        
        # --- FILTRAR SENSORES DE DISTANCIA ---
        dist_maestros = []
        for i in range(1, self.cant_dist_sensores + 1):
            lk_emisor = self.FindCustomGui(3700 + i, c4d.CUSTOMGUI_LINKBOX)
            lk_target = self.FindCustomGui(3900 + i, c4d.CUSTOMGUI_LINKBOX)
            obj_emisor = lk_emisor.GetLink(doc) if lk_emisor else None
            obj_target = lk_target.GetLink(doc) if lk_target else None
            
            if obj_emisor and obj_target:
                if not EsHijoDe(obj_emisor, obj_maestro) and obj_emisor != obj_maestro:
                    continue
                val_max = bc.GetFloat(OFFSET_DIST_MAX + i, 300.0) if bc else 300.0
                dist_maestros.append((i, obj_emisor, obj_target, val_max))
        
        # =========================================================================
        # OPTIMIZACIÓN PRE-BUCLE 1: Precompilación de formatos Struct (Velocidad C)
        # =========================================================================
        struct_header = struct.Struct("<HHBBB")
        struct_clon_id = struct.Struct("<B")
        struct_uint16 = struct.Struct("<H")
        struct_imu = struct.Struct("<hhhhh")
        
        # =========================================================================
        # OPTIMIZACIÓN PRE-BUCLE 2: Caché Estático de Jerarquías de Clones
        # =========================================================================
        mapa_clones = {}
        
        for clon_idx in range(entornos_reales):
            mapa_clones[clon_idx] = {
                'servos': {},
                'imus': {},
                'dist_emisor': {},
                'dist_target': {}
            }
            if clones_activos:
                nombre_clon = "Robot_Clon_{}".format(clon_idx + 1)
                obj_entorno_raiz = doc.SearchObject(nombre_clon)
                if obj_entorno_raiz:
                    # Cachear correspondencias de Servos
                    for casilla_id, obj_m_servo, _, _, _ in servos_maestros:
                        obj_c = self.BuscarObjetoPorNombre(obj_entorno_raiz, obj_m_servo.GetName())
                        mapa_clones[clon_idx]['servos'][casilla_id] = obj_c or obj_m_servo
                    
                    # Cachear correspondencias de IMUs
                    for casilla_id, obj_m_imu, _, _ in imus_maestras:
                        obj_c = self.BuscarObjetoPorNombre(obj_entorno_raiz, obj_m_imu.GetName())
                        mapa_clones[clon_idx]['imus'][casilla_id] = obj_c or obj_m_imu
                    
                    # Cachear correspondencias de Sensores de Distancia
                    for casilla_id, obj_m_emisor, obj_m_target, _ in dist_maestros:
                        obj_e = self.BuscarObjetoPorNombre(obj_entorno_raiz, obj_m_emisor.GetName())
                        obj_t = self.BuscarObjetoPorNombre(obj_entorno_raiz, obj_m_target.GetName())
                        mapa_clones[clon_idx]['dist_emisor'][casilla_id] = obj_e or obj_m_emisor
                        mapa_clones[clon_idx]['dist_target'][casilla_id] = obj_t or obj_m_target
            else:
                # Si no hay clones, mapear directamente los objetos maestros del robot
                for casilla_id, obj_m_servo, _, _, _ in servos_maestros:
                    mapa_clones[clon_idx]['servos'][casilla_id] = obj_m_servo
                for casilla_id, obj_m_imu, _, _ in imus_maestras:
                    mapa_clones[clon_idx]['imus'][casilla_id] = obj_m_imu
                for casilla_id, obj_m_emisor, obj_m_target, _ in dist_maestros:
                    mapa_clones[clon_idx]['dist_emisor'][casilla_id] = obj_m_emisor
                    mapa_clones[clon_idx]['dist_target'][casilla_id] = obj_m_target
        
        # =========================================================================
        # OPTIMIZACIÓN PRE-BUCLE 3: Instancia única de GeRayCollider
        # =========================================================================
        rc = c4d.utils.GeRayCollider()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (ip_destino, puerto_destino)
        tiempo_original = doc.GetTime()
        
        try:
            for paso in range(1, pasos + 1):
                tiempo_actual = c4d.BaseTime(paso, fps)
                doc.SetTime(tiempo_actual)
                doc.ExecutePasses(bt=None, animation=True, expressions=True, caches=True, flags=0)
                
                # Cabecera optimizada mediante uso de la instancia Struct compilada
                payload = bytearray(struct_header.pack(paso, entornos_reales, len(servos_maestros), len(imus_maestras), len(dist_maestros)))
                
                for clon_idx in range(entornos_reales):
                    payload.extend(struct_clon_id.pack(clon_idx))
                    cache_clon = mapa_clones[clon_idx]
                    
                    # --- SECCIÓN SERVOS (2 bytes por servo -> 'H') ---
                    for casilla_id, _, val_min, val_max, val_vel in servos_maestros:
                        obj_actual_servo = cache_clon['servos'].get(casilla_id)
                        
                        if obj_actual_servo:
                            angulo_flotante = c4d.utils.RadToDeg(obj_actual_servo.GetAbsRot().y)
                            angulo_flotante = max(val_min, min(val_max, angulo_flotante))
                        else:
                            angulo_flotante = 0.0
                        
                        rango_servo = (val_max - val_min) if (val_max - val_min) > 0 else 180.0
                        val_normalizado = int((angulo_flotante - val_min) / rango_servo * 65535)
                        val_uint16 = max(0, min(65535, val_normalizado))
                        payload.extend(struct_uint16.pack(val_uint16))
                    
                    # --- SECCIÓN IMUS (10 bytes por IMU -> 'hhhhh') ---
                    for casilla_id, _, ruido_acel, rango_max_acel in imus_maestras:
                        obj_actual_imu = cache_clon['imus'].get(casilla_id)
                        
                        if obj_actual_imu:
                            mg = obj_actual_imu.GetMg()
                            
                            rot_flotante = c4d.utils.MatrixToHPB(mg)
                            pitch_flotante = c4d.utils.RadToDeg(rot_flotante.y)
                            roll_flotante = c4d.utils.RadToDeg(rot_flotante.z)
                            
                            pos_actual = mg.off
                            
                            id_hist = "{}_{}".format(clon_idx, casilla_id)
                            if id_hist not in self.historico_imus:
                                self.historico_imus[id_hist] = {"pos": pos_actual, "vel": c4d.Vector(0)}
                            
                            hist = self.historico_imus[id_hist]
                            vel_actual = (pos_actual - hist["pos"]) * (1.0 / dt)
                            vel_actual_m = vel_actual * 0.01
                            vel_anterior_m = hist["vel"] * 0.01
                            
                            acel_m = (vel_actual_m - vel_anterior_m) * (1.0 / dt)
                            
                            self.historico_imus[id_hist]["pos"] = pos_actual
                            self.historico_imus[id_hist]["vel"] = vel_actual
                            
                            if ruido_acel > 0:
                                semilla = paso + clon_idx + casilla_id
                                r_x = (math.sin(semilla * 12.9898) * 43758.5453) % 1.0 - 0.5
                                r_y = (math.sin(semilla * 78.233) * 43758.5453) % 1.0 - 0.5
                                r_z = (math.sin(semilla * 45.164) * 43758.5453) % 1.0 - 0.5
                                acel_m.x += r_x * ruido_acel
                                acel_m.y += r_y * ruido_acel
                                acel_m.z += r_z * ruido_acel
                        else:
                            pitch_flotante = roll_flotante = 0.0
                            acel_m = c4d.Vector(0.0)
                        
                        pitch_int16 = max(-32768, min(32767, int(pitch_flotante * 100)))
                        roll_int16 = max(-32768, min(32767, int(roll_flotante * 100)))
                        
                        ax_int16 = max(-32767, min(32767, int((acel_m.x / rango_max_acel) * 32767)))
                        ay_int16 = max(-32767, min(32767, int((acel_m.y / rango_max_acel) * 32767)))
                        az_int16 = max(-32767, min(32767, int((acel_m.z / rango_max_acel) * 32767)))
                        
                        payload.extend(struct_imu.pack(pitch_int16, roll_int16, ax_int16, ay_int16, az_int16))
                    
                    # --- SECCIÓN SENSORES DE DISTANCIA (2 bytes por sensor -> 'H') ---
                    for casilla_id, _, _, val_max in dist_maestros:
                        distancia_detectada = val_max
                        
                        obj_actual_emisor = cache_clon['dist_emisor'].get(casilla_id)
                        obj_actual_target = cache_clon['dist_target'].get(casilla_id)
                        
                        if obj_actual_target and obj_actual_emisor:
                            poly_target = obj_actual_target
                            if obj_actual_target.GetType() != c4d.Opolygon:
                                cache = obj_actual_target.GetDeformCache() or obj_actual_target.GetCache()
                                if cache and cache.GetType() == c4d.Opolygon: 
                                    poly_target = cache
                            
                            if poly_target and poly_target.GetType() == c4d.Opolygon:
                                mg_emisor = obj_actual_emisor.GetMg()
                                mg_target = obj_actual_target.GetMg()
                                
                                # Matriz inversa matemática para calcular en espacio local del objetivo
                                mg_target_inv = ~mg_target
                                origen_local = mg_target_inv * mg_emisor.off
                                direccion_local = (mg_target_inv.MulV(mg_emisor.v3)).GetNormalized()
                                
                                # Inicialización directa en la geometría base libre de clones costosos
                                rc.Init(poly_target, force=False)
                                
                                if rc.Intersect(origen_local, direccion_local, val_max):
                                    primer_impacto = rc.GetNearestIntersection()
                                    if primer_impacto:
                                        distancia_detectada = primer_impacto['distance']
                        
                        dist_normalizada = int((distancia_detectada / val_max) * 65535)
                        dist_uint16 = max(0, min(65535, dist_normalizada))
                        payload.extend(struct_uint16.pack(dist_uint16))
                
                sock.sendto(payload, server_address)
                
                if espectador: 
                    c4d.DrawViews(c4d.DRAWFLAGS_ONLY_ACTIVE_VIEW | c4d.DRAWFLAGS_NO_THREAD)
                if retardo > 0: 
                    time.sleep(retardo / 1000.0)
        
        except Exception as e:
            print("[-] Error crítico en simulación binaria optimizada: {}".format(e))
        finally:
            sock.close()
        
        doc.SetTime(tiempo_original)
        doc.ExecutePasses(bt=None, animation=True, expressions=True, caches=True, flags=0)
        c4d.EventAdd()
        print("=== TRANSMISIÓN OPTIMIZADA COMPLETADA ===")







        
    def Command(self, id, msg):
        if id == BTN_RELOAD_UI:
            self.cant_servos = self.GetInt32(NUM_CANT_SERVOS)
            self.cant_sensores = self.GetInt32(NUM_CANT_SENSORES)
            self.cant_dist_sensores = self.GetInt32(NUM_CANT_DIST_SENSORS)
            self.LayoutFlushGroup(GRP_DYNAMIC_MAIN)
            self.DibujarListasDinamicas()
            self.LayoutChanged(GRP_MASTER_SCROLL)
            self.GuardarDatosEnDocumento()
            return True
        elif id == BTN_AYUDA_VEL:
            self.MuestrearAyudaVelocidad()
            return True
        elif id == BTN_CONECTAR:
            self.IniciarSimulacion()
            return True
        elif id == BTN_START_TRAINING:
            self.EjecutarSimulacionParalela()
            return True
            
        ids_estaticos = [
            NUM_CANT_SERVOS, NUM_CANT_SENSORES, NUM_CANT_DIST_SENSORS, LNK_ROBOT_MAESTRO, 
            NUM_INSTANCIAS, NUM_DISTANCIA_CM, NUM_TRAINING_STEPS, NUM_CICLO_MS, 
            CHK_MODO_ESPECTADOR, CHK_MOSTRAR_CLONES, TXT_UDP_IP, NUM_UDP_PORT
        ]
        
        if id in ids_estaticos or (id >= 2100 and id < 4000):
            self.cant_servos = self.GetInt32(NUM_CANT_SERVOS)
            self.cant_sensores = self.GetInt32(NUM_CANT_SENSORES)
            self.cant_dist_sensores = self.GetInt32(NUM_CANT_DIST_SENSORS)
            self.instancias = self.GetInt32(NUM_INSTANCIAS)
            self.distancia_cm = self.GetInt32(NUM_DISTANCIA_CM)
            self.modo_espectador = self.GetBool(CHK_MODO_ESPECTADOR)
            self.mostrar_clones = self.GetBool(CHK_MOSTRAR_CLONES)
            self.ciclo_ms = self.GetInt32(NUM_CICLO_MS)
            self.udp_ip = self.GetString(TXT_UDP_IP)
            self.udp_port = self.GetInt32(NUM_UDP_PORT)
            self.GuardarDatosEnDocumento()
            
            if id in [NUM_INSTANCIAS, NUM_DISTANCIA_CM, CHK_MOSTRAR_CLONES, LNK_ROBOT_MAESTRO]:
                self.ActualizarClonacionEnTiempoReal()
                return True
        return True

class EasyRobotRLCommand(c4d.plugins.CommandData):
    dialog = None
    def Execute(self, doc):
        if self.dialog is None: 
            self.dialog = EasyRobotRLDlg()
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=400, defaulth=500)
        
    def RestoreLayout(self, secret):
        if self.dialog is None: 
            self.dialog = EasyRobotRLDlg()
        return self.dialog.Restore(PLUGIN_ID, secret)

if __name__ == "__main__":
    import os
    bmp = c4d.bitmaps.BaseBitmap()
    ruta_icono = os.path.join(os.path.dirname(__file__), "icono.png")
    bmp.InitWith(ruta_icono)
    
    c4d.plugins.RegisterCommandPlugin(
        id=PLUGIN_ID, 
        str="Easy Robot RL", 
        info=0, 
        icon=bmp, 
        help="Herramienta de simulación paralela para IA", 
        dat=EasyRobotRLCommand()
    )
