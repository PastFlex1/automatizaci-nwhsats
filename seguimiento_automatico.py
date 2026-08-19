import time
from crm_db import obtener_clientes_para_seguimiento, actualizar_estado_cliente, registrar_estadistica

def ejecutar_seguimiento_automatico():
    """
    Simula o ejecuta un seguimiento automático para clientes en estado 'Interesado' o 'Seguimiento'
    que no han sido contactados en las últimas 24 horas.
    """
    print("Iniciando revisión de CRM para seguimientos automáticos...")
    clientes_seguimiento = obtener_clientes_para_seguimiento(horas_inactividad=24)
    
    if not clientes_seguimiento:
        print("No hay clientes pendientes de seguimiento en este momento.")
        return

    print(f"Se encontraron {len(clientes_seguimiento)} clientes para seguimiento.")
    
    for cliente in clientes_seguimiento:
        # En una implementación completa con Playwright, aquí se abriría Messenger y se enviaría un mensaje.
        # Por ahora, simplemente actualizaremos el CRM y simularemos el envío.
        
        mensaje = f"Hola {cliente['nombre']} 👋, queríamos saber si pudiste revisar la información sobre {cliente['interes']}. ¡Tenemos disponibilidad para fabricación esta semana!"
        
        print(f"-> Enviando seguimiento a {cliente['nombre']} (Perfil: {cliente['perfil_fb']})")
        print(f"   Mensaje: {mensaje}")
        
        # Simulamos que se envió el mensaje y el cliente nos deja en visto / en seguimiento
        actualizar_estado_cliente(cliente['id'], "Seguimiento")
        registrar_estadistica("mensajes_recibidos") # Cuenta como interacción de salida/entrada general en stats para este ejemplo
        time.sleep(2)

    print("Revisión de seguimientos completada.")

if __name__ == "__main__":
    ejecutar_seguimiento_automatico()
