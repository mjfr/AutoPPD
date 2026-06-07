import datetime
import fitz
import re


def limpar_texto(texto):
    if not texto: return ""
    return re.sub(r'\s+', ' ', texto.strip())


def minerar_texto_pdf(caminho_arquivo, nome_disciplina_alvo):
    try:
        doc = fitz.open(caminho_arquivo)
        texto_limpo_paginas = []
        for pagina in doc:
            txt = pagina.get_text("text")
            txt = txt.replace('\n', ' ')

            txt = re.sub(r'\d*\s*Uni\s*SENAI.*?CEP\s*\d{5}-\d{3}', ' ', txt, flags=re.IGNORECASE)
            txt = re.sub(r'Uni\s*SENAI\s*PR', ' ', txt, flags=re.IGNORECASE)

            texto_limpo_paginas.append(txt)
        doc.close()

        texto_completo = " ".join(texto_limpo_paginas)
        texto_completo = re.sub(r'[–—−]', '-', texto_completo)
        texto_completo = re.sub(r'\s+', ' ', texto_completo)
    except Exception as e:
        print(f"Erro ao abrir o PDF: {e}")
        return None

    texto_upper = texto_completo.upper()

    nome_limpo = re.sub(r'[–—−]', '-', nome_disciplina_alvo).upper().strip()
    palavras_alvo = re.split(r'\s+', nome_limpo)
    padrao_busca = r'[\s\-–—−:.,]+'.join([re.escape(p) for p in palavras_alvo])

    matches_nome = list(re.finditer(padrao_busca, texto_upper))

    indice_inicio_bloco = -1
    indice_cht_atual = -1

    for m in matches_nome:
        pos = m.end()
        proximo_cht = re.search(r'CHT\s*\([dD]ISCIPLINA\)', texto_upper[pos:])
        if proximo_cht and proximo_cht.start() < 1500:
            indice_inicio_bloco = m.start()
            indice_cht_atual = pos + proximo_cht.start()
            break

    if indice_inicio_bloco == -1:
        return {}

    proximo_cht_fim = re.search(r'CHT\s*\([dD]ISCIPLINA\)', texto_upper[indice_cht_atual + 50:])

    if proximo_cht_fim:
        pos_fim_cht = indice_cht_atual + 50 + proximo_cht_fim.start()
        pos_quadro = texto_upper.rfind("QUADRO", indice_cht_atual, pos_fim_cht)

        if pos_quadro != -1 and (pos_fim_cht - pos_quadro) < 600:
            indice_fim = pos_quadro
        else:
            indice_fim = pos_fim_cht

        texto_disciplina = texto_completo[indice_inicio_bloco:indice_fim]
    else:
        texto_disciplina = texto_completo[indice_inicio_bloco:]

    dados = {}

    match_ch_total = re.search(r'CHT\s*\([dD]isciplina\)\s*:\s*(\d+)', texto_disciplina)
    match_ch_pratica = re.search(r'CH\s*\([pP]rática\)\s*:\s*(\d+)', texto_disciplina)
    match_ch_extensao = re.search(r'CH\s*\([eE]xtensão\)\s*:\s*(\d+)', texto_disciplina)

    ch_total = int(match_ch_total.group(1)) if match_ch_total else 0
    ch_pratica = int(match_ch_pratica.group(1)) if match_ch_pratica else 0
    ch_extensao = int(match_ch_extensao.group(1)) if match_ch_extensao else 0

    dados['ch_total'] = f"{ch_total}"
    dados['ch_pratica'] = f"{ch_pratica}"
    dados['ch_teorica'] = f"{ch_total - ch_pratica}"

    match_extensao_txt = re.search(r'CH\s*\([eE]xtensão\)\s*:\s*(.*)', texto_disciplina)
    if match_extensao_txt and "NÃO SE APLICA" in match_extensao_txt.group(1).upper():
        dados['at_ext_sim'] = " "
        dados['at_ext_nao'] = "X"
    else:
        dados['at_ext_sim'] = "X"
        dados['at_ext_nao'] = " "
        dados['ch_extensao'] = f"{ch_extensao}"

    match_periodo = re.search(r'(\d+º)', texto_disciplina)
    if match_periodo: dados['nome_periodo'] = limpar_texto(match_periodo.group(1))
    ano_semestre = match_periodo.group(1)[0] if match_periodo else "1"
    year_now = datetime.datetime.now().year
    dados['ano_semestre'] = f"{year_now}/1" if int(ano_semestre) % 2 == 1 else f"{year_now}/2"

    match_ementa = re.search(r'EMENTA\s*:(.*?)CONTEÚDO FORMATIVO\s*:', texto_disciplina, re.IGNORECASE)
    if match_ementa: dados['ementa'] = limpar_texto(match_ementa.group(1))

    match_conteudo = re.search(r'CONTEÚDO FORMATIVO\s*:(.*?)BIBLIOGRAFIA BÁSICA\s*:', texto_disciplina, re.IGNORECASE)
    if match_conteudo:
        dados['conteudos_formativos'] = [i.strip() for i in limpar_texto(match_conteudo.group(1)).split(';') if
                                         i.strip()]

    match_competencias = re.search(r'COMPETÊNCIAS E HABILIDADES(.*?)EMENTA\s*:', texto_disciplina, re.IGNORECASE)
    if match_competencias:
        padrao = r'(C\.\d+|H\.\d+(?:\.\d+)?)\s*(.*?)(?=\s*C\.\d+|\s*H\.\d+(?:\.\d+)?|$)'
        encontrados = re.findall(padrao, limpar_texto(match_competencias.group(1)))
        dados['competencia_habilidades'] = [{'tag': c[0], 'texto': c[1]} for c in encontrados] if encontrados else [
            {'tag': '', 'texto': limpar_texto(match_competencias.group(1))}]

    def extrair_bibliografias(texto_bruto):
        texto_limpo = limpar_texto(texto_bruto)
        texto_limpo = re.sub(r'\[on-?line\]\s*Ac\s*\d+\.?', '', texto_limpo, flags=re.IGNORECASE)
        texto_limpo = re.sub(r'Ac\s*\d+\.?', '', texto_limpo, flags=re.IGNORECASE)
        if re.search(r'\[\d+\]', texto_limpo):
            itens = re.split(r'\[\d+\]\s*', texto_limpo)
        else:
            itens = re.split(r'(?<=\.)\s+(?=[A-ZÁÉÍÓÚÂÊÎÔÛÃÕÇ]{2,},\s+[A-Z])', texto_limpo)
        return [i.strip() for i in itens if len(i.strip()) > 5]

    match_bib_basica = re.search(r'BIBLIOGRAFIA BÁSICA\s*:(.*?)BIBLIOGRAFIA COMPLEMENTAR\s*:', texto_disciplina,
                                 re.IGNORECASE)
    if match_bib_basica:
        lista_formatada = []
        for i, bib in enumerate(extrair_bibliografias(match_bib_basica.group(1)), start=1):
            url_match = re.search(r'(https?://[^\s]+[^.\s>\]])', bib)
            url = url_match.group(1) if url_match else ""
            texto_sem_url = bib.replace(url, '').strip() if url else bib
            texto_sem_url = texto_sem_url.replace('Disponível em: .', 'Disponível em:').replace('Disponível em:.',
                                                                                                'Disponível em:')
            match_abnt = re.search(r'^(.+?\.(?:\s*\([^)]+\)\.)?)\s+([^.]+?\.)\s+(.*)', texto_sem_url)

            if match_abnt:
                lista_formatada.append(
                    {'num': f"[{i}] ", 'autor': match_abnt.group(1) + " ", 'titulo': match_abnt.group(2) + " ",
                     'resto': match_abnt.group(3) + " ", 'url': url})
            else:
                lista_formatada.append(
                    {'num': f"[{i}] ", 'autor': "", 'titulo': texto_sem_url + " ", 'resto': "", 'url': url})
        dados['bibliografia_basica'] = lista_formatada

    match_bib_comp = re.search(r'BIBLIOGRAFIA COMPLEMENTAR\s*:(.*)', texto_disciplina, re.IGNORECASE)
    if match_bib_comp:
        lista_formatada = []
        for i, bib in enumerate(extrair_bibliografias(match_bib_comp.group(1)), start=1):
            url_match = re.search(r'(https?://[^\s]+[^.\s>\]])', bib)
            url = url_match.group(1) if url_match else ""
            texto_sem_url = bib.replace(url, '').strip() if url else bib
            texto_sem_url = texto_sem_url.replace('Disponível em: .', 'Disponível em:').replace('Disponível em:.',
                                                                                                'Disponível em:')
            match_abnt = re.search(r'^(.+?\.(?:\s*\([^)]+\)\.)?)\s+([^.]+?\.)\s+(.*)', texto_sem_url)
            if match_abnt:
                lista_formatada.append(
                    {'num': f"[{i}] ", 'autor': match_abnt.group(1) + " ", 'titulo': match_abnt.group(2) + " ",
                     'resto': match_abnt.group(3) + " ", 'url': url})
            else:
                lista_formatada.append(
                    {'num': f"[{i}] ", 'autor': "", 'titulo': texto_sem_url + " ", 'resto': "", 'url': url})
        dados['bibliografia_complementar'] = lista_formatada

    return dados