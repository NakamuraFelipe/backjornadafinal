# back_end/lead_dao_postgres.py
import traceback
from database import get_db_connection
from models.lead_model import Lead, Address


class LeadDAO:

    @staticmethod
    def create_localizacao(endereco: Address):
        print("=== Iniciando create_localizacao ===")
        print("Dados do endereço recebidos:", vars(endereco))

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:

                    # --- País ---
                    cur.execute("SELECT id_pais FROM pais WHERE nome_pais=%s", (endereco.pais,))
                    pais = cur.fetchone()
                    if pais:
                        id_pais = pais['id_pais']
                        print(f"[LOG] País já existe: {endereco.pais} -> id_pais={id_pais}")
                    else:
                        cur.execute(
                            "INSERT INTO pais (nome_pais) VALUES (%s) RETURNING id_pais",
                            (endereco.pais,)
                        )
                        id_pais = cur.fetchone()['id_pais']
                        print(f"[LOG] País inserido: {endereco.pais} -> id_pais={id_pais}")

                    # --- Estado ---
                    cur.execute(
                        "SELECT id_estado FROM estado WHERE nome_estado=%s AND id_pais=%s",
                        (endereco.estado, id_pais)
                    )
                    estado = cur.fetchone()
                    if estado:
                        id_estado = estado['id_estado']
                        print(f"[LOG] Estado já existe: {endereco.estado} -> id_estado={id_estado}")
                    else:
                        cur.execute(
                            "INSERT INTO estado (nome_estado, uf, id_pais) VALUES (%s, %s, %s) RETURNING id_estado",
                            (endereco.estado, endereco.estado[:2].upper(), id_pais)
                        )
                        id_estado = cur.fetchone()['id_estado']
                        print(f"[LOG] Estado inserido: {endereco.estado} -> id_estado={id_estado}")

                    # --- Cidade ---
                    cur.execute(
                        "SELECT id_cidade FROM cidade WHERE nome_cidade=%s AND id_estado=%s",
                        (endereco.cidade, id_estado)
                    )
                    cidade = cur.fetchone()
                    if cidade:
                        id_cidade = cidade['id_cidade']
                        print(f"[LOG] Cidade já existe: {endereco.cidade} -> id_cidade={id_cidade}")
                    else:
                        cur.execute(
                            "INSERT INTO cidade (nome_cidade, id_estado) VALUES (%s, %s) RETURNING id_cidade",
                            (endereco.cidade, id_estado)
                        )
                        id_cidade = cur.fetchone()['id_cidade']
                        print(f"[LOG] Cidade inserida: {endereco.cidade} -> id_cidade={id_cidade}")

                    # --- Bairro ---
                    cur.execute("SELECT id_bairro, id_cidade FROM bairro WHERE nome_bairro=%s", (endereco.bairro,))
                    bairros = cur.fetchall()
                    id_bairro = None
                    for b in bairros:
                        cur.execute("SELECT nome_cidade FROM cidade WHERE id_cidade=%s", (b['id_cidade'],))
                        nome_cidade = cur.fetchone()['nome_cidade']
                        if nome_cidade == endereco.cidade:
                            id_bairro = b['id_bairro']
                            print(f"[LOG] Bairro já existe na cidade: {endereco.bairro} -> id_bairro={id_bairro}")
                            break
                    if not id_bairro:
                        cur.execute(
                            "INSERT INTO bairro (nome_bairro, id_cidade) VALUES (%s, %s) RETURNING id_bairro",
                            (endereco.bairro, id_cidade)
                        )
                        id_bairro = cur.fetchone()['id_bairro']
                        print(f"[LOG] Bairro inserido: {endereco.bairro} -> id_bairro={id_bairro}")

                    # --- Rua ---
                    cur.execute("SELECT id_rua, id_bairro FROM rua WHERE nome_rua=%s", (endereco.rua,))
                    ruas = cur.fetchall()
                    id_rua = None
                    for r in ruas:
                        cur.execute("SELECT nome_bairro FROM bairro WHERE id_bairro=%s", (r['id_bairro'],))
                        nome_bairro = cur.fetchone()['nome_bairro']
                        if nome_bairro == endereco.bairro:
                            id_rua = r['id_rua']
                            print(f"[LOG] Rua já existe no bairro: {endereco.rua} -> id_rua={id_rua}")
                            break
                    if not id_rua:
                        cur.execute(
                            "INSERT INTO rua (nome_rua, id_bairro) VALUES (%s, %s) RETURNING id_rua",
                            (endereco.rua, id_bairro)
                        )
                        id_rua = cur.fetchone()['id_rua']
                        print(f"[LOG] Rua inserida: {endereco.rua} -> id_rua={id_rua}")

                    # --- Localizacao ---
                    cur.execute(
                        "SELECT id_localizacao FROM localizacao WHERE cep=%s AND numero=%s AND complemento=%s AND id_rua=%s",
                        (endereco.cep, endereco.numero, endereco.complemento, id_rua)
                    )
                    local = cur.fetchone()
                    if local:
                        id_localizacao = local['id_localizacao']
                        print(f"[LOG] Localizacao já existe -> id_localizacao={id_localizacao}")
                    else:
                        cur.execute(
                            "INSERT INTO localizacao (cep, numero, complemento, id_rua) VALUES (%s, %s, %s, %s) RETURNING id_localizacao",
                            (endereco.cep, endereco.numero, endereco.complemento, id_rua)
                        )
                        id_localizacao = cur.fetchone()['id_localizacao']
                        print(f"[LOG] Localizacao inserida -> id_localizacao={id_localizacao}")

                    conn.commit()
                    print("=== create_localizacao finalizado ===")
                    return id_localizacao

        except Exception as e:
            print("[ERRO] create_localizacao:", e)
            traceback.print_exc()
            raise e

    @staticmethod
    def create_lead(lead: Lead):
        """Cria o lead no banco"""
        if not all([lead.nome_local, lead.responsavel, lead.telefone, lead.estado_leads, lead.id_usuario]):
            raise ValueError(
                "Campos obrigatórios do lead estão vazios.",
                lead.nome_local, lead.responsavel, lead.telefone, lead.estado_leads, lead.id_usuario
            )

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO leads (nome_local, nome_responsavel, id_localizacao,
                                           id_usuario, valor_proposta, categoria_venda, observacao, estado_leads)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id_lead
                    """
                    values = (
                        lead.nome_local,
                        lead.responsavel,
                        lead.id_localizacao,
                        lead.id_usuario,
                        lead.valor,
                        lead.categoria_venda,
                        lead.observacao,
                        lead.estado_leads
                    )
                    cur.execute(query, values)
                    inserted_id = cur.fetchone()['id_lead']
                    print(f"Lead inserido com sucesso -> id_lead={inserted_id}")

                    # Inserir telefone na tabela telefone
                    if lead.telefone:
                        tel_query = """
                            INSERT INTO telefone (id_leads, telefone)
                            VALUES (%s, %s)
                        """
                        cur.execute(tel_query, (inserted_id, lead.telefone))
                        print(f"Telefone inserido com sucesso -> {lead.telefone}")

                    conn.commit()
                    return inserted_id

        except Exception as e:
            print("Erro em create_lead:", e)
            traceback.print_exc()
            raise e

    @staticmethod
    def get_all():
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM leads")
                    results = cur.fetchall()
                    return results
        except Exception as e:
            print("Erro em get_all:", e)
            traceback.print_exc()
            raise e