import socket
import struct
import numpy as np

UDP_IP = "127.0.0.1"
UDP_PORT = 2026

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("========================================================================")
print("   MONITOR DE DATOS EN BRUTO Y NORMALIZACIÓN CORREGIDA v6.3            ")
print("========================================================================")
print(f"Estado: ESCUCHANDO | Canal: UDP://{UDP_IP}:{UDP_PORT}\n")

try:
    while True:
        # 1. CAPTURA DEL PAQUETE EN BRUTO DESDE CINEMA 4D
        data, addr = sock.recvfrom(65535)
        if len(data) < 7: 
            continue
        
        # Desempaquetar el encabezado general (7 bytes)
        step_id, num_clones, activos_servos, activos_imus, activos_dist = struct.unpack("<HHBBB", data[:7])
        
        print("\n" + "="*95)
        print(f"📥 [ENTRADA DESDE C4D] Paso: {step_id:04d} | Tamaño del Datagrama: {len(data)} Bytes")
        print(f"   PAQUETE HEXADECIMAL EN BRUTO (Primeros 100 bytes):")
        print(f"   {data[:100].hex().upper()}")
        print("-" * 95)
        
        offset = 7
        lista_estados_ia = []
        
        # 2. PROCESAMIENTO BINARIO EN MEMORIA POR CADA CLON
        for clon_idx in range(num_clones):
            if offset + 1 > len(data): break
            
            # Leer el ID del clon (1 byte) para garantizar la alineación del offset
            clon_id = struct.unpack("<B", data[offset:offset+1])[0]
            offset += 1
            
            # Calcular las dimensiones del bloque dinámico de este clon en la memoria
            bytes_servos = activos_servos * 2
            bytes_imus = activos_imus * 10
            bytes_dist = activos_dist * 2
            total_bytes_clon = bytes_servos + bytes_imus + bytes_dist
            
            if offset + total_bytes_clon > len(data): break
            
            # Capturar el fragmento de memoria específico de este clon
            fragmento_clon_raw = data[offset:offset + total_bytes_clon]
            
            # Desempaquetar todos los Uint16 e Int16 del clon en un solo golpe de CPU
            formato_clon = f"<{activos_servos}H{activos_imus * 5}h{activos_dist}H"
            valores_raw = struct.unpack(formato_clon, fragmento_clon_raw)
            offset += total_bytes_clon
            
            # 3. NORMALIZACIÓN SEGMENTADA EXACTA (Rango estricto [-1.0, 1.0])
            vector_clon = np.array(valores_raw, dtype=np.float32)
            
            idx_fin_servos = activos_servos
            idx_fin_imus = activos_servos + (activos_imus * 5)
            
            # Aplicar la normalización por bloques independientes en NumPy
            if activos_servos > 0:
                vector_clon[:idx_fin_servos] = (vector_clon[:idx_fin_servos] / 65535.0) * 2.0 - 1.0
            if activos_imus > 0:
                vector_clon[idx_fin_servos:idx_fin_imus] = vector_clon[idx_fin_servos:idx_fin_imus] / 32767.0
            if activos_dist > 0:
                vector_clon[idx_fin_imus:] = (vector_clon[idx_fin_imus:] / 65535.0) * 2.0 - 1.0
            
            lista_estados_ia.append(vector_clon)
            
            # Mostrar la disección interna de este clon en la consola
            print(f"   ──> ENTORNO [ID_{clon_id:02d}]")
            print(f"       HEX del Clon:         {fragmento_clon_raw.hex().upper()[:60]}...")
            print(f"       Enteros Extraídos:    {list(valores_raw[:8])}...")
            print(f"       Vector IA Normalizado: {np.round(vector_clon[:8], 4)}...")
        
        # 4. MATRIZ FINAL DE OBSERVACIONES DESTINO GPU
        matriz_observaciones = np.array(lista_estados_ia, dtype=np.float32)
        
        print("-" * 95)
        print(f"📤 [SALIDA HACIA LA IA/GPU] Matriz Unificada de Observaciones:")
        print(f"   Dimensiones Tensor: {matriz_observaciones.shape} (Clones × Variables)")
        print(f"   Contenido Indexado (Primer clon):")
        print(f"   {matriz_observaciones[0]}")
        print("="*95)

except KeyboardInterrupt:
    print("\n[SISTEMA] Servidor apagado correctamente.")
finally:
    sock.close()
