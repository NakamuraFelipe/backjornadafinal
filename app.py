from flask import Flask
from flask_cors import CORS # type: ignore

from routes.login import login_bp
from routes.lead_routes import lead_bp
from routes.meus_leads import meus_leads_bp
from routes.all_leads import all_leads_bp



app = Flask(__name__)
app.secret_key = "DeAdMaU5#"  # Necessário para usar session

# 🔹 Configure corretamente o CORS
CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://localhost:3000",  # se o front estiver rodando localmente
        "http://192.168.0.3:5000"  # se o front estiver acessando via rede
    ]
)

# 🔹 Registrar o blueprint de login
app.register_blueprint(login_bp)

# 🔹 Registrar o blueprint de lead
app.register_blueprint(lead_bp)

# 🔹 Registrar o blueprint de meus lead
app.register_blueprint(meus_leads_bp)  

app.register_blueprint(all_leads_bp)
1


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Railway define PORT
    app.run(host="0.0.0.0", port=port, debug=True)  # debug pode ficar True para teste
