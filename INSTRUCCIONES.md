# 📋 FANAR — Sistema de Registro de Placas
## Instrucciones de Instalación y Uso

---

## ✅ REQUISITOS
- Python 3.8 o superior instalado en el PC de Recepción
- Los 3 PCs conectados a la misma red LAN (WiFi o cable)

---

## 🚀 INSTALACIÓN (solo una vez, en el PC de Recepción)

### Paso 1 — Instalar librerías
Abre una consola (CMD o Terminal) y ejecuta:
```
pip install flask openpyxl
```

### Paso 2 — Copiar la carpeta
Copia la carpeta `fanar/` donde quieras, por ejemplo:
```
C:\fanar\
```

### Paso 3 — Iniciar el sistema
En la consola, ve a la carpeta y ejecuta:
```
cd C:\fanar
python app.py
```

Verás algo como:
```
✅ Sistema FANAR iniciado
📡 Abre en este PC:        http://localhost:5000
📡 Desde otros PC en red:  http://192.168.1.X:5000
```

---

## 💻 CÓMO ACCEDER DESDE CADA PC

| PC | ¿Cómo accede? |
|----|---------------|
| **Recepción** (donde corre el servidor) | Abrir Chrome → `http://localhost:5000` |
| **PC Motocicletas** | Abrir Chrome → `http://192.168.1.X:5000` |
| **PC Vehículos** | Abrir Chrome → `http://192.168.1.X:5000` |

> 💡 **Nota:** Reemplaza `192.168.1.X` con la IP real del PC de Recepción.
> Para ver la IP: en CMD escribe `ipconfig` y busca "Dirección IPv4".

---

## 📖 USO DEL SISTEMA

### Registrar una placa
1. En Recepción, selecciona la pestaña **Motocicletas** o **Vehículos**
2. Llena el formulario (la Placa es obligatoria)
3. Clic en **REGISTRAR**
4. ⚠️ Si la placa ya existe en el periodo, el sistema avisa automáticamente

### Ver registros en tiempo real
- Los PC del fondo actualizan la tabla automáticamente cada 20 segundos
- También pueden buscar por placa, cliente o cédula en el buscador

### Exportar a Excel
- Clic en el botón **Excel** para descargar los registros del periodo seleccionado
- El archivo se guarda en la carpeta `exports/` y también se descarga

### Reiniciar al inicio del mes
1. Exporta primero los datos (botón Excel) si lo deseas
2. Clic en **Reiniciar**
3. Confirma la acción
4. Los registros se archivan internamente (no se pierden) y se borra la pantalla
5. Puedes consultar meses anteriores desde el selector de periodo

---

## 🗂 ESTRUCTURA DE ARCHIVOS

```
fanar/
├── app.py              ← Servidor principal (NO modificar)
├── requirements.txt    ← Librerías necesarias
├── fanar.db            ← Base de datos (se crea automáticamente)
├── templates/
│   └── index.html      ← Interfaz web
└── exports/            ← Aquí se guardan los Excel exportados
```

---

## ❓ SOLUCIÓN DE PROBLEMAS

**No puedo acceder desde otro PC:**
- Verifica que todos estén en la misma red
- Desactiva temporalmente el Firewall de Windows en el PC servidor
- Confirma la IP con `ipconfig`

**Se me cerró la consola y el sistema no responde:**
- Vuelve a ejecutar `python app.py` en la carpeta `fanar/`
- Los datos NO se pierden (están en `fanar.db`)

**Quiero que inicie automáticamente con Windows:**
- Crea un archivo `iniciar_fanar.bat` con el contenido:
  ```
  cd C:\fanar
  python app.py
  ```
- Colócalo en la carpeta de Inicio de Windows

---

## 📞 Soporte
Sistema desarrollado como asesoría para **FANAR**.
Datos almacenados localmente — sin internet requerido.
