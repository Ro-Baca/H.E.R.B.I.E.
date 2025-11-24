# prueba_total.py
# Script de prueba interactivo para TODOS los actuadores de HERBIE (Luz y Sonido).

import utime
import hrb_config as config
import hrb_actuators as actuators

# --- Funciones de Ayuda ---

def run(state_name):
    """
    Ejecuta un estado completo (luz y sonido) por su nombre.
    Espera un string, ej: run("DRY")
    """
    # Convierte a mayúsculas para no ser sensible a may/min
    state_name = state_name.upper()
    
    if state_name in actuators.state_map:
        print(f"\n--- Ejecutando estado: {state_name} ---")
        actuators.state_map[state_name]()
    else:
        print(f"\n--- ERROR: Estado '{state_name}' no encontrado. ---")
        print("Estados disponibles:")
        # Imprime una lista de todos los nombres de estado válidos
        for key in actuators.state_map.keys():
            print(f"- {key}")

def off():
    """Función de emergencia para apagar todo."""
    print("Apagando actuadores...")
    actuators.no_tone()
    actuators.led_turn_off()

# --- Bloque Principal de Prueba ---

# 1. Inicializa el hardware
actuators.init_actuators()
print("Actuadores inicializados.")

# 2. Ejecuta la secuencia de arranque para confirmar
run("STARTUP")
utime.sleep(1)

# 3. Imprime el menú de ayuda en la consola REPL
print("=" * 40)
print("🤖 MENÚ DE PRUEBA DE ESTADOS DE HERBIE 🤖")
print("Usa la función run('ESTADO') para probar:")
print("-" * 40)
print("  run('OK')")
print("  run('DRY')")
print("  run('HOT')")
print("  run('COLD')")
print("  run('SAD')")
print("  run('TIRED')")
print("  run('DEAD')")
print("  run('THANKS')")
print("  run('STARTUP')")
print("  run('SHUTDOWN')")
print("-" * 40)
print("Para apagar todo en caso de error:")
print("  off()")
print("=" * 40)

# El script termina, la consola REPL (>>>) está lista.