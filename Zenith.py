import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pickle
import os
from torch.optim.lr_scheduler import ReduceLROnPlateau
import joblib
from logger_config import get_logger
logger = get_logger("ZenithServer")

# Configuración de semilla para reproducibilidad
torch.manual_seed(42)
np.random.seed(42)

class Zenith(nn.Module):
    def __init__(self, n_entradas, n_salidas=15):
        super(Zenith, self).__init__()
        
        # Capa de entrada
        self.capa_entrada = nn.Linear(n_entradas, 64)
        self.bn1 = nn.BatchNorm1d(64)
        
        # Bloques residuales corregidos
        self.bloque1 = nn.Sequential(
            nn.Linear(64, 64), nn.BatchNorm1d(64), nn.SELU(), nn.Dropout(0.2),
            nn.Linear(64, 64), nn.BatchNorm1d(64)  # Devuelve a 64 para la conexión residual
        )

        self.bloque2 = nn.Sequential(
            nn.Linear(64, 48), nn.BatchNorm1d(48), nn.SELU(), nn.Dropout(0.3),
            nn.Linear(48, 48), nn.BatchNorm1d(48)
        )

        self.bloque3 = nn.Sequential(
            nn.Linear(48, 32), nn.BatchNorm1d(32), nn.SELU(), nn.Dropout(0.2),
            nn.Linear(32, 32), nn.BatchNorm1d(32)
        )

        # Capa de atención
        self.atencion = nn.Sequential(
            nn.Linear(32, 32), nn.Sigmoid()
        )

        # Capa de salida
        self.capa_salida = nn.Linear(32, n_salidas)
        self.selu = nn.SELU()

    def forward(self, x):
        # Entrada
        x = self.capa_entrada(x)
        x = self.bn1(x)
        x = self.selu(x)

        # Bloque residual 1 (dimensiones corregidas)
        residual = x
        x = self.bloque1(x)
        x = x + residual  # Ahora las dimensiones coinciden
        x = self.selu(x)

        # Bloque residual 2
        x = self.bloque2(x)
        x = self.selu(x)

        # Bloque residual 3
        x = self.bloque3(x)
        x = self.selu(x)

        # Mecanismo de atención
        pesos_atencion = self.atencion(x)
        x = x * pesos_atencion

        # Salida
        x = self.capa_salida(x)
        return x

# Función para cargar y preparar los datos
def cargar_datos(archivo_csv, test_size=0.2, random_state=42):
    print(f"Cargando datos desde {archivo_csv}...")
    
    # Cargar el dataset
    dataset = np.loadtxt(archivo_csv, delimiter=',', skiprows=1)
    
    # Dividir el dataset en entrada (primeros 30 valores) y salida (últimos 15 valores)
    X = dataset[:, :30]  # Las primeras 30 columnas (preferencias + feedback)
    Y = dataset[:, 30:]  # Las últimas 15 columnas (preferencias ajustadas)
    
    # Normalizar los datos de entrada
    escalador = StandardScaler()
    X_escalado = escalador.fit_transform(X)

    joblib.dump(escalador, 'escalador_preferencias.pkl')
    print("Escalador guardado en 'escalador_preferencias.pkl'")
    # Dividir en conjuntos de entrenamiento y prueba
    x_train, x_test, y_train, y_test = train_test_split(
        X_escalado, Y, test_size=test_size, random_state=random_state
    )
    
    print(f"X Train: {x_train.shape}, Y Train: {y_train.shape}, X Test: {x_test.shape}, Y Test: {y_test.shape}")
    
    # Convertir a tensores de PyTorch
    tensor_x_train = torch.from_numpy(x_train).float()
    tensor_x_test = torch.from_numpy(x_test).float()
    tensor_y_train = torch.from_numpy(y_train).float()
    tensor_y_test = torch.from_numpy(y_test).float()
    
    return tensor_x_train, tensor_y_train, tensor_x_test, tensor_y_test, escalador

