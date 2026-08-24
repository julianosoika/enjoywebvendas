from flask import Flask, redirect, request, jsonify
import mercadopago
import requests

app = Flask(__name__)

# Configurações do Mercado Pago
sdk = mercadopago.SDK("APP_USR-4852571365623547-082415-ab27b3c4ba3c75ee260fc222d0efb811-3639627762")

# Configurações da Evolution API
EVOLUTION_URL = "https://evolution.mxbr.com.br"
EVOLUTION_TOKEN = "429683C4C977415CAAFCCE10F7D57E11"
INSTANCE_NAME = "EnjoyWeb"

@app.route("/")
def home():
    return """
    <div style="font-family: Arial; text-align: center; margin-top: 50px;">
        <h1>Bem-vindo ao Enjoy Web! 🚀</h1>
        <p>Acesse <a href='/pagar'>/pagar</a> para gerar o link de pagamento.</p>
        <p>Acesse <a href='/testar-zap'>/testar-zap</a> para testar o envio de WhatsApp.</p>
    </div>
    """

@app.route("/pagar")
def gerar_pagamento():
    preference_data = {
        "items": [
            {
                "title": "Produto do Enjoy Web",
                "quantity": 1,
                "unit_price": 100.00
            }
        ]
    }

    result = sdk.preference().create(preference_data)
    
    if "response" not in result:
        return f"Erro na API do Mercado Pago: {result}", 400

    preference = result["response"]
    link_pagamento = preference.get("init_point")

    if link_pagamento:
        return redirect(link_pagamento)
    else:
        return "Erro ao gerar o link de pagamento.", 400

@app.route("/testar-zap")
def testar_whatsapp():
    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE_NAME}"
    
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_TOKEN
    }
    
    payload = {
        "number": "554731500105", 
        "text": "Olá Juliano! O bot do Enjoy Web integrado com a Evolution API está funcionando perfeitamente 🚀"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201 or response.status_code == 200:
        return "<h1 style='color: green; text-align: center; margin-top: 50px;'>Mensagem enviada com sucesso no WhatsApp! 📱</h1>"
    else:
        return f"<h1>Erro ao enviar mensagem:</h1><p>{response.text}</p>", 400

# Rota que recebe as mensagens do WhatsApp (Webhook da Evolution)
@app.route("/webhook-whatsapp", methods=['POST'])
def webhook_whatsapp():
    data = request.json
    
    try:
        # Extrai os dados da mensagem recebida
        message_data = data.get('data', {})
        sender_phone = message_data.get('key', {}).get('remoteJid')
        
        # Evita responder a si mesmo (mensagens enviadas pelo próprio bot)
        from_me = message_data.get('key', {}).get('fromMe', False)
        
        if sender_phone and not from_me:
            # Dispara os botões interativos de boas-vindas
            enviar_botoes_boas_vindas(sender_phone)
            
    except Exception as e:
        print(f"Erro ao processar webhook do whatsapp: {e}")
        
    return jsonify({"status": "success"}), 200

def enviar_botoes_boas_vindas(phone_number):
    url = f"{EVOLUTION_URL}/message/sendButtons/{INSTANCE_NAME}"
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_TOKEN
    }
    
    payload = {
        "number": phone_number,
        "title": "Bem-vindo ao Enjoy Web! 🚀",
        "description": "Que bom ter você por aqui. Como podemos te ajudar hoje?",
        "footer": "Escolha uma das opções abaixo:",
        "buttons": [
            {
                "buttonId": "btn_comprar",
                "buttonText": {"displayText": "🟢 Quero Comprar"}
            },
            {
                "buttonId": "btn_duvida",
                "buttonText": {"displayText": "💬 Falar com Suporte"}
            }
        ]
    }
    
    requests.post(url, json=payload, headers=headers)

# Rotas de Retorno do Mercado Pago
@app.route("/sucesso")
def pagamento_sucesso():
    return "<h1 style='color: green; text-align: center; margin-top: 50px;'>Pagamento Aprovado com Sucesso! 🎉</h1>"

@app.route("/pendente")
def pagamento_pendente():
    return "<h1 style='color: orange; text-align: center; margin-top: 50px;'>Pagamento Pendente ⏳</h1>"

@app.route("/falha")
def pagamento_falha():
    return "<h1 style='color: red; text-align: center; margin-top: 50px;'>Pagamento Falhou ❌</h1>"

if __name__ == "__main__":
    app.run(debug=True)
