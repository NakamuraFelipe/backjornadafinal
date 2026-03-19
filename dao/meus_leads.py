# back_end/meus_leads_dao_postgres.py
from database import get_db_connection
from models.meus_leads import MeusLeads

class MeusLeadsDAO:

    @staticmethod
    def buscar_leads(query, id_usuario):
        # Transformar query para filtro LIKE
        like = f"%{query}%"
        id_localizacao_filter = int(query) if query.isdigit() else None

        leads = []

        try:
            # Context manager garante fechamento automático de conexão e cursor
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # 1 — Buscar ID(s) da rua pelo nome digitado
                    cur.execute("""
                        SELECT id_rua 
                        FROM rua 
                        WHERE nome_rua LIKE %s
                    """, (like,))
                    ruas = cur.fetchall()
                    id_ruas = [r["id_rua"] for r in ruas]

                    # 2 — Buscar ID(s) da localizacao para essas ruas
                    id_localizacoes = []
                    if id_ruas:
                        placeholders = ','.join(['%s'] * len(id_ruas))
                        cur.execute(
                            f"SELECT id_localizacao FROM localizacao WHERE id_rua IN ({placeholders})",
                            id_ruas
                        )
                        locs = cur.fetchall()
                        id_localizacoes = [l["id_localizacao"] for l in locs]

                    # 3 — Query principal
                    sql_query = """
                    SELECT 
                        l.id_leads,
                        l.nome_local,
                        l.categoria_venda,
                        l.estado_leads,
                        l.id_localizacao,

                        lo.numero,
                        lo.complemento,

                        r.nome_rua,
                        c.nome_cidade,
                        e.uf,

                        l.nome_responsavel,
                        l.observacao,
                        l.valor_proposta,
                        l.data_criacao,

                        l.id_usuario,
                        u.nome_usuario AS nome_consultor,
                        l.ultima_visita
                    FROM leads l
                    INNER JOIN localizacao lo ON lo.id_localizacao = l.id_localizacao
                    INNER JOIN rua r ON r.id_rua = lo.id_rua
                    INNER JOIN bairro b ON b.id_bairro = r.id_bairro
                    INNER JOIN cidade c ON c.id_cidade = b.id_cidade
                    INNER JOIN estado e ON e.id_estado = c.id_estado
                    LEFT JOIN usuario u ON u.id_usuario = l.id_usuario
                    WHERE l.id_usuario = %s
                      AND (
                            l.nome_local LIKE %s
                            OR l.categoria_venda LIKE %s
                            OR l.estado_leads LIKE %s
                            OR (%s IS NOT NULL AND l.id_localizacao = %s)
                         )
                    """

                    cur.execute(sql_query, (
                        id_usuario,
                        like, like, like,
                        id_localizacao_filter, id_localizacao_filter
                    ))

                    rows = cur.fetchall()

                    # Converter rows → OBJETO MeusLeads
                    for row in rows:
                        leads.append(MeusLeads(
                            id_lead=row.get("id_leads"),
                            nome_local=row.get("nome_local"),
                            categoria_venda=row.get("categoria_venda"),
                            estado_leads=row.get("estado_leads"),
                            id_localizacao=row.get("id_localizacao"),

                            nome_rua=row.get("nome_rua"),
                            numero=row.get("numero"),
                            complemento=row.get("complemento"),
                            nome_cidade=row.get("nome_cidade"),
                            uf=row.get("uf"),

                            nome_consultor=row.get("nome_consultor"),
                            nome_responsavel=row.get("nome_responsavel"),
                            ultima_visita=row.get("ultima_visita"),
                            observacoes=row.get("observacao"),
                            valor_proposta=row.get("valor_proposta"),
                            data_criacao=str(row.get("data_criacao"))
                        ))

        except Exception as e:
            print("Erro em buscar_leads:", e)
            raise e

        return leads