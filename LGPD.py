import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, DateTime, insert, text
from datetime import datetime

import time
from functools import wraps
def medir_tempo(func):
    """Decorator que mede o tempo de execução de uma função."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()  # tempo inicial (mais preciso que time.time)
        resultado = func(*args, **kwargs)
        fim = time.perf_counter()     # tempo final
        duracao = fim - inicio
        print(f"⏱ Função '{func.__name__}' executada em {duracao:.6f} segundos.")
        return resultado
    return wrapper

engine = create_engine("postgresql+psycopg://alunos:AlunoFatec@200.19.224.150:5432/atividade2", echo=False)
metadata = MetaData()

usuarios = Table(
    'usuarios', metadata,
    Column('id', Integer, primary_key=True),
    Column('nome', String(50), nullable=False, index=True),
    Column('cpf', String(14), nullable=False),
    Column('email', String(100), nullable=False, unique=True),
    Column('telefone', String(20), nullable=False),
    Column('data_nascimento', Date, nullable=False),
    Column('created_on', DateTime(), default=datetime.now),
    Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now)
)

metadata.create_all(engine)

@medir_tempo
def LGPD(row):
    # Transforma a linha em uma lista mutável para podermos alterar os campos
    dados = list(row)
    
    # 1. Anonimizar o Nome (mantém a 1ª letra e troca o restante por '*')
    nome = dados[1]
    partes_nome = nome.split()
    nome_anonimizado = []
    for parte in partes_nome:
        if len(parte) > 1:
            nome_anonimizado.append(parte[0] + '*' * (len(parte) - 1))
        else:
            nome_anonimizado.append(parte)
    dados[1] = ' '.join(nome_anonimizado)
    
    # 2. Anonimizar o CPF (substitui os últimos caracteres por '*')
    cpf = dados[2] # Ex: '237.615.809-59'
    dados[2] = cpf[:4] + '*** ***-**'
    
    # 3. Anonimizar o E-mail (substitui a parte antes do '@' por '*')
    email = dados[3] # Ex: 'nuneserick@example.com'
    if '@' in email:
        usuario, dominio = email.split('@', 1)
        dados[3] = usuario[0] + '*' * (len(usuario) - 1) + '@' + dominio
        
    # 4. Anonimizar o Telefone (apresenta o final somente)
    telefone = dados[4] # Ex: '+55 (011) 9483-6810'
    # Pega os últimos 4 dígitos ou caracteres limpos do telefone
    telefones_limpos = ''.join(filter(str.isdigit, telefone))
    if len(telefones_limpos) >= 4:
        dados[4] = telefones_limpos[-4:]
        
    return tuple(dados)

# --- LÓGICA DA ATIVIDADE 2 (COLOCAR NO FINAL DO ARQUIVO) ---
todos_dados_anonimizados = []

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM usuarios;"))
    for row in result:
        row_anonimizada = LGPD(row)
        todos_dados_anonimizados.append(row_anonimizada)

colunas = ['id', 'nome', 'cpf', 'email', 'telefone', 'data_nascimento', 'created_on', 'updated_on']
df = pd.DataFrame(todos_dados_anonimizados, columns=colunas)

# Extrai o ano da data de nascimento
df['ano_nascimento'] = pd.to_datetime(df['data_nascimento']).dt.year

# Cria um arquivo CSV para cada ano encontrado
for ano, grupo in df.groupby('ano_nascimento'):
    nome_arquivo = f"{int(ano)}.csv"
    grupo_salvar = grupo.drop(columns=['ano_nascimento'])
    grupo_salvar.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
    print(f"Arquivo gerado com sucesso: {nome_arquivo}")
    # --- LÓGICA DA ATIVIDADE 3: Arquivo único sem anonimização (Nome e CPF) ---
dados_completos = []

with engine.connect() as conn:
    # Consulta selecionando apenas o nome e o cpf de todos os registros
    result = conn.execute(text("SELECT nome, cpf FROM usuarios;"))
    for row in result:
        dados_completos.append(list(row))

# Cria um DataFrame do Pandas com as colunas Nome e CPF
colunas_todos = ['nome', 'cpf']
df_todos = pd.DataFrame(dados_completos, columns=colunas_todos)

# Salva em um arquivo único consolidado
nome_arquivo_todos = "todos.csv"  # Pode ser .xls se preferir o formato do Excel
df_todos.to_csv(nome_arquivo_todos, index=False, encoding='utf-8-sig')
print(f"Arquivo consolidado gerado com sucesso: {nome_arquivo_todos}")