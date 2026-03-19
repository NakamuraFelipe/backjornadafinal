# back_end/usuario_dao_postgres.py
import traceback
from database import get_db_connection  # deve retornar psycopg3 connection
from models.usuario_logado import UsuarioLogado

class UsuarioDAO:

    @staticmethod
    def create_usuario(usuario):
        """Cria o usuário no banco"""
        if not all([usuario.nome_usuario, usuario.cargo, usuario.senha_hash, usuario.id_supervisor]):
            raise ValueError(
                "Campos obrigatórios do usuário estão vazios.",
                usuario.nome_usuario, usuario.cargo, usuario.senha_hash, usuario.id_supervisor
            )

        try:
            # Context manager abre e fecha conexão automaticamente
            with get_db_connection() as conn:
                # Cursor com dict_row para retornar dicts
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO usuario (nome_usuario, cargo, email,
                                             telefone, foto, senha_hash, id_supervisor)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id_usuario
                    """
                    values = (
                        usuario.nome_usuario,
                        usuario.cargo,
                        usuario.email,
                        usuario.telefone,
                        usuario.foto,
                        usuario.senha_hash,
                        usuario.id_supervisor
                    )
                    print("Valores para insert usuario:", values)

                    cur.execute(query, values)
                    inserted_id = cur.fetchone()['id_usuario']
                    conn.commit()
                    print(f"Usuário inserido com sucesso -> id_usuario={inserted_id}")

                    return inserted_id

        except Exception as e:
            print("Erro em create_usuario:", e)
            traceback.print_exc()
            raise e

    @staticmethod
    def get_usuarios_geridos(id_supervisor):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        SELECT *
                        FROM usuario
                        WHERE id_supervisor = %s
                    """
                    cur.execute(query, (id_supervisor,))
                    results = cur.fetchall()
                    return results
        except Exception as e:
            print("Erro em get_usuarios_geridos:", e)
            traceback.print_exc()
            raise e