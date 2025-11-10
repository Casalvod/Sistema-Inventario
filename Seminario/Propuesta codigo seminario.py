import csv
import os
from datetime import datetime

# Archivos CSV
ARCHIVO_INVENTARIO = 'inventario.csv'
ARCHIVO_MOVIMIENTOS = 'movimientos.csv'

# --- Cargar inventario existente ---
def cargar_inventario():
    inventario = {}
    if os.path.exists(ARCHIVO_INVENTARIO):
        with open(ARCHIVO_INVENTARIO, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for fila in reader:
                codigo = fila['codigo']
                inventario[codigo] = {
                    'nombre': fila['nombre'],
                    'cantidad': int(fila['cantidad']),
                    'precio': float(fila.get('precio', 0.0))
                }
    return inventario

# --- Guardar inventario ordenado alfabéticamente ---
def guardar_inventario(inventario):
    inventario_ordenado = dict(sorted(inventario.items(), key=lambda x: x[1]['nombre'].lower()))
    with open(ARCHIVO_INVENTARIO, 'w', newline='', encoding='utf-8') as csvfile:
        campos = ['codigo', 'nombre', 'cantidad', 'precio']
        writer = csv.DictWriter(csvfile, fieldnames=campos)
        writer.writeheader()
        for codigo, datos in inventario_ordenado.items():
            writer.writerow({
                'codigo': codigo,
                'nombre': datos['nombre'],
                'cantidad': datos['cantidad'],
                'precio': datos['precio']
            })
    return inventario_ordenado

# --- Registrar movimientos en bitácora ---
def registrar_movimiento(tipo, codigo, nombre, cantidad, observacion=""):
    with open(ARCHIVO_MOVIMIENTOS, 'a', newline='', encoding='utf-8') as csvfile:
        campos = ['fecha', 'tipo', 'codigo', 'nombre', 'cantidad', 'observacion']
        writer = csv.DictWriter(csvfile, fieldnames=campos)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow({
            'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'tipo': tipo,
            'codigo': codigo,
            'nombre': nombre,
            'cantidad': cantidad,
            'observacion': observacion
        })

# --- Mostrar inventario ---
def mostrar_inventario(inventario):
    if not inventario:
        print("\nEl inventario está vacío.\n")
        return
    print("\n=== INVENTARIO ACTUAL ===")
    print(f"{'CÓDIGO':<10} {'PRODUCTO':<25} {'CANTIDAD':<10} {'PRECIO ($)':<10}")
    print("-" * 60)
    for codigo, datos in sorted(inventario.items(), key=lambda x: x[1]['nombre'].lower()):
        print(f"{codigo:<10} {datos['nombre']:<25} {datos['cantidad']:<10} {datos['precio']:<10.2f}")
    print()

# --- Buscar producto ---
def buscar_producto(inventario):
    termino = input("Ingrese nombre o código del producto a buscar: ").strip().lower()
    encontrados = {c: d for c, d in inventario.items() if termino in d['nombre'].lower() or termino in c.lower()}

    if not encontrados:
        print("No se encontraron coincidencias.")
        return
    print("\n=== RESULTADOS DE BÚSQUEDA ===")
    for codigo, datos in encontrados.items():
        print(f"Código: {codigo} | Producto: {datos['nombre']} | Cantidad: {datos['cantidad']} | Precio: ${datos['precio']:.2f}")

# --- Agregar nuevo producto ---
def agregar_producto(inventario):
    codigo = input("Ingrese el código del producto: ").strip()
    if codigo in inventario:
        print(f"\n❌ Error: Ya existe un producto con el código '{codigo}'.")
        mostrar_inventario(inventario)
        return

    nombre = input("Ingrese el nombre del producto: ").strip()
    try:
        cantidad = int(input("Ingrese la cantidad inicial: "))
        if cantidad < 0:
            print("❌ La cantidad no puede ser negativa.")
            return
        precio = float(input("Ingrese el precio del producto: "))
    except ValueError:
        print("❌ Entrada inválida. Asegúrese de ingresar valores numéricos.")
        return

    inventario[codigo] = {'nombre': nombre, 'cantidad': cantidad, 'precio': precio}
    inventario = guardar_inventario(inventario)
    registrar_movimiento("Ingreso", codigo, nombre, cantidad, "Nuevo producto registrado")
    print(f"✅ Producto '{nombre}' agregado correctamente.")
    mostrar_inventario(inventario)

# --- Actualizar cantidad de producto existente ---
def actualizar_producto(inventario):
    if not inventario:
        print("\nNo hay productos registrados.\n")
        return

    mostrar_inventario(inventario)
    termino = input("Ingrese el código o nombre del producto a actualizar: ").strip().lower()

    # Buscar coincidencias por código o nombre
    coincidencias = {c: d for c, d in inventario.items() if termino == c.lower() or termino in d['nombre'].lower()}

    if not coincidencias:
        print("❌ No se encontró ningún producto que coincida con la búsqueda.")
        return

    # Si hay más de una coincidencia, pedir al usuario que elija
    if len(coincidencias) > 1:
        print("\nSe encontraron varios productos con ese nombre:")
        for i, (codigo, datos) in enumerate(coincidencias.items(), start=1):
            print(f"{i}. {datos['nombre']} (Código: {codigo}) | Cantidad: {datos['cantidad']}")
        try:
            eleccion = int(input("Seleccione el número del producto que desea actualizar: "))
            if eleccion < 1 or eleccion > len(coincidencias):
                print("Opción inválida.")
                return
            codigo = list(coincidencias.keys())[eleccion - 1]
        except ValueError:
            print("Entrada inválida.")
            return
    else:
        codigo = next(iter(coincidencias))

    producto = inventario[codigo]
    print(f"\nProducto seleccionado: {producto['nombre']} (Código: {codigo})")
    print(f"Cantidad actual: {producto['cantidad']} unidades")

    # Solicitar cambio en cantidad
    try:
        cambio = int(input("Ingrese cuántos productos desea sumar (negativo para restar): "))
    except ValueError:
        print("❌ Entrada inválida. Debe ingresar un número entero.")
        return

    nueva_cantidad = producto['cantidad'] + cambio
    if nueva_cantidad < 0:
        print("❌ No puede quedar stock negativo.")
        return

    # Actualizar e informar
    inventario[codigo]['cantidad'] = nueva_cantidad
    inventario = guardar_inventario(inventario)
    tipo = "Ingreso" if cambio >= 0 else "Salida"
    registrar_movimiento(tipo, codigo, producto['nombre'], cambio, "Actualización manual")

    print(f"✅ Stock actualizado: '{producto['nombre']}' ahora tiene {nueva_cantidad} unidades.")

# --- Registrar venta ---
def registrar_venta(inventario):
    codigo = input("Ingrese el código del producto vendido: ").strip()
    if codigo not in inventario:
        print("❌ El producto no existe en el inventario.")
        return

    try:
        cantidad_vendida = int(input("Ingrese cantidad vendida: "))
    except ValueError:
        print("❌ Cantidad inválida.")
        return

    if cantidad_vendida <= 0 or cantidad_vendida > inventario[codigo]['cantidad']:
        print("❌ Cantidad fuera de rango. Verifique el stock.")
        return

    inventario[codigo]['cantidad'] -= cantidad_vendida
    inventario = guardar_inventario(inventario)
    registrar_movimiento("Venta", codigo, inventario[codigo]['nombre'], -cantidad_vendida, "Venta registrada")
    print(f"✅ Venta registrada. Se descontaron {cantidad_vendida} unidades de '{inventario[codigo]['nombre']}'.")

# --- Reporte de productos con bajo stock ---
def reporte_bajo_stock(inventario, limite=15):
    print(f"\n=== PRODUCTOS CON STOCK MENOR O IGUAL A {limite} ===")
    bajos = [d for d in inventario.values() if d['cantidad'] <= limite]
    if not bajos:
        print("No hay productos con bajo stock.")
        return
    for codigo, datos in inventario.items():
        if datos['cantidad'] <= limite:
            print(f"⚠️  {datos['nombre']} ({codigo}) - Cantidad: {datos['cantidad']}")

# --- Menú principal ---
def menu():
    inventario = cargar_inventario()
    while True:
        print("\n=== SISTEMA DE INVENTARIO - Minimarket ===")
        print("1. Agregar nuevo producto")
        print("2. Actualizar stock existente")
        print("3. Registrar venta")
        print("4. Buscar producto")
        print("5. Mostrar inventario")
        print("6. Reporte de bajo stock")
        print("7. Salir")

        opcion = input("Seleccione una opción: ").strip()
        if opcion == '1':
            agregar_producto(inventario)
        elif opcion == '2':
            actualizar_producto(inventario)
        elif opcion == '3':
            registrar_venta(inventario)
        elif opcion == '4':
            buscar_producto(inventario)
        elif opcion == '5':
            mostrar_inventario(inventario)
        elif opcion == '6':
            reporte_bajo_stock(inventario)
        elif opcion == '7':
            print("\nGuardando inventario y cerrando sistema...")
            guardar_inventario(inventario)
            break
        else:
            print("❌ Opción no válida, intente nuevamente.")

# --- Ejecución principal ---
if __name__ == "__main__":
    menu()
