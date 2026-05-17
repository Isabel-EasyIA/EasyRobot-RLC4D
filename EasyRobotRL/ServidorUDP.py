import socket
import struct

UDP_IP = "127.0.0.1"
UDP_PORT = 2026

# --- CONFIGURACIÓN DE RANGOS GEOMÉTRICOS Y DINÁMICOS ---
SERVO_VAL_MIN = 0.0
SERVO_VAL_MAX = 180.0
IMU_RANGO_MAX_ACEL = 20.0  
DIST_VAL_MAX = 3000.0       

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("========================================================================")
print("   SERVIDOR UNIVERSAL OPTIMIZADO - DECODIFICACIÓN 16-BIT INT V5.1       ")
print("========================================================================")
print(f"Estado: ESCUCHANDO | Canal: UDP://{UDP_IP}:{UDP_PORT}\n")

try:
    while True:
        data, addr = sock.recvfrom(65535)
        
        if data == b"PING_CHECK":
            sock.sendto(b"PONG_ALIVE", addr)
            continue
            
        if len(data) < 7: 
            continue
        
        step_id, num_clones, activos_servos, activos_imus, activos_dist = struct.unpack("<HHBBB", data[:7])
        
        print("\n" + "="*80)
        print(f"[PAQUETE UDP] Lote optimizado detectado | Longitud: {len(data)} Bytes")
        print(f"[DATAGRAMA] Paso: {step_id:04d} | Entornos Activos: {num_clones}")
        print(f"            Elementos por Clon -> Servos: {activos_servos} | IMUs: {activos_imus} | Sensores Dist: {activos_dist}")
        print("-" * 80)
        
        offset = 7
        
        for _ in range(num_clones):
            # 1. LEER ID DE CLON (1 Byte -> 'B')
            if offset + 1 > len(data): break
            clon_id = struct.unpack("<B", data[offset:offset+1])[0]
            offset += 1
            
            print(f"\n ──> ENTORNO [ID_{clon_id:02d}]")
                
            # 2. SECCIÓN SERVOS (2 Bytes por servo -> 'H')
            if activos_servos > 0:
                print("    " + "─"*15 + f" ACTUADORES SERVOS ({activos_servos}) " + "─"*15)
            for idx_servo in range(activos_servos):
                if offset + 2 > len(data): break
                servo_bytes = data[offset:offset+2]
                val_uint16 = struct.unpack("<H", servo_bytes)[0]
                offset += 2
                
                rango_servo = (SERVO_VAL_MAX - SERVO_VAL_MIN)
                angulo_reconstruido = SERVO_VAL_MIN + (val_uint16 / 65535.0) * rango_servo
                
                print(f"    [SERVO_CH_{idx_servo+1:02d}] ──> Ángulo: {angulo_reconstruido:+7.2f}° | RAW: {val_uint16:5d} | HEX: {servo_bytes.hex().upper()}")
                
            # 3. SECCIÓN IMUS (10 Bytes por IMU -> 'hhhhh')
            if activos_imus > 0:
                print("    " + "─"*15 + f" MATRIZ INERCIAL IMUS ({activos_imus}) " + "─"*15)
            for idx_imu in range(activos_imus):
                if offset + 10 > len(data): break
                imu_bytes = data[offset:offset+10]
                pitch_i16, roll_i16, ax_i16, ay_i16, az_i16 = struct.unpack("<hhhhh", imu_bytes)
                offset += 10
                
                pitch_deg = pitch_i16 / 100.0
                roll_deg  = roll_i16 / 100.0
                
                ax_m = (ax_i16 / 32767.0) * IMU_RANGO_MAX_ACEL
                ay_m = (ay_i16 / 32767.0) * IMU_RANGO_MAX_ACEL
                az_m = (az_i16 / 32767.0) * IMU_RANGO_MAX_ACEL
                
                print(f"    [IMU_CH_{idx_imu+1:02d}] HEX: {imu_bytes.hex().upper()}")
                print(f"          Orientación: Pitch: {pitch_deg:+7.2f}° | Roll: {roll_deg:+7.2f}°")
                print(f"          Aceleración: X: {ax_m:+7.2f} | Y: {ay_m:+7.2f} | Z: {az_m:+7.2f} m/s²")

            # 4. SECCIÓN DISTANCIAS (2 Bytes por sensor -> 'H')
            if activos_dist > 0:
                print("    " + "─"*15 + f" TELEMETRÍA RAYCAST DISTANCIAS ({activos_dist}) " + "─"*15)
            for idx_dist in range(activos_dist):
                if offset + 2 > len(data): break
                dist_bytes = data[offset:offset+2]
                dist_uint16 = struct.unpack("<H", dist_bytes)[0]
                offset += 2
                
                distancia_cm = (dist_uint16 / 65535.0) * DIST_VAL_MAX
                
                print(f"    [DIST_CH_{idx_dist+1:02d}] ──> Distancia: {distancia_cm:7.2f} cm | RAW: {dist_uint16:5d} | HEX: {dist_bytes.hex().upper()}")

        print("="*80)

except KeyboardInterrupt:
    print("\n[INFO_SIS] Servidor dinámico optimizado apagado de forma segura.")
finally:
    sock.close()
