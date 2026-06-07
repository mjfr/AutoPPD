import streamlit as st
import os
from core.pdf_extractor import minerar_texto_pdf
from core.word_generator import preencher_documento

st.set_page_config(page_title="AutoPPD - UniSenai", page_icon="", layout="centered")

st.title("AutoPPD")
st.markdown("Professor, automatize a criação dos seus Planos de Ensino puxando os dados direto da ementa oficial.")

st.header("1. Arquivos Base")
pdf_file = st.file_uploader("Faça o upload do PDF da Ementa (PPC)", type=["pdf"])
caminho_template = "templates/Modelo Plano de Aula e Ensino - Template.docx"

st.header("2. Informações da Disciplina")

nome_professor = st.text_input("Seu Nome Completo", placeholder="Ex: João Maria")
coordenador_curso = st.text_input("Nome do Coordenador de Curso", placeholder="Ex: Maria João")
nome_curso = st.text_input("Nome do Curso", placeholder="Ex: Engenharia Mecânica")
nome_disciplina = st.text_input("Nome da Disciplina (Exatamente como está no PDF)",
                                placeholder="Ex: DESIGN DE SOFTWARE APLICADO À ENGENHARIA")
perfil_saida = st.text_area("Perfil de Saída do Aluno/Egresso", placeholder="Cole ou digite o perfil de saída aqui")

if st.button("Gerar Plano de Ensino", type="primary"):
    if not pdf_file or not nome_professor or not nome_disciplina:
        st.error("Preencha os campos principais e faça o upload do PDF antes de gerar.")
    else:
        with st.spinner("Lendo o PDF, ignorando rodapés e formatando o documento..."):
            temp_pdf_path = "temp_ementa.pdf"
            with open(temp_pdf_path, "wb") as f:
                f.write(pdf_file.getbuffer())

            dados_pdf = minerar_texto_pdf(temp_pdf_path, nome_disciplina)

            if not dados_pdf:
                st.error("Disciplina não encontrada no PDF. Verifique se o nome está idêntico.")
            else:
                dados_complementares = {
                    "nome_curso": nome_curso,
                    "coordenador_curso": coordenador_curso if coordenador_curso else " ",
                    "nome_disciplina": nome_disciplina.title(),
                    "nome_professor": nome_professor,
                    "perfil_saida": perfil_saida if perfil_saida else " ",
                }

                dados_finais = {**dados_pdf, **dados_complementares}

                caminho_saida = f"PPD_{nome_disciplina.replace(' ', '_')}.docx"
                sucesso = preencher_documento(dados_finais, caminho_template, caminho_saida)

                if sucesso:
                    st.success("PPD Gerado com Sucesso! ABNT e formatações aplicadas.")
                    with open(caminho_saida, "rb") as file:
                        st.download_button(
                            label="Baixar Plano de Ensino (.docx)",
                            data=file,
                            file_name=caminho_saida,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    os.remove(temp_pdf_path)
                    os.remove(caminho_saida)
                else:
                    st.error("Erro interno ao gerar o arquivo Word.")