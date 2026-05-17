import socket
import struct
import torch
import sys

def inicializar_entorno_amd():
    print("=" * 65)
    print("       VERIFICACIÓN AVANZADA DE TOPOLOGÍA AMD GPU (ROCm/HIP)      ")
    print("=" * 65)
    
    # Validar disponibilidad física del silicio Radeon
    if not torch.cuda.is_available():
        print("[ERR] No se detectó hardware compatible con aceleración HIP/ROCm.")
        sys.exit("[SISTEMA] Abortando inicialización. Revisa los controladores AMD.")

    # 1. Metadatos de Identificación de Hardware
    nombre_gpu = torch.cuda.get_device_name(0)
    id_dispositivo = torch.cuda.current_device()
    propiedades = torch.cuda.get_device_properties(id_dispositivo)
    
    # 2. Métricas de Memoria en Tiempo Real (Conversión de bytes a Gigabytes)
    mem_libre_bytes, mem_total_bytes = torch.cuda.mem_get_info()
    vram_total = mem_total_bytes / (1024 ** 3)
    vram_libre = mem_libre_bytes / (1024 ** 3)
    vram_en_uso = vram_total - vram_libre

    # 3. Datos del Entorno de Ejecución (Backend)
    rocm_version = torch.version.hip if hasattr(torch.version, 'hip') else "HIP Native Bindings"
    arquitectura_sm = f"{propiedades.major}.{propiedades.minor}"

    # Imprimir panel expandido de información de la GPU
    print(f"[HARDWARE] Tarjeta Gráfica : {nombre_gpu}")
    print(f"[HARDWARE] Índice de Unidad: GPU_ID: {id_dispositivo}")
    print(f"[HARDWARE] Capacidad Cómputo: HIP CC {arquitectura_sm} (RDNA Architecture)")
    print("-" * 65)
    print(f"[SOFTWARE] Versión de Python: {sys.version.split()[0]}")
    print(f"[SOFTWARE] PyTorch Backend : ROCm/HIP v{rocm_version}")
    print("-" * 65)
    print(f"[MEMORIA]  VRAM Total      : {vram_total:.2f} GB")
    print(f"[MEMORIA]  VRAM Libre      : {vram_libre:.2f} GB")
    print(f"[MEMORIA]  VRAM Asignada   : {vram_en_uso:.2f} GB")
    print("=" * 65)
    print("[ESTADO] ¡GPU AMD validada para entrenamiento paralelo de IA! 🔥\n")

    return torch.device("cuda")

def iniciar_servidor_receptor(device):
    UDP_IP = "127.0.0.1"
    UDP_PORT = 2026
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    print("-" * 65)
    print(f" Servidor escuchando telemetría binaria en {UDP_IP}:{UDP_PORT}")
    print(" Ejecuta la simulación en Cinema 4D para inyectar datos...")
    print("-" * 65)
    
    try:
        while True:
            # Capturar el datagrama binario de la red
            payload, addr = sock.recvfrom(4096)
            
            # Desempaquetar la cabecera fija de 7 bytes (<HHBBB)
            cabecera_datos = struct.unpack("<HHBBB", payload[:7])
            step, clones, n_servos, n_imus, n_lasers = cabecera_datos
            
            # Carga instantánea de tensores en la GPU AMD RX 9070 XT
            tensor_cabecera = torch.tensor(cabecera_datos, dtype=torch.float32).to(device)
            
            # Métricas dinámicas de uso de memoria interna de PyTorch
            vram_reservada_py = torch.cuda.memory_reserved(0) / (1024 ** 2) # en MB
            
            # Imprimir salida limpia con métricas de la simulación y de la GPU integradas
            print(f"[TELEMETRÍA] Frame: {step:05d} | Entornos Paralelos: {clones}")
            print(f"             └─ Sensores -> Servos: {n_servos} | IMUs: {n_imus} | Láseres: {n_lasers}")
            print(f"[GPU METRICS] Alloc Device: {tensor_cabecera.device} | Caché Reservada PyTorch: {vram_reservada_py:.2f} MB\n")
            
    except KeyboardInterrupt:
        print("\n[SISTEMA] Deteniendo servidor de forma segura...")
    finally:
        sock.close()

if __name__ == "__main__":
    # Inicializar diagnósticos avanzados de la GPU AMD
    target_device = inicializar_entorno_amd()
    
    # Escuchar la tubería de datos de Cinema 4D
    iniciar_servidor_receptor(target_device)
