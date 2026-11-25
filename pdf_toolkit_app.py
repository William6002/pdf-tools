 """
PDF Toolkit - Aplicação para manipulação de PDFs
==================================================
Funcionalidades:
  - Juntar múltiplos PDFs em um único arquivo
  - Reorganizar (reordenar) as páginas de um PDF
  - Remover páginas específicas
  - Baixar o resultado final

Como executar:
    pip install streamlit pypdf
    streamlit run pdf_toolkit_app.py
"""

import io
from pypdf import PdfReader, PdfWriter
import streamlit as st

st.set_page_config(page_title="PDF Toolkit", page_icon="📄", layout="centered")
st.title("📄 PDF Toolkit")
st.caption("Junte PDFs e reorganize páginas de forma simples.")

modo = st.sidebar.radio(
    "Escolha a funcionalidade:",
    ["Juntar PDFs", "Reorganizar páginas"]
)

# ---------------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# ---------------------------------------------------------------------------

def juntar_pdfs(arquivos):
    """Recebe uma lista de arquivos (na ordem desejada) e retorna bytes do PDF final."""
    writer = PdfWriter()
    for arquivo in arquivos:
        reader = PdfReader(arquivo)
        for pagina in reader.pages:
            writer.add_page(pagina)
    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    return buffer


def reorganizar_paginas(arquivo, nova_ordem):
    """Recebe um arquivo PDF e uma lista com a nova ordem (índices 0-based)."""
    reader = PdfReader(arquivo)
    writer = PdfWriter()
    for indice in nova_ordem:
        writer.add_page(reader.pages[indice])
    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    return buffer


# ---------------------------------------------------------------------------
# MODO 1: JUNTAR PDFs
# ---------------------------------------------------------------------------

if modo == "Juntar PDFs":
    st.header("🔗 Juntar PDFs")
    st.write("Envie dois ou mais arquivos PDF. Você poderá definir a ordem antes de juntar.")

    arquivos = st.file_uploader(
        "Selecione os arquivos PDF",
        type="pdf",
        accept_multiple_files=True
    )

    if arquivos:
        st.subheader("Defina a ordem dos arquivos")
        nomes = [a.name for a in arquivos]

        # Cria um seletor de ordem para cada arquivo
        ordem_escolhida = []
        opcoes_disponiveis = list(range(1, len(arquivos) + 1))

        for i, arquivo in enumerate(arquivos):
            posicao = st.selectbox(
                f"Posição de '{arquivo.name}'",
                options=opcoes_disponiveis,
                index=i,
                key=f"pos_{i}"
            )
            ordem_escolhida.append((posicao, arquivo))

        # Ordena os arquivos pela posição escolhida
        ordem_escolhida.sort(key=lambda x: x[0])
        arquivos_ordenados = [a for _, a in ordem_escolhida]

        st.write("**Ordem final:**")
        for idx, a in enumerate(arquivos_ordenados, start=1):
            st.write(f"{idx}. {a.name}")

        if st.button("Juntar PDFs", type="primary"):
            resultado = juntar_pdfs(arquivos_ordenados)
            st.success("PDFs unidos com sucesso!")
            st.download_button(
                label="⬇️ Baixar PDF final",
                data=resultado,
                file_name="pdf_unido.pdf",
                mime="application/pdf"
            )

# ---------------------------------------------------------------------------
# MODO 2: REORGANIZAR PÁGINAS
# ---------------------------------------------------------------------------

else:
    st.header("🔀 Reorganizar páginas")
    st.write("Envie um PDF e defina a nova ordem das páginas.")

    arquivo = st.file_uploader("Selecione o PDF", type="pdf")

    if arquivo:
        reader = PdfReader(arquivo)
        total_paginas = len(reader.pages)
        st.info(f"O PDF tem **{total_paginas}** páginas.")

        st.write("Informe a nova ordem das páginas separadas por vírgula "
                  "(numeração a partir de 1). Exemplo para inverter um PDF de 4 páginas: `4,3,2,1`")

        ordem_padrao = ", ".join(str(n) for n in range(1, total_paginas + 1))
        ordem_texto = st.text_input("Nova ordem das páginas", value=ordem_padrao)

        # Botões de atalho úteis
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Inverter ordem"):
                ordem_texto = ", ".join(str(n) for n in range(total_paginas, 0, -1))
                st.session_state["ordem_texto"] = ordem_texto
        with col2:
            if st.button("Ordem original"):
                ordem_texto = ordem_padrao
                st.session_state["ordem_texto"] = ordem_texto

        if "ordem_texto" in st.session_state:
            ordem_texto = st.session_state["ordem_texto"]

        try:
            nova_ordem = [int(n.strip()) - 1 for n in ordem_texto.split(",") if n.strip()]

            # Validações
            if any(idx < 0 or idx >= total_paginas for idx in nova_ordem):
                st.error(f"Use apenas números entre 1 e {total_paginas}.")
            elif len(nova_ordem) == 0:
                st.error("Informe ao menos uma página.")
            else:
                if len(set(nova_ordem)) != total_paginas:
                    st.warning(
                        "Atenção: você não incluiu todas as páginas, ou repetiu alguma. "
                        "O PDF resultante terá apenas as páginas listadas, na ordem informada."
                    )

                if st.button("Reorganizar PDF", type="primary"):
                    resultado = reorganizar_paginas(arquivo, nova_ordem)
                    st.success("Páginas reorganizadas com sucesso!")
                    st.download_button(
                        label="⬇️ Baixar PDF reorganizado",
                        data=resultado,
                        file_name="pdf_reorganizado.pdf",
                        mime="application/pdf"
                    )
        except ValueError:
            st.error("Formato inválido. Use números separados por vírgula, ex: 1,3,2,4")
