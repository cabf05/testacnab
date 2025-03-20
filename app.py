import streamlit as st
import datetime
import pandas as pd

# ====================== FUNÇÕES AUXILIARES ======================
def pad_numeric(value, length):
    """Formata valor numérico com zeros à esquerda, garantindo tamanho fixo."""
    s = str(value)
    return s.zfill(length)[-length:]

def pad_alfa(value, length):
    """Formata texto com espaços à direita, truncando se necessário."""
    s = str(value)
    return s.ljust(length)[:length]

# ====================== FUNÇÕES PARA GERAR O ARQUIVO CNAB240 (REMESSA) ======================
def build_header_arquivo(company):
    record = ""
    record += pad_numeric("077", 3)                           # Código do banco (1-3)
    record += pad_numeric("0000", 4)                          # Lote de serviço (4-7)
    record += "0"                                             # Tipo de registro (8)
    record += " " * 9                                         # Campo em branco (9-17)
    record += "2"                                             # Tipo de documento (CNPJ) (18)
    record += pad_numeric(company["cnpj"], 14)                # CNPJ (19-32)
    record += " " * 20                                        # Campo em branco (33-52)
    record += pad_numeric(company["agencia"], 5)              # Agência (53-57)
    record += pad_alfa(company["agencia_dv"], 1)              # Dígito da agência (58)
    record += pad_numeric(company["conta"], 12)               # Conta corrente (59-70)
    record += pad_numeric(company["conta_dv"], 1)             # Dígito da conta (71)
    record += " "                                             # Campo em branco (72)
    record += pad_alfa(company["nome_empresa"], 30)           # Nome da empresa (73-102)
    record += pad_alfa("BANCO INTER", 30)                     # Nome do banco (103-132)
    record += " " * 10                                        # Campo em branco (133-142)
    record += "1"                                             # Código de remessa (143)
    hoje = datetime.datetime.now()
    record += hoje.strftime("%d%m%Y")                         # Data de geração (144-151)
    record += hoje.strftime("%H%M%S")                         # Hora de geração (152-157)
    record += pad_numeric(company["sequencial"], 6)           # Número sequencial do arquivo (158-163)
    record += pad_numeric("107", 3)                           # Versão do layout (164-166)
    record += pad_numeric("01600", 5)                         # Densidade de gravação (167-171)
    record += " " * 20                                        # Uso reservado do banco (172-191)
    record += " " * 20                                        # Uso reservado da empresa (192-211)
    record += " " * 29                                        # Uso exclusivo FEBRABAN/CNAB (212-240)
    return record.ljust(240)

def build_header_lote_pix(company):
    record = ""
    record += pad_numeric("077", 3)                           # Código do banco (1-3)
    record += pad_numeric("1", 4)                             # Lote de serviço "0001" (4-7)
    record += "1"                                             # Tipo de registro (8)
    record += "C"                                             # Tipo de operação (9)
    record += pad_numeric("00", 2)                            # Tipo de serviço (10-11) – default "00"
    record += pad_numeric("45", 2)                            # Forma de lançamento PIX (12-13)
    record += pad_numeric("046", 3)                           # Versão do layout do lote (14-16)
    record += " "                                             # Campo em branco (17)
    record += "2"                                             # Tipo de documento da empresa (18)
    record += pad_numeric(company["cnpj"], 14)                # CPF/CNPJ (19-32)
    record += " " * 20                                        # Campo em branco (33-52)
    record += pad_numeric(company["agencia"], 5)              # Agência (53-57)
    record += pad_alfa(company["agencia_dv"], 1)              # DV Agência (58)
    record += pad_numeric(company["conta"], 12)               # Conta (59-70)
    record += pad_numeric(company["conta_dv"], 1)             # DV Conta (71)
    record += " "                                             # Campo em branco (72)
    record += pad_alfa(company["nome_empresa"], 30)           # Nome da empresa (73-102)
    record += pad_alfa(company.get("generica", ""), 40)       # Informação genérica opcional (103-142)
    record += pad_alfa(company["rua"], 30)                    # Nome da Rua (143-172)
    record += pad_numeric(company["numero"], 5)               # Número do local (173-177)
    record += pad_alfa(company["complemento"], 15)            # Complemento (178-192)
    record += pad_alfa(company["cidade"], 20)                 # Cidade (193-212)
    record += pad_numeric(company["cep"], 5)                  # CEP (213-217)
    record += " " * 3                                         # Complemento do CEP (218-220)
    record += pad_alfa(company["estado"], 2)                  # Sigla do Estado (221-222)
    record += " " * 8                                         # Campo em branco (223-230)
    record += " " * 10                                        # Ocorrências para retorno (231-240)
    return record.ljust(240)

