# Gerador Automático de PPD (Planos de Ensino)

Este projeto foi desenvolvido como parte de uma Iniciação Científica (IC) na UniSenai. O objetivo é eliminar o trabalho braçal e repetitivo na criação de Planos de Aula e Ensino (PPDs) através da extração inteligente de dados em PDFs institucionais (Projetos Pedagógicos de Curso - PPC).

## Como funciona?
O sistema utiliza **Python** e Expressões Regulares (Regex) avançadas para varrer e extrair blocos específicos de texto de PDFs engessados. Em seguida, os dados estruturados são injetados diretamente em um template oficial do Microsoft Word (`.docx`), mantendo toda a formatação original da instituição de ensino, gerando um documento pronto para uso em segundos.

A interface do usuário é gerada dinamicamente com **Streamlit**, permitindo que qualquer professor utilize a ferramenta sem necessidade de conhecimentos técnicos.

## Stack Tecnológica
* **Back-end:** Python 3
* **Extração de PDF:** `PyMuPDF` (fitz)
* **Geração de Documentos:** `docxtpl` (Jinja2 para Word)
* **Front-end:** `Streamlit`

## Arquitetura do Projeto (Separation of Concerns)
A aplicação foi construída visando facilidade de manutenção e expansão. A interface não sabe como o PDF é lido, e o extrator não sabe como o Word é gerado.

```text
gerador-ppd/
├── app/
│   ├── main.py                 # Interface Web (Streamlit)
│   └── core/
│       ├── pdf_extractor.py    # Motor de Regex e Extração
│       └── word_generator.py   # Motor de Injeção de Tags
├── templates/
│   └── Modelo Plano...docx     # O "molde" com as tags Jinja2
└── README.md
```

A arquitetura foi desenhada para facilitar a integração de novas automações. As próximas fases do desenvolvimento incluem a extração e o autopreenchimento de:

[ ] Cronograma de aulas (Grade diária).

[ ] Atividades Práticas Supervisionadas (APS).

[ ] Instrumentos de Avaliação e Desafios.

[ ] Composição de Nota.

# Como executar localmente
Instale as dependências: 
```bash
pip install -r requirements.txt 
ou 
pip install streamlit docxtpl PyMuPDF
```

Execute o servidor: 
```bash
streamlit run app/main.py
```

Acesse via navegador no localhost.

# Problemas conhecidos:
1. Layout do documento Word está mal formatado.
* Solução: Abrir Manualmente o documento Word e expandir a tabela até o conteúdo caber dentro das células.
