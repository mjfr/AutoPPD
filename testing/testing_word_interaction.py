import os

from docxtpl import DocxTemplate


def testar_gerador():

    print("Iniciando e lendo o template")
    doc = DocxTemplate("../templates/Modelo Plano de Aula e Ensino - Template.docx")

    print("Definindo as tags e conteúdos")
    contexto = {
        "nome_curso": "Engenharia Mecânica",
        "nome_periodo": "Primeiro Periodo",
        "ano_semestre": "1º Semestre",
        "nome_disciplina": "Engenharia de Protótipos e Modelagem 3D",
        "nome_professor": "Matheus",
        "coordenador_curso": "José",
        "at_ext_sim": "",
        "at_ext_nao": "x",
        "ementa": "Esta é uma ementa gerada automaticamente pelo nosso script Python. A mágica está acontecendo!",
        "perfil_saida": "O aluno será capaz de resolver problemas reais sem depender de burocracia.",
        "conteudos_formativos": "1. Introdução à Automação\n2. Manipulação de Documentos\n3. Interface Web",
        "bibliografia_basica": "Documentação Oficial do Python.",
        "bibliografia_complementar": "Fóruns e StackOverflow.",
        "competencia_habilidades": "Capacidade de integrar bibliotecas e gerar valor prático."
    }

    print("Fazendo as substituições das tags")
    # Engine para substituição dos conteúdos do documento
    doc.render(contexto)

    print("Salvando o arquivo")
    docs_folder = "docs"
    nome_arquivo_final = "PPD_MVP.docx"
    os.makedirs(docs_folder, exist_ok=True)
    doc.save(docs_folder+"/"+nome_arquivo_final)

    print(f"{nome_arquivo_final} foi gerado com sucesso.")


if __name__ == "__main__":
    testar_gerador()