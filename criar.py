from database import get_db_connection
from passlib.hash import argon2

def criar_usuario_teste():
    # Dados do usuário
    nome = "Usuário Teste"
    cargo = "gestor"
    email = "teste@teste.com"
    telefone = "11999999999"
    senha = "1234"

    # Hash da senha
    senha_hash = argon2.hash(senha)

    try:
        # Usando context manager para fechar conexão e cursor automaticamente
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = """
                INSERT INTO usuario (nome_usuario, cargo, email, telefone, senha_hash)
                VALUES (%s, %s, %s, %s, %s)
                """
                cur.execute(query, (nome, cargo, email, telefone, senha_hash))
                conn.commit()  # necessário em psycopg3

        print("✅ Usuário criado com sucesso!")
        print(f"Email: {email}")
        print(f"Senha: {senha}")

    except Exception as e:
        print("❌ Erro ao criar usuário:", e)


if __name__ == "__main__":
    criar_usuario_teste()