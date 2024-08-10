import asyncio
from bleak import BleakClient, BleakError

# Endereço do dispositivo BLE
DEVICE_ADDRESS = "22:34:50:10:7b:fc"

# UUID da characteristic que queremos monitorar
CHARACTERISTIC_UUID = "0000ffe2-0000-1000-8000-00805f9b34fb"

# Valores que indicam os diferentes estados do dispositivo
DEVICE_STATE_STARTED = bytearray(b'\xaa\x05\xa2\x00\xfe')
DEVICE_STATE_WAITING = bytearray(b'\xaa\x05\xa3\x00\xfe')
DEVICE_STATE_READY = bytearray(b'\xaa\x05\xa4\x00\xfe')
DEVICE_STATE_BLOW = bytearray(b'\xaa\x05\xa5\x00\xfe')

def convert_to_mg_l(data):
    if len(data) < 9 or data[0:2] != b'\xaa\t':
        print("Formato de dados inválido ou incompleto.")
        return None

    # Extrai os 4 bytes relevantes para a leitura (índices 3 a 6)
    reading_bytes = data[2:6]

    # Converte os bytes em uma string hexadecimal, depois em um inteiro
    reading_hex = ''.join(f'{byte:02x}' for byte in reading_bytes)
    reading_int = int(reading_hex, 16)

    # Converte o valor inteiro para mg/L (dividido por 1000.0 para obter o valor correto)
    reading_mg_l = reading_int / 1000.0

    return reading_mg_l

# Função para ser chamada quando a characteristic mudar
def notification_handler(sender, data):
    data_bytes = bytearray(data)

    if data_bytes == DEVICE_STATE_STARTED:
        print("O dispositivo foi ligado.")
    elif data_bytes == DEVICE_STATE_WAITING:
        print("Aguarde até utilizar o dispositivo.")
    elif data_bytes == DEVICE_STATE_READY:
        print("O dispositivo está pronto.")
    elif data_bytes == DEVICE_STATE_BLOW:
        print("dispositivo sendo utilizado.")
    else:
        reading = convert_to_mg_l(data_bytes)
        if reading is not None:
            print(f"Leitura de álcool: {reading} mg/L")

async def connect_and_monitor():
    while True:
        try:
            async with BleakClient(DEVICE_ADDRESS) as client:
                # Verifique se está conectado ao dispositivo
                if client.is_connected:
                    print(f"Conectado ao dispositivo {DEVICE_ADDRESS}")

                    # Habilitar notificações para a characteristic desejada
                    await client.start_notify(CHARACTERISTIC_UUID, notification_handler)

                    print("bafômetro conectado...")

                    try:
                        # Continuar executando indefinidamente
                        while True:
                            await asyncio.sleep(1)
                    except KeyboardInterrupt:
                        print("Encerrando monitoramento...")
                        break
                    finally:
                        # Parar notificações quando o programa for encerrado
                        await client.stop_notify(CHARACTERISTIC_UUID)
                else:
                    print("Falha na conexão. Tentando novamente...")
        except BleakError as e:
            print(f"Erro ao tentar se conectar: {e}. Tentando novamente em 5 segundos...")
            await asyncio.sleep(5)  # Aguarda 5 segundos antes de tentar novamente

async def main():
    await connect_and_monitor()

# Iniciar o loop do asyncio
asyncio.run(main())
