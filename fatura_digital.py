import requests
import websocket
import _thread
import time
import json
import re

last_digits = "0000"
cpf = "12345678909"
page_url = "https://prime.altubots.com/chats/viavarejo/1/index.html"
wss_url = re.findall(r"var socket_url = '(.*?)';", requests.get(page_url).text)[0]
identifier = wss_url.split("=")[-1]


def on_message(ws, message):
    data = json.loads(message)

    if data.get("event") == "connected":
        time.sleep(0.1)

        reply = {
            "source": "widget", "event": "chat_message", "params": {
                "slug": "viavarejo", "identifier": data["data"].get("identifier"),
                "assistant_id": "1", "widget_id": "1", "url_params": {
                    "identifier": identifier,
                    "slug": "viavarejo", "source": "widget",
                    "widget_identifier": data["data"]["url_params"]["widget_identifier"],
                    "connection_id": data["data"]["url_params"]["connection_id"],
                    "ip": data["data"]["url_params"]["ip"],
                    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/96.0.4664.110 Safari/537.36"}, "livechat": False, "homol": False},
            "data": {
                "message": "",
                "cognitive": False
            }
        }
        ws.send(json.dumps(reply))

    elif data.get("event") == "chat_message":

        print(data["data"][0]["text"])

        if data["data"][0]["text"] == 'Olá! Sou a Ana, Assistente Virtual das Casas Bahia. Posso te ajudar com a ' \
                                      'fatura do seu cartão Casas Bahia.':
            time.sleep(0.1)

            reply = {
                "source": "widget", "event": "chat_message", "params": {
                    "slug": "viavarejo", "identifier": identifier, "assistant_id": "1",
                    "widget_id": "1", "livechat": False, "homol": False
                },
                "data": {
                    "message": "Sim",
                    "cognitive": False
                }
            }
            ws.send(json.dumps(reply))

        elif data["data"][0]["text"] == 'OK, vamos lá. Qual o seu CPF?':
            time.sleep(0.1)

            reply = {
                "source": "widget", "event": "chat_message", "params": {
                    "slug": "viavarejo", "identifier": identifier, "assistant_id": "1",
                    "widget_id": "1", "livechat": False, "homol": False
                },
                "data": {
                    "message": cpf,
                    "cognitive": False
                }
            }
            ws.send(json.dumps(reply))

        elif data["data"][0]["text"] == 'Desculpe mas este CPF é inválido. Tente novamente por favor.':
            time.sleep(0.1)

            reply = {
                "source": "widget", "event": "chat_message", "params": {
                    "slug": "viavarejo", "identifier": identifier, "assistant_id": "1",
                    "widget_id": "1", "livechat": False, "homol": False
                },
                "data": {
                    "message": cpf,
                    "cognitive": False
                }
            }
            ws.send(json.dumps(reply))

        elif data["data"][0]["text"] == 'Por favor informe os quatro últimos dígitos do seu cartão.':
            time.sleep(0.1)

            reply = {
                "source": "widget", "event": "chat_message", "params": {
                    "slug": "viavarejo", "identifier": identifier, "assistant_id": "1",
                    "widget_id": "1", "livechat": False, "homol": False
                },
                "data": {
                    "message": last_digits,
                    "cognitive": False
                }
            }
            ws.send(json.dumps(reply))

        elif data["data"][0]["text"] == 'Desculpe, mas não consegui verificar seus dados.':
            time.sleep(0.1)

            reply = {
                "source": "widget", "event": "chat_message", "params": {
                    "slug": "viavarejo", "identifier": identifier, "assistant_id": "1",
                    "widget_id": "1", "livechat": False, "homol": False
                },
                "data": {
                    "message": last_digits,
                    "cognitive": False
                }
            }
            ws.send(json.dumps(reply))

        elif 'segue a sua última fatura fechada' in data["data"][0]["text"]:
            link_pdf = re.compile(r"<a href=\'(.+?)\' target=\'_blank\'>Baixar Fatura</a>").findall(
                data["data"][2]["text"])[0]
            file_path = 'fatura_casas_bahia.pdf'
            with requests.get(link_pdf, stream=True) as response:
                with open(file_path, 'wb') as out_file:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        out_file.write(chunk)
            print(data["data"][1]["text"])
            ws.close()

        elif data["data"][0]["text"] == 'Desculpe mas o CPF que você está tentando parece inválido. Por favor ' \
                                        'verifique e tente mais tarde.':
            ws.close()

        elif data["data"][0]["text"] == 'Não foi possível localizar os dados da sua fatura.':
            ws.close()


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        time.sleep(1)

    _thread.start_new_thread(run, ())


if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"{wss_url}&identifier={identifier}",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close
                                )

    ws.run_forever()
