import time
import logging

# Configuração básica do sistema de logs
logging.basicConfig(
    filename='execucao.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def medir_tempo(func):
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fim = time.time()
        tempo_total = fim - inicio
        
        mensagem = f"⏱ Função '{func.__name__}' executada em {tempo_total:.6f} segundos."
        print(mensagem)
        logging.info(mensagem)
        
        return resultado
    return wrapper