def cargar_escalador(ruta_archivo='escalador_preferencias.pkl'):
    """Carga el escalador previamente guardado."""
    try:
        escalador = joblib.load(ruta_archivo)
        logger.debug(f"Escalador cargado correctamente desde {ruta_archivo}")
        return escalador
    except Exception as e:
        print(f"Error al cargar el escalador: {str(e)}")
        raise

# Función para entrenar el modelo
def entrenar_modelo(modelo, tensor_x_train, tensor_y_train, tensor_x_test, tensor_y_test, 
                   learning_rate=0.001, epochs=10, batch_size=64, patience=20,
                   estatus_print=100, early_stopping=True, guardar_mejor=True):
    
    # Crear dataloaders para batch training
    train_dataset = TensorDataset(tensor_x_train, tensor_y_train)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    test_dataset = TensorDataset(tensor_x_test, tensor_y_test)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    
    # Definir función de pérdida y optimizador
    funcion_de_perdida = nn.MSELoss()
    optimizer = torch.optim.SGD(
        params=modelo.parameters(),  # Parámetros del modelo
        lr=learning_rate,            # Tasa de aprendizaje
        weight_decay=1e-4            # Regularización L2 (opcional)
    )


    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=patience//2, verbose=True)
    
    # Inicializar variables para early stopping
    mejor_loss = float('inf')
    counter_early_stopping = 0
    mejor_modelo_estado = None
    
    # Historico para seguimiento
    historico = pd.DataFrame()
    
    print(f"Arquitectura del modelo:\n{modelo}")
    print(f"Entrenando modelo por {epochs} épocas...")
    mayor_MAE = 0
    menor_mae = 10
    for epoch in range(1, epochs + 1):
        # Modo entrenamiento
        modelo.train()
        running_loss = 0.0
        
        for batch_x, batch_y in train_loader:
            # Forward pass
            y_predict = modelo(batch_x)
            loss = funcion_de_perdida(y_predict, batch_y)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(modelo.parameters(), max_norm=1.0)
            optimizer.step()
            
            running_loss += loss.item() * batch_x.size(0)
        
        # Calcular loss promedio
        train_loss = running_loss / len(train_loader.dataset)
        
        # Modo evaluación
        modelo.eval()
        val_loss = 0.0
        error_abs = 0.0
        
        with torch.no_grad():
            for batch_x, batch_y in test_loader:
                y_predict = modelo(batch_x)
                val_loss += funcion_de_perdida(y_predict, batch_y).item() * batch_x.size(0)
                error_abs += torch.abs(y_predict - batch_y).mean().item() * batch_x.size(0)
        
        val_loss /= len(test_loader.dataset)
        error_abs /= len(test_loader.dataset)
        
        # Actualizar scheduler
        scheduler.step(val_loss)
        
        # Early stopping check
        if val_loss < mejor_loss:
            mejor_loss = val_loss
            counter_early_stopping = 0
            if guardar_mejor:
                mejor_modelo_estado = modelo.state_dict().copy()
        else:
            counter_early_stopping += 1
        
        # Imprimir estado
        print(f"Epoch: {epoch}/{epochs} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | MAE: {error_abs:.4f}")
        if error_abs > mayor_MAE:
            mayor_MAE = error_abs
            print(f"MAE Más alto en la época: {epoch} \ncon: {error_abs:.4f}")
        if error_abs < menor_mae:
            menor_mae = error_abs
            print(f"MAE Más bajo en la época: {epoch} \ncon: {error_abs:.4f}")
        # Guardar histórico
        df_tmp = pd.DataFrame(data={
            'Epoch': epoch,
            'Train_Loss': round(train_loss, 5),
            'Val_Loss': round(val_loss, 5),
            'Error_Absoluto_Medio': round(error_abs, 4)
        }, index=[0])
        historico = pd.concat(objs=[historico, df_tmp], ignore_index=True, sort=False)
        
        # Early stopping
        if early_stopping and counter_early_stopping >= patience:
            print(f"Early stopping en la época {epoch}")
            break
    
    # Cargar el mejor modelo si se guardó
    if guardar_mejor and mejor_modelo_estado is not None:
        modelo.load_state_dict(mejor_modelo_estado)
        print("Cargado el mejor modelo guardado.")
    print(f"El MAE más bajo: {menor_mae} \n El MAE más alto: {mayor_MAE}")
    return modelo, historico