def build_segmento_a_pix(transaction, seq):
    record = ""
    record += pad_numeric("077", 3)                           # (1-3)
    record += pad_numeric("1", 4)                             # (4-7)
    record += "3"                                             # (8)
    record += pad_numeric(seq, 5)                             # (9-13)
    record += "A"                                             # Código de segmento (14)
    record += "0"                                             # Tipo de movimento (15)
    record += pad_numeric("00", 2)                            # Código da instrução para movimento (16-17)
    record += pad_numeric("000", 3)                           # Código da câmara centralizadora (18-20)
    # Bloco de dados do favorecido – deve ocupar 53 caracteres
    if transaction["forma_iniciacao"] == "05":
        record += pad_numeric(transaction.get("fav_banco", ""), 3)
        record += pad_numeric(transaction.get("fav_agencia", ""), 5)
        record += pad_alfa(transaction.get("fav_agencia_dv", ""), 1)
        record += pad_numeric(transaction.get("fav_conta", ""), 12)
        record += pad_alfa(transaction.get("fav_conta_dv", ""), 1)
        record += " "
        record += pad_alfa(transaction.get("fav_nome", ""), 30)
    else:
        record += "000"
        record += "00000"
        record += " "
        record += "0" * 12
        record += " "
        record += " " * 30
        record += " "
    record += pad_alfa(transaction.get("doc_empresa", ""), 20)  # (74-93)
    date_str = transaction["data_pagamento"].strftime("%d%m%Y")  # (94-101)
    record += date_str
    record += pad_alfa("BRL", 3)                              # (102-104)
    record += pad_numeric("0", 15)                            # (105-119)
    try:
        valor = float(transaction["valor_pagamento"].replace(",", "."))
    except:
        valor = 0.0
    valor_int = int(round(valor * 100))
    record += pad_numeric(valor_int, 15)                      # (120-134)
    record += " " * 20                                        # Número do documento atribuído pelo banco (135-154)
    record += " " * 8                                         # Data real da efetivação (155-162)
    record += " " * 15                                        # Valor real da efetivação (163-177)
    record += " " * 22                                        # Campo em branco (178-199)
    record += pad_numeric("01", 2)                            # Tipo de conta – default "01" (200-201)
    record += " " * 18                                        # Campo em branco (202-219)
    record += pad_numeric("00010", 5)                         # Código finalidade – default "00010" (220-224)
    record += " " * 6                                         # Campo em branco (225-230)
    record += " " * 10                                        # Ocorrências para retorno (231-240)
    return record.ljust(240)

def build_segmento_b_pix(transaction, seq):
    record = ""
    record += pad_numeric("077", 3)                           
    record += pad_numeric("1", 4)                             
    record += "3"                                             
    record += pad_numeric(seq, 5)                             
    record += "B"                                             
    record += pad_alfa(transaction["forma_iniciacao"], 3)     
    record += pad_numeric(transaction["tipo_doc_fav"], 1)       
    record += pad_numeric(transaction["doc_fav"], 14)         
    record += pad_alfa(transaction["txid"], 35)               
    record += " " * 60                                        
    if transaction["forma_iniciacao"] in ["01", "02", "04"]:
        record += pad_alfa(transaction["chave_pix"], 99)      
    else:
        record += " " * 99                                    
    record += " " * 6                                         
    if transaction["fav_ispb"]:
        record += pad_numeric(transaction["fav_ispb"], 8)     
    else:
        record += pad_numeric("0", 8)
    return record.ljust(240)

def build_trailer_lote(n_transacoes, total_valor):
    record = ""
    record += pad_numeric("077", 3)
    record += pad_numeric("1", 4)
    record += "5"
    record += " " * 9
    registros_lote = 2 * n_transacoes + 2
    record += pad_numeric(registros_lote, 6)
    total_cents = int(round(total_valor * 100))
    record += pad_numeric(total_cents, 18)
    record += pad_numeric("0", 18)
    record += " " * 6
    record += " " * 165
    record += " " * 10
    return record.ljust(240)

def build_trailer_arquivo(total_lotes, total_registros):
    record = ""
    record += pad_numeric("077", 3)
    record += pad_numeric("9999", 4)
    record += "9"
    record += " " * 9
    record += pad_numeric(total_lotes, 6)
    record += pad_numeric(total_registros, 6)
    record += " " * (240 - (3+4+1+9+6+6))
    return record.ljust(240)

