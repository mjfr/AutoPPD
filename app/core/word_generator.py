from docxtpl import DocxTemplate


def preencher_documento(dados_extraidos, caminho_template, caminho_saida):
    print(f"Injetando os dados no template: {caminho_template}")
    try:
        doc = DocxTemplate(caminho_template)
        doc.render(dados_extraidos)
        doc.save(caminho_saida)

        print(f"PPD gerado em: {caminho_saida}")
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False