from utils.futbot_nlp import *

entrada = ""
while(entrada!="Salir"):
    print("¡Hola! Mi nombre es FutBot y estoy aquí para ayudarte. Cuento con datos hasta la temporada 19-20.")
    print()
    level = 1
    while(entrada!="Salir" and level==1):
        print("¿De qué liga te gustaría saber?")
        liga = str(input())
        print()
        entrada = str(get_gpt3_completion(f"To which of these strings is the string '{liga}' more similar to? If there is no clear match, print 'Again'. The strings to check are: [Salir, Liga MX, La Liga, Premier League, Serie A, Ligue 1, Bundesliga]. Only answer with one of the strings and print it."))
        entrada = entrada.replace("\n\n ", '')
        entrada = entrada.replace("\n\n", '')
        liga = entrada
        if(liga == "Salir"):
            print("¡Gracias por usar FutBot!")
            entrada = "Salir"
            break
        elif(liga == "Again"):
            print("No te entendi. ¡Inténtalo de nuevo!")
        else:
            level = 2
            while(entrada!="Salir" and level==2):
                if(liga not in ["La Liga", "Premier League", "Serie A", "Ligue 1", "Bundesliga"]):
                    print(liga+" no soportada :(")
                    level=1
                    liga=""
                    break
                else:
                    print(f"¿Sobre qué equipo de la {liga} te gustaría saber?")
                    liga_mod = liga.lower().replace(" ", "-")
                    equipos_liga = os.listdir(f"C:/Users/ssds6/Documents/analisis_deportivo/data/capology/raw/{liga_mod}/2019-2020/")
                    equipos_liga = [s.replace(f'_{liga_mod}_2019-2020.csv', '') for s in equipos_liga]
                    equipos_liga = [s for s in equipos_liga if not s.startswith('all')]
                    equipos_liga = [s.replace('-', ' ') for s in equipos_liga]
                    #equipos_liga = [s.title() for s in equipos_liga]
                    equipos_liga_options = equipos_liga + ["salir, atras"]
                    equipo = str(input())
                    print()
                    entrada = str(get_gpt3_completion(f"To which of these strings is the string '{equipo}' more similar to? If you find an exact match in the list, print the exact match. Only answer with one of the strings, and if there is no clear match, print 'Again'. The strings to check are: "+str(equipos_liga_options)))
                    entrada = entrada.replace("\n\n ", '')
                    entrada = entrada.replace("\n\n", '')
                    equipo = entrada
                    if(equipo == "salir"):
                        print("¡Gracias por usar FutBot!")
                        entrada="Salir"
                        break
                    elif(equipo == "again"):
                        print("No te entendi. ¡Inténtalo de nuevo!")
                        print()
                        equipo=''
                    elif(equipo == "atras"):
                        print("Regresando al menú anterior...")
                        print()
                        level = 1
                    else:
                        datos_temp = str(get_gpt3_completion(f"Escribe 3 datos de la temporada de liga más reciente de {equipo} en español"))
                        datos_temp = datos_temp.replace("\n\n ", '')
                        datos_temp = datos_temp.replace("\n\n", '')
                        print(datos_temp)
                        print()
                        level = 3
                        while(entrada!="Salir" and level==3):
                            print(f"¿Sobre qué jugador de {equipo} te gustaría saber?")
                            liga_mod = liga.lower().replace(" ", "-")
                            equipo_mod = equipo.replace(" ", "-")
                            equipo_mod += f'_{liga_mod}_2019-2020.csv'
                            equipo_df = pd.read_csv(f"C:/Users/ssds6/Documents/analisis_deportivo/data/capology/raw/{liga_mod}/2019-2020/{equipo_mod}")
                            list_players = equipo_df.Player.to_list()
                            list_players_options = list_players + ["salir, atras"]
                            player = str(input())
                            print()
                            entrada = str(get_gpt3_completion(f"To which of these strings is the string '{player}' more similar to? If you find an exact match in the list, print the exact match. Only answer with one of the strings, and if there is no clear match, print 'Again'. The strings to check are: "+str(list_players_options)))
                            entrada = entrada.replace("\n\n ", '')
                            entrada = entrada.replace("\n\n", '')
                            player = entrada
                            if(player == "salir"):
                                print("¡Gracias por usar FutBot!")
                                entrada="Salir"
                                break
                            elif(player == "Again"):
                                print("No te entendi. ¡Inténtalo de nuevo!")
                                print()
                                player=''
                            elif(player == "atras"):
                                print("Regresando al menú anterior...")
                                print()
                                level = 2
                            else:
                                dict_player_name = query_payload_name(equipo_df, player)
                                dict_player_pos = query_payload_posdfkm(equipo_df, player)
                                dict_player_age = query_payload_age(equipo_df, player)
                                dict_player_country = query_payload_country(equipo_df, player)
                                output_name = query(dict_player_name)
                                output_pos = query(dict_player_pos)
                                output_age = query(dict_player_age)
                                output_country = query(dict_player_country)
                                player_labels = [dict_player_name['inputs']['query'], dict_player_pos['inputs']['query'], dict_player_age['inputs']['query'],dict_player_country['inputs']['query']]
                                player_answers = [output_name['cells'],output_pos['cells'],output_age['cells'],output_country['cells']]
                                print(str(get_gpt3_completion(f"Dado que {str(player_answers)} son las respuestas de {str(player_labels)}, cambiando la palabras 'jugador' por 'nombre', 'Pos. DFKM' por 'posicion', 'D' por 'defensa', 'F' por 'delantero', 'K' por 'portero' y 'M' por 'mediocampista', escribe estos datos en una sola oración.")))
                                print()
                                level = 3
