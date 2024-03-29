import re
import time
import json
import requests
import websocket
from optparse import OptionParser

wss_url = re.findall(r"var socket_url = '(.*?)';",
                     requests.get("https://prime.altubots.com/chats/viavarejo/1/index.html").text)[0]
identifier = wss_url.split("=")[-1]
source_id = None


def client_reply(message, is_private=False, initial_reply=None):
    print("==> Client: ",
          f"{message.translate(message.maketrans(dict.fromkeys('.-', '')))[:-4]}****"
          if is_private else message) if message != "" else ""
    return {
        "source": "widget", "event": "chat_message", "params": initial_reply if initial_reply else {
            "slug": "viavarejo", "source": "widget", "source_id": source_id,
            "identifier": identifier, "homol": False
        },
        "data": {
            "message": message,
            "cognitive": False
        }
    }


def on_message(ws, message):
    global source_id
    data = json.loads(message)

    if data.get("event") == "connected":
        reply = {
            "source": "widget",
            "event": "chat_message",
            "params": {
                "slug": "viavarejo",
                "source": "widget",
                "source_id": data["data"]["params"]["source_id"],
                "identifier": data["data"]["params"]["identifier"],
                "homol": False,
                "init": {
                    "source": "widget",
                    "ip": data["data"]["params"]["init"]["ip"],
                    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/96.0.4664.110 Safari/537.36",
                    "external_id": data["data"]["params"]["init"]["external_id"]
                },
            },
            "data": {
                "message": "",
                "cognitive": False
            }
        }

        source_id = data["data"]["params"]["source_id"]
        # reply = client_reply("", initial_reply=reply)
        ws.send(json.dumps(reply))

    elif data.get("event") == "chat_message":
        print("==> Server: ", data["data"]["messages"][0]["text"])
        if data["data"]["messages"][0]["text"] in ['Olá! Sou a Ana, Assistente Virtual das Casas Bahia. '
                                                   'Posso te ajudar com a fatura do seu cartão Casas Bahia.']:
            reply = client_reply("Sim")
            ws.send(json.dumps(reply))

        elif data["data"]["messages"][0]["text"] in ['OK, vamos lá. Qual o seu CPF?',
                                                     'Desculpe mas este CPF é inválido. Tente novamente por favor.']:
            reply = client_reply(cpf, is_private=True)
            ws.send(json.dumps(reply))

        elif data["data"]["messages"][0]["text"] in ['Por favor informe os quatro últimos dígitos do seu cartão.',
                                                     'Desculpe, mas não consegui verificar seus dados.']:
            reply = client_reply(last_digits, is_private=True)
            ws.send(json.dumps(reply))

        elif 'segue a sua última fatura fechada' in data["data"]["messages"][0]["text"]:
            link_pdf = re.compile(r"<a href=\'(.+?)\' target=\'_blank\'>Baixar Fatura</a>").findall(
                data["data"]["messages"][2]["text"])[0]
            print(f"\n{link_pdf}")
            file_path = 'fatura_casas_bahia.pdf'
            with requests.get(link_pdf, stream=True) as response:
                print(f"Baixando {file_path} ...")
                with open(file_path, 'wb') as out_file:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        out_file.write(chunk)
            print(f'\n{data["data"]["messages"][1]["text"]}')
            ws.close()

        elif data["data"]["messages"][0]["text"] in ['Desculpe mas o CPF que você está tentando parece inválido. '
                                                     'Por favor verifique e tente mais tarde.',
                                                     'Não foi possível localizar os dados da sua fatura.']:
            ws.close()
    time.sleep(0.1)


if __name__ == "__main__":
    usage = "USAGE: %prog [options]\n\nDownload invoices from the website https://casasbahia.digital"

    parser = OptionParser(usage=usage, version='%prog 0.1')
    parser.add_option("-c", "--cpf", dest="cpf",
                      help="Official document of person", type=str, default='123.456.789-09')
    parser.add_option("-l", "--last-digits", dest="last_digits",
                      help="Four last digits from the credit card", default='0000', type=str)

    (options, args) = parser.parse_args()
    cpf, last_digits = options.cpf, options.last_digits
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"{wss_url}&identifier={identifier}",
                                on_message=on_message
                                )
    ws.run_forever()
