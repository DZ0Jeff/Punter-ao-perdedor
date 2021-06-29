print('> Checando...')
# print(match_link)
current_result = ''
try:
    current_result = soap.select_one('h1 span.text-danger').text

except Exception as error:
    print('Resultado ainda não disponivel! checando novamente...')
    continue

else:
    print(f'Resultado: {str(current_result).strip()}')

    if current_result == "Cancelled":
        print('> Partida cancelada!')
        break

    if current_result == "0-1":
        self.telegram.send_message(f"casa {guest} perdendo de {current_result} \nPartida {match_link}")

    if current_result == "0-2" or current_result == "2-0":
        print('Enviar a alarme para o usuário!')
        print('link', match_link)
        self.telegram.send_message(f'partida: {title}\nplacar {current_result}\nlink: {match_link}\nodd: {odd}')
        break

    # results_numbers = current_result.split('-')
    # if int(results_numbers[0]) > 2 or int(results_numbers[1]) > 2:
    #     print('Condição de quebra achada!')
    #     break
    time += 1
    print('segundos...')

    if time >= 50:
        print('Condição de quebra achada!')
        break