def generate_cnab_file(company, transactions):
    lines = []
    header_arquivo = build_header_arquivo(company)
    lines.append(header_arquivo)
    header_lote = build_header_lote_pix(company)
    lines.append(header_lote)
    seq = 1
    total_valor = 0.0
    for t in transactions:
        seg_a = build_segmento_a_pix(t, seq)
        lines.append(seg_a)
        seq += 1
        seg_b = build_segmento_b_pix(t, seq)
        lines.append(seg_b)
        seq += 1
        try:
            valor = float(t["valor_pagamento"].replace(",", "."))
        except:
            valor = 0.0
        total_valor += valor
    trailer_lote = build_trailer_lote(len(transactions), total_valor)
    lines.append(trailer_lote)
    total_registros = 1 + 1 + (2 * len(transactions)) + 1 + 1
    trailer_arquivo = build_trailer_arquivo(1, total_registros)
    lines.append(trailer_arquivo)
    return "\n".join(lines)

# ====================== FUNÇÃO PARA IMPORTAR E PARSER O ARQUIVO RETORNO (.RET) ======================
def parse_ret_file(text):
    # Garante que cada linha tenha 240 caracteres
    lines = [line if len(line) >= 240 else line.ljust(240) for line in text.splitlines() if line.strip()]
    registros = []
    for line in lines:
        tipo_registro = line[7:8]
        # Processa apenas registros de detalhe (tipo "3") e, dentro destes, apenas os Segmento A
        if tipo_registro == "3":
            segmento = line[13:14]
            if segmento == "A":
                reg = {}
                reg["Código Banco"] = line[0:3].strip()
                reg["Lote"] = line[3:7].strip()
                reg["Tipo Registro"] = line[7:8].strip()
                reg["Segmento"] = segmento
                reg["Tipo Movimento"] = line[14:15].strip()
                reg["Instrução Movimento"] = line[15:17].strip()
                reg["Câmara Centralizadora"] = line[17:20].strip()
                reg["Doc Empresa"] = line[73:93].strip()        # (pos. 74-93)
                reg["Data Pagamento"] = line[93:101].strip()      # (pos. 94-101)
                reg["Moeda"] = line[101:104].strip()              # (pos. 102-104)
                reg["Qtde Moeda"] = line[104:119].strip()         # (pos. 105-119)
                nominal_str = line[119:134].strip()              # (pos. 120-134)
                try:
                    nominal_val = int(nominal_str)
                except:
                    nominal_val = 0
                reg["Valor Nominal (R$)"] = nominal_val / 100.0
                reg["Doc Banco"] = line[134:154].strip()          # (pos. 135-154)
                reg["Data Efetivação"] = line[154:162].strip()      # (pos. 155-162)
                efetivo_str = line[162:177].strip()               # (pos. 163-177)
                try:
                    efetivo_val = int(efetivo_str)
                except:
                    efetivo_val = 0
                reg["Valor Efetivo (R$)"] = efetivo_val / 100.0
                # Campo em branco (pos. 178-199) ignorado
                reg["Tipo de Conta"] = line[199:201].strip()       # (pos. 200-201)
                # Campo em branco (202-219) ignorado
                reg["Código Finalidade"] = line[219:224].strip()   # (pos. 220-224)
                # Campo em branco (225-230) ignorado
                reg["Ocorrência"] = line[230:240].strip()          # (pos. 231-240)
                # Define Status com base na Data Efetivação (se diferente de "00000000")
                if reg["Data Efetivação"] and reg["Data Efetivação"] != "00000000":
                    reg["Status"] = "Pago"
                else:
                    reg["Status"] = "Não Pago"
                registros.append(reg)
    return registros

# ====================== INTERFACE STREAMLIT ======================
menu = st.sidebar.radio("Selecione a funcionalidade", ["Gerar Remessa", "Importar Retorno"])

