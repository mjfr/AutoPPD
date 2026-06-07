from app.core.pdf_extractor import minerar_texto_pdf
from app.core.word_generator import preencher_documento
import re


def rodar_teste_completo():
    print("Iniciando a fábrica (Polimento Final Absoluto)...")
    ementas = "../ementas/"
    templates = "../templates/"
    testing_docs = "docs/"
    caminho_pdf = ementas + "Ementas GRB0000605.pdf"
    caminho_template = templates + "Modelo Plano de Aula e Ensino - Template.docx"
    caminho_saida = testing_docs + "PPD_Final_Pronto.docx"

    dados_pdf = minerar_texto_pdf(caminho_pdf, "CIÊNCIA, TECNOLOGIA E SUSTENTABILIDADE")

    if not dados_pdf:
        print("Falha pesada na extração. PDF não lido.")
        return

    def formatar_lista_bibliografia(lista_bib):
        lista_formatada = []
        for i, bib in enumerate(lista_bib, start=1):
            url_match = re.search(r'(https?://[^\s]+[^.\s>\]])', bib)
            url = url_match.group(1) if url_match else ""
            texto_sem_url = bib.replace(url, '').strip() if url else bib

            # Limpa as pontuações vazias que sobram quando arrancamos a URL
            texto_sem_url = texto_sem_url.replace('Disponível em: .', 'Disponível em:').replace('Disponível em:.',
                                                                                                'Disponível em:')

            match_abnt = re.search(r'^([^.]+?\.)\s*([^.]+?\.)\s*(.*)', texto_sem_url)

            if match_abnt:
                item = {
                    'num': f"[{i}] ",
                    'autor': match_abnt.group(1) + " ",
                    'titulo': match_abnt.group(2) + " ",
                    'resto': match_abnt.group(3) + " ",
                    'url': url
                }
            else:
                item = {
                    'num': f"[{i}] ",
                    'autor': "",
                    'titulo': texto_sem_url + " ",
                    'resto': "",
                    'url': url
                }
            lista_formatada.append(item)
        return lista_formatada

    if 'bibliografia_basica' in dados_pdf:
        dados_pdf['bibliografia_basica'] = formatar_lista_bibliografia(dados_pdf['bibliografia_basica'])

    if 'bibliografia_complementar' in dados_pdf:
        dados_pdf['bibliografia_complementar'] = formatar_lista_bibliografia(dados_pdf['bibliografia_complementar'])

    if 'competencia_habilidades' in dados_pdf:
        lista_comps = []
        for item in dados_pdf['competencia_habilidades']:
            lista_comps.append({'tag': item['tag'], 'texto': item['texto']})
        dados_pdf['competencia_habilidades'] = lista_comps

    dados_complementares = {
        "nome_curso": "Engenharia Mecânica",
        "coordenador_curso": "\nPara Preencher",
        "nome_disciplina": "Ciência, Tecnologia e Sustentabilidade",
        "nome_professor": "Para Preencher",
        "perfil_saida": "Para Preencher",
    }

    dados_finais = {**dados_pdf, **dados_complementares}
    preencher_documento(dados_finais, caminho_template, caminho_saida)
    print(f"Pronto! Arquivo gerado em: {caminho_saida}")


if __name__ == "__main__":
    rodar_teste_completo()