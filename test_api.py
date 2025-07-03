import requests
import json

# URL base de la API
BASE_URL = "http://localhost:8000"

def test_api():
    """Función para probar todos los endpoints de la API"""
    
    print("=== Probando API de Transacciones MongoDB ===\n")
    
    # 1. Probar endpoint raíz
    print("1. Probando endpoint raíz...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    # 2. Crear una transacción
    print("2. Creando una transacción...")
    nueva_transaccion = {
        "descripcion": "Salario mensual",
        "monto": 2500.00,
        "tipo": "ingreso",
        "categoria": "Trabajo"
    }
    
    response = requests.post(
        f"{BASE_URL}/transacciones",
        json=nueva_transaccion,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        transaccion_creada = response.json()
        print(f"Transacción creada: {json.dumps(transaccion_creada, indent=2)}")
        transaccion_id = transaccion_creada["id"]
    else:
        print(f"Error: {response.text}")
        return
    print()
    
    # 3. Crear otra transacción
    print("3. Creando otra transacción...")
    otra_transaccion = {
        "descripcion": "Compra de víveres",
        "monto": 150.50,
        "tipo": "gasto",
        "categoria": "Alimentación"
    }
    
    response = requests.post(
        f"{BASE_URL}/transacciones",
        json=otra_transaccion,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Segunda transacción creada: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    print()
    
    # 4. Obtener todas las transacciones
    print("4. Obteniendo todas las transacciones...")
    response = requests.get(f"{BASE_URL}/transacciones")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        transacciones = response.json()
        print(f"Total de transacciones: {len(transacciones)}")
        for trans in transacciones:
            print(f"- {trans['descripcion']}: ${trans['monto']} ({trans['tipo']})")
    else:
        print(f"Error: {response.text}")
    print()
    
    # 5. Obtener transacción específica
    print("5. Obteniendo transacción específica...")
    response = requests.get(f"{BASE_URL}/transacciones/{transaccion_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Transacción encontrada: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    print()
    
    # 6. Actualizar transacción
    print("6. Actualizando transacción...")
    actualizacion = {
        "descripcion": "Salario mensual actualizado",
        "monto": 2600.00,
        "tipo": "ingreso",
        "categoria": "Trabajo"
    }
    
    response = requests.put(
        f"{BASE_URL}/transacciones/{transaccion_id}",
        json=actualizacion,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Transacción actualizada: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    print()
    
    # 7. Obtener transacciones por tipo
    print("7. Obteniendo transacciones por tipo (ingreso)...")
    response = requests.get(f"{BASE_URL}/transacciones/tipo/ingreso")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        ingresos = response.json()
        print(f"Total de ingresos: {len(ingresos)}")
        for ingreso in ingresos:
            print(f"- {ingreso['descripcion']}: ${ingreso['monto']}")
    else:
        print(f"Error: {response.text}")
    print()
    
    print("8. Obteniendo transacciones por tipo (gasto)...")
    response = requests.get(f"{BASE_URL}/transacciones/tipo/gasto")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        gastos = response.json()
        print(f"Total de gastos: {len(gastos)}")
        for gasto in gastos:
            print(f"- {gasto['descripcion']}: ${gasto['monto']}")
    else:
        print(f"Error: {response.text}")
    print()
    
    # 9. Eliminar transacción (opcional - comentado para no eliminar datos de prueba)
    print("9. Eliminando transacción (comentado para preservar datos de prueba)...")
    # response = requests.delete(f"{BASE_URL}/transacciones/{transaccion_id}")
    # print(f"Status: {response.status_code}")
    # if response.status_code == 200:
    #     print(f"Transacción eliminada: {response.json()}")
    # else:
    #     print(f"Error: {response.text}")
    print("Operación de eliminación comentada para preservar datos de prueba")
    
    print("\n=== Pruebas completadas ===")

if __name__ == "__main__":
    test_api() 