if menu == "Gerar Remessa":
    st.title("Gerador de Arquivo CNAB240 - Pagamentos via PIX")
    st.markdown("Preencha os dados da empresa:")
    with st.form("company_info"):
        cnpj = st.text_input("CNPJ (somente números, 14 dígitos)")
        agencia = st.text_input("Agência (5 dígitos)", value="00001")
        agencia_dv = st.text_input("Dígito da Agência (1 dígito)", value="9")
        conta = st.text_input("Conta Corrente (12 dígitos)")
        conta_dv = st.text_input("Dígito da Conta (1 dígito)")
        nome_empresa = st.text_input("Nome da Empresa (até 30 caracteres)")
        rua = st.text_input("Nome da Rua/Av")
        numero = st.text_input("Número do Local (até 5 dígitos)")
        complemento = st.text_input("Complemento (até 15 caracteres)")
        cidade = st.text_input("Cidade (até 20 caracteres)")
        cep = st.text_input("CEP (somente números, 5 dígitos)")
        estado = st.text_input("Estado (2 letras)")
        generica = st.text_input("Informação Genérica Opcional (até 40 caracteres)", value="")
        sequencial = st.text_input("Número Sequencial do Arquivo (4 dígitos)", value="0001")
        submitted_company = st.form_submit_button("Salvar Dados da Empresa")
        if submitted_company:
            st.session_state.company = {
                "cnpj": cnpj,
                "agencia": agencia,
                "agencia_dv": agencia_dv,
                "conta": conta,
                "conta_dv": conta_dv,
                "nome_empresa": nome_empresa,
                "rua": rua,
                "numero": numero,
                "complemento": complemento,
                "cidade": cidade,
                "cep": cep,
                "estado": estado,
                "generica": generica,
                "sequencial": sequencial
            }
            st.success("Dados da empresa salvos!")
    
    if "transactions" not in st.session_state:
        st.session_state.transactions = []
    
    st.markdown("### Adicionar Transação PIX")
    with st.form("transaction_form"):
        data_pagamento = st.date_input("Data do Pagamento")
        valor_pagamento = st.text_input("Valor do Pagamento (ex.: 1234,56)")
        doc_empresa = st.text_input("Número do Documento atribuído para a empresa (opcional)")
        forma_iniciacao = st.selectbox("Forma de Iniciação (tipo de chave)", 
                                       options=["01 - Telefone", "02 - Email", "03 - CPF/CNPJ", "04 - Chave Aleatória", "05 - Dados Bancários"])
        if forma_iniciacao.startswith("05"):
            fav_banco = st.text_input("Banco do Favorecido (3 dígitos)")
            fav_agencia = st.text_input("Agência do Favorecido (5 dígitos)")
            fav_agencia_dv = st.text_input("Dígito da Agência do Favorecido (1 dígito)")
            fav_conta = st.text_input("Conta do Favorecido (12 dígitos)")
            fav_conta_dv = st.text_input("Dígito da Conta do Favorecido (1 dígito)")
            fav_nome = st.text_input("Nome do Favorecido (até 30 caracteres)")
        else:
            fav_banco = ""
            fav_agencia = ""
            fav_agencia_dv = ""
            fav_conta = ""
            fav_conta_dv = ""
            fav_nome = ""
        tipo_doc_fav = st.selectbox("Tipo de documento do Favorecido", options=["1 - CPF", "2 - CNPJ"])
        doc_fav = st.text_input("CPF/CNPJ do Favorecido (somente números)")
        txid = st.text_input("TX ID (opcional)")
        chave_pix = st.text_input("Chave PIX (se aplicável para tipos 01, 02 ou 04)")
        fav_ispb = st.text_input("Código ISPB do Favorecido (8 dígitos, opcional)", value="")
        submitted_trans = st.form_submit_button("Adicionar Transação")
        if submitted_trans:
            st.session_state.transactions.append({
                "data_pagamento": data_pagamento,
                "valor_pagamento": valor_pagamento,
                "doc_empresa": doc_empresa,
                "forma_iniciacao": forma_iniciacao.split(" - ")[0],
                "fav_banco": fav_banco,
                "fav_agencia": fav_agencia,
                "fav_agencia_dv": fav_agencia_dv,
                "fav_conta": fav_conta,
                "fav_conta_dv": fav_conta_dv,
                "fav_nome": fav_nome,
                "tipo_doc_fav": tipo_doc_fav.split(" - ")[0],
                "doc_fav": doc_fav,
                "txid": txid,
                "chave_pix": chave_pix,
                "fav_ispb": fav_ispb
            })
            st.success("Transação adicionada!")
    
    if st.session_state.get("transactions"):
        st.markdown("### Transações Adicionadas")
        for i, trans in enumerate(st.session_state.transactions):
            st.write(f"Transação {i+1}: Data: {trans['data_pagamento']}, Valor: {trans['valor_pagamento']}, Forma: {trans['forma_iniciacao']}")
            
        if st.button("Gerar Arquivo .REM"):
            if "company" not in st.session_state:
                st.error("Por favor, preencha os dados da empresa primeiro.")
            else:
                arquivo = generate_cnab_file(st.session_state.company, st.session_state.transactions)
                file_name = f"CI240_001_{pad_numeric(st.session_state.company['sequencial'], 4)}.rem"
                st.download_button("Download do Arquivo .REM", data=arquivo, file_name=file_name, mime="text/plain")

elif menu == "Importar Retorno":
    st.title("Importar Arquivo Retorno (.RET)")
    uploaded_file = st.file_uploader("Escolha o arquivo .RET", type=["ret"])
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = file_bytes.decode("latin1")
        registros = parse_ret_file(text)
        if registros:
            df = pd.DataFrame(registros)
            st.dataframe(df)
        else:
            st.warning("Nenhum registro detalhado (Segmento A) encontrado no arquivo.")