# Función para visualizar los resultados
def visualizar_resultados(historico, titulo_base="Entrenamiento de Zenith"):
    plt.figure(figsize=(12, 5))
    
    # Gráfico de pérdida
    plt.subplot(1, 2, 1)
    plt.plot(historico['Epoch'], historico['Train_Loss'], label='Train Loss')
    plt.plot(historico['Epoch'], historico['Val_Loss'], label='Validation Loss')
    plt.title(f"{titulo_base} - Pérdida", fontsize=16)
    plt.xlabel("Época", fontsize=12)
    plt.ylabel("Pérdida", fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Gráfico de error absoluto medio
    plt.subplot(1, 2, 2)
    plt.plot(historico['Epoch'], historico['Error_Absoluto_Medio'], label='MAE')
    plt.title(f"{titulo_base} - Error Absoluto Medio", fontsize=16)
    plt.xlabel("Época", fontsize=12)
    plt.ylabel("MAE", fontsize=12)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('entrenamiento_zenith.png')
    plt.show()

# Función para guardar el modelo y escalador
def guardar_modelo(modelo, escalador, directorio='modelos'):
    # Crear directorio si no existe
    if not os.path.exists(directorio):
        os.makedirs(directorio)
    
    # Guardar modelo
    ruta_modelo = os.path.join(directorio, 'modelo_zenith.pt')
    torch.save(modelo.state_dict(), ruta_modelo)
    
    # Guardar escalador
    ruta_escalador = os.path.join(directorio, 'escalador_zenith.pkl')
    with open(ruta_escalador, 'wb') as f:
        pickle.dump(escalador, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print(f"Modelo guardado en {ruta_modelo}")
    print(f"Escalador guardado en {ruta_escalador}")

# Función para cargar el modelo y escalador
def cargar_modelo(n_entradas, n_salidas=15, directorio='modelos'):
    modelo = Zenith(n_entradas, n_salidas)
    
    ruta_modelo = os.path.join(directorio, 'modelo_zenith.pt')
    modelo.load_state_dict(torch.load(ruta_modelo))
    modelo.eval()
    
    ruta_escalador = os.path.join(directorio, 'escalador_zenith.pkl')
    with open(ruta_escalador, 'rb') as f:
        escalador = pickle.load(f)
    
    return modelo, escalador


# Función principal
def main():
    # Configuración
    archivo_csv = 'dataset_preferencias.csv'
    learning_rate = 0.1
    epochs = 100
    batch_size = 64
    patience = 20
    estatus_print = 100
    
    # Cargar datos
    tensor_x_train, tensor_y_train, tensor_x_test, tensor_y_test, escalador = cargar_datos(archivo_csv)
    
    # Crear modelo
    n_entradas = tensor_x_train.shape[1]
    n_salidas = tensor_y_train.shape[1]
    modelo = Zenith(n_entradas, n_salidas)
    
    # Entrenar modelo
    modelo, historico = entrenar_modelo(
        modelo, tensor_x_train, tensor_y_train, tensor_x_test, tensor_y_test,
        learning_rate=learning_rate, epochs=epochs, batch_size=batch_size,
        patience=patience, estatus_print=estatus_print
    )
        # Guardar modelo
    guardar_modelo(modelo, escalador)
    # Visualizar resultados
    visualizar_resultados(historico